import datetime
import logging
from collections import defaultdict
from functools import partial
from typing import Dict

import click
import spotipy

# will get credentials and save them locally
from store import User, initdb

scope = ",".join((
    'user-read-email',
    'user-library-read', 'user-library-modify',
    'playlist-read-private',
    'playlist-modify-public', 'playlist-modify-private',
    'user-read-recently-played', 'user-top-read',
))

logger = logging.getLogger('spotlike.spottools')


class StoredSpotifyOauth(spotipy.SpotifyOAuth):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        self.token_info = None

    def get_cached_token(self):
        if not self.user:  # I have no tokens - we'll ask for them
            return None
        token_info = self.user.tokens  # get from DB
        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
            self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(
                token_info["refresh_token"]
            )
        self.token_info = token_info
        return token_info

    def _save_token_info(self, token_info):
        self.token_info = token_info
        if not self.user:
            # logger.warning("Skipping tokens save - without a user")
            return
        self.user.tokens = token_info
        self.user.save()


def get_auth_manager(user=None, redirect_uri='http://localhost:3000'):
    return StoredSpotifyOauth(scope=scope,
                              user=user,
                              redirect_uri=redirect_uri,
                              # show_dialog=True,
                              )


class SpotUserActions:
    def __init__(self, user=None, connect=True, redirect_uri='http://localhost:3000'):
        initdb()
        # we use a custom client_credentials_manager that writes in the DB
        self.auth_manager = auth_manager = get_auth_manager(user, redirect_uri=redirect_uri)

        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

        if connect:
            spotify_user = self.spotify.current_user()

            # we are initialized - let's save the user
            self.user = User(id=spotify_user['id'], name=spotify_user['display_name'],
                             email=spotify_user['email'],
                             picture=spotify_user['images'][0]['url'] if spotify_user['images'] else None,
                             tokens=auth_manager.token_info,
                             )

            if user is None:
                # we didn't have the user - so we save the tokens now
                auth_manager.user = self.user
            self.user.insert_or_update()

    def get_spotify_list(self, results):
        while True:
            for item in results['items']:
                yield item
            if results['next']:
                results = self.spotify.next(results)
            else:
                break

    # @ttl_cache(ttl=1 * 60)  # cached for a minute
    def get_all_playlists(self):
        """ Return all the playlists of the user """
        return [
            p
            for p in self.get_spotify_list(
                self.spotify.current_user_playlists()
            )
        ]

    def get_or_create_playlist(self, name):
        playlists = self.get_all_playlists()
        same_name_playlists = list(filter(lambda p: p['name'] == name, playlists))
        if not same_name_playlists:
            click.echo(f"Creating a new playlist {name}")
            playlist = self.spotify.user_playlist_create(self.spotify.current_user()['id'],
                                                         description="All the song you like - synced by Spotlike",
                                                         name=name, public=False)
        else:
            if len(same_name_playlists) > 1:
                click.echo(f"Warning: We have multiple playlist with the name {name}", color='green')
            playlist = same_name_playlists[0]  # getting the first
        return playlist

    def sync_liked_with_playlist(self, name, full=True):
        """ Here we try to be smart to avoid having to go through all the likes or all the song in the playlist
             when it's not needed.
        """
        playlist = self.get_or_create_playlist(name)
        # we have these two iterators
        playlist_tracks = self.get_spotify_list(self.spotify.playlist_items(playlist['id'],
                                                                            additional_types=('track',)
                                                                            ))
        likes = self.liked_songs()

        to_add, to_del = sync_merge(likes, playlist_tracks, full=full)

        click.echo(f"Adding {len(to_add)} songs / removing {len(to_del)}")

        # we add and remove all the needed tracks
        for all_tracks, method in ((to_add, partial(self.spotify.playlist_add_items, position=0)),
                                   (to_del, self.spotify.playlist_remove_all_occurrences_of_items)):
            # we do our operations in chunks of 100 tracks
            for tracks in reverse_block_chunks(all_tracks, 100):
                method(
                    playlist['id'],
                    tracks,
                )

    def liked_songs(self):
        yield from self.get_spotify_list(
            self.spotify.current_user_saved_tracks(limit=50)
        )

    def remove_liked_duplicates(self):
        track_versions: Dict[str:list] = defaultdict(list)  # track key - list of (track_id, date)
        # we keep the date when a song was liked - so we can show it to the user
        for liked in self.liked_songs():
            track_id = liked['track']['id']
            track_duration = liked['track']['duration_ms']
            track_name = liked['track']['name']

            key = track_name, track_duration
            track_versions[key].append((track_id, liked['added_at']))

        to_unlike = set()
        for key, versions in track_versions.items():
            if len(versions) > 1:
                duplicates = versions[:-1]  # all but the last
                logger.debug(
                    f"Found a duplicate for {key} - removing {len(duplicates)}"
                    f" - liked on {[date for dup_id, date in versions]}")
                to_unlike |= set(dup_id for dup_id, date in duplicates)
        if to_unlike:
            logger.info(f"Unlike {len(to_unlike)} songs")
            for tracks in reverse_block_chunks(list(to_unlike), 100):
                self.spotify.current_user_saved_tracks_delete(
                    tracks=tracks,
                )

    def auto_like_recurrent(self, played_times=5, day_period=30, store=True):
        """ Autolike songs played at least `played_times` times over the `day_period` """
        check_history_from = datetime.datetime.utcnow() - datetime.timedelta(days=day_period)
        as_timestamp = int(check_history_from.timestamp() * 1000)  # in ms
        recently_played: Dict[str, Dict] = {}
        scanned = 0

        # we collect recent tracks in two ways - via the spotify top list - and via the recently played ones
        track_collecting_methods = (
            partial(self.spotify.current_user_top_tracks, time_range='short_term'),
            partial(self.spotify.current_user_recently_played, after=as_timestamp),
        )

        to_like = set()

        for track_collecting_method in track_collecting_methods:
            for played in self.get_spotify_list(track_collecting_method()):
                scanned += 1
                if played.get('type') == 'track':  # this is a top-track we just add it
                    logger.debug(f"Track {played['name']} is a recent top")
                    to_like.add(played['id'])
                else:
                    track_id = played['track']['id']
                    played_at = played['played_at']
                    if track_id not in recently_played:
                        recently_played[track_id] = dict(name=played['track']['name'],
                                                         play_history=set())
                    recently_played[track_id]['play_history'].add(played_at)

        for track_id, desc in recently_played.items():
            if len(desc['play_history']) >= played_times:
                logger.debug("Recently played several", desc)
                to_like.add(track_id)

        logger.debug(f"Scanned {scanned} songs - recurrent {len(to_like)}")


def reverse_block_chunks(l, size):
    """ iterate through the list with a given size so the blocks keep their inner order,
         but we get them from the latest"""
    start, end = len(l) - size, len(l)
    while end > 0:
        yield l[start:end]
        start, end = max(0, start - size), start


def sync_merge_full(likes, playlist_tracks):
    """ A full-sync, iterating all likes and all the playlist_tracks
        There's no way around to avoid a full-iteration sync from now and then
        Because it's possible to unlike old songs - and that leaves no traces
    """
    likes_ids = [t['track']['id'] for t in likes]  # here we care about the order
    playlist_ids = set([t['track']['id'] for t in playlist_tracks])  # we don't care about the order

    to_add = [t for t in likes_ids if t not in playlist_ids]
    to_del = list(playlist_ids - set(likes_ids))
    return to_add, to_del


def sync_merge_fast(likes, playlist_tracks):
    """ A fast-sync - that copies every new likes in the playlist """
    to_add = []
    to_del = []

    in_playlist = next(playlist_tracks, None)
    liked = next(likes, None)

    # so let's do merge-magic
    while True:
        # let's add songs until we find something already synced or we find something sinced before the current like
        if liked and in_playlist and (liked['track']['id'] != in_playlist['track']['id']
                                      and in_playlist['added_at'] <= liked['added_at']):
            to_add.append(liked['track']['id'])
            liked = next(likes, None)
            continue

        if liked and (not in_playlist or liked['track']['id'] != in_playlist['track']['id']):
            # if what we have
            logger.info(f"Adding the non-liked {liked['track']['name']}")
            to_add.append(liked['track']['id'])
            liked = next(likes, None)
            continue
        break

    return to_add, to_del


def sync_merge(likes, playlist_tracks, full=True):
    # ... and in the end that's what we want to know
    if full:
        return sync_merge_full(likes, playlist_tracks)
    else:
        return sync_merge_fast(likes, playlist_tracks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    logging.getLogger('spotlike').setLevel(logging.DEBUG)


    def playground():
        # iterate through all the users and
        for user in User.select():
            act = SpotUserActions(user)
            # act.sync_liked_with_playlist(name='Liked playlist')
            act.auto_like_recurrent()
            # act.remove_liked_duplicates()

        # get a local user
        # act = SpotUserActions()
        # act.sync_liked_with_playlist(name='Liked playlist')


    playground()
