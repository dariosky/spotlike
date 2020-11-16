import datetime
import logging
from collections import defaultdict
from functools import partial
from typing import Dict

import click
import peewee
import spotipy

# will get credentials and save them locally
from store import (User, initdb, Message, Track,
                   Artist, TrackArtist, Album, Liked, Play, AlbumArtist, db)

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
            return self.token_info
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
        self.user.insert_or_update(
            tokens=token_info
        )


def get_auth_manager(user=None, redirect_uri='http://localhost:3000'):
    return StoredSpotifyOauth(scope=scope,
                              user=user,
                              redirect_uri=redirect_uri,
                              # show_dialog=True,
                              )


ALLOWED_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%dT%H:%M:%SZ',
    "%Y-%m-%dT%H:%M:%S.%fZ",
    '%Y-%m-%d',
    '%Y-%m-%d %H:%M',
    '%Y-%m',
)


def parse_date(date_str):
    if isinstance(date_str, str):
        if len(date_str) == 4:
            date_str += "-01-01"  # %Y, let's add Jan01
        elif len(date_str) == 7:
            date_str += "-01"  # %Y-%M, let's add the day to be able to parse
        date_str = date_str.strip()
        for date_fmt in ALLOWED_DATETIME_FORMATS:
            try:
                return datetime.datetime.strptime(date_str, date_fmt)
            except ValueError:
                pass
        raise ValueError(
            f"Invalid date: '{date_str}', please pass a datetime or a string format"
        )
    return date_str


def store_track(track):
    artists = []
    for artist in track.get('artists', []):
        a = Artist().insert_or_update(
            id=artist['id'],
            name=artist['name'],
        )
        artists.append(a)

    if track.get('album'):
        album = Album().insert_or_update(
            id=track['album']['id'],
            name=track['album']['name'],
            release_date=parse_date(track['album']['release_date']),
            release_date_precision=track['album']['release_date_precision'],
            picture=track['album']['images'][0] if track['album']['images'] else None,
        )
        for artist in track['album'].get('artists', []):
            a = Artist().insert_or_update(
                id=artist['id'],
                name=artist['name'],
            )
            AlbumArtist().insert_or_update(album=album, artist=a)
    else:
        album = None

    t = Track().insert_or_update(
        id=track['id'],
        duration=track['duration_ms'],
        title=track['name'],
        album=album,
    )
    for a in artists:
        TrackArtist().insert_or_update(track=t, artist=a)
    return t


class SpotUserActions:
    def __init__(self, user=None,
                 auth_manager=None,
                 connect=True,
                 redirect_uri='http://localhost:3000'):
        initdb()
        # we use a custom client_credentials_manager that writes in the DB
        self.auth_manager = auth_manager or get_auth_manager(user, redirect_uri=redirect_uri)

        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

        if connect:
            spotify_user = self.spotify.current_user()

            # we are initialized - let's save the user
            self.user = User(id=spotify_user['id']) \
                .insert_or_update(**dict(name=spotify_user['display_name'],
                                         email=spotify_user['email'],
                                         picture=spotify_user['images'][0]['url'] if spotify_user['images'] else None,
                                         tokens=self.auth_manager.token_info,
                                         ))

            if user is None:
                # we didn't have the user - so we save the tokens now
                self.auth_manager.user = self.user
            if getattr(self, '_new', False):
                self.msg("Sign up successful", msg_type='signup')

    def get_spotify_list(self, results):
        """ A generic method to consume the Spotify API paginated results """
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

    def filter_own_playlists(self, playlists):
        for playlist in playlists:
            if playlist['owner']['id'] == self.user.id:  # get only the one owned by the user
                yield playlist

    def get_or_create_playlist(self, name):
        playlists = self.filter_own_playlists(self.get_all_playlists())

        same_name_playlists = list(filter(lambda p: p['name'] == name, playlists))
        if not same_name_playlists:
            self.msg(f"Creating a new playlist: {name}", msg_type='playlist-create')
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

        if to_add or to_del:
            msg = filter(lambda x: x is not None, [
                f"Added {len(to_add)}" if to_add else None,
                f"Removed {len(to_del)}" if to_del else None,
            ])
            self.msg(" / ".join(msg) + " songs", msg_type='synclike')

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
        messages = []
        for key, versions in track_versions.items():
            if len(versions) > 1:
                duplicates = versions[:-1]  # all but the last
                messages.append(
                    f"Found a duplicate for {key} - removing {len(duplicates)}"
                    f" - liked on {[date for dup_id, date in versions]}")
                to_unlike |= set(dup_id for dup_id, date in duplicates)
        if messages:
            self.msg("\n".join(messages), msg_type='duplicate')
        if to_unlike:
            logger.debug(f"Unlike {len(to_unlike)} songs")
            for tracks in reverse_block_chunks(list(to_unlike), 100):
                self.spotify.current_user_saved_tracks_delete(
                    tracks=tracks,
                )

    def recently_played(self, after=None):
        for played in self.get_spotify_list(self.spotify.current_user_recently_played()):
            yield played

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

    def msg(self, message, msg_type=None):
        click.echo(message)
        message = Message(
            user=self.user,
            message=message,
            msg_type=msg_type,
        )
        message.save()

    def collect_likes(self):
        added = 0
        with db.atomic():
            for liked in self.liked_songs():
                track = store_track(liked['track'])
                try:
                    l = Liked(track=track, user=self.user,
                              date=parse_date(liked['added_at']))
                    l.save(force_insert=True)
                    added += 1
                except peewee.IntegrityError:
                    break
        if added:
            logger.debug(f"Added {added} likes")

    def collect_recent(self):
        added = 0
        with db.atomic():
            for played in self.recently_played():
                track = store_track(played['track'])

                try:
                    Play(track=track, user=self.user,
                         date=parse_date(played['played_at'])).save(force_insert=True)
                    added += 1
                except peewee.IntegrityError:
                    break
        if added:
            logger.debug(f"Added {added} recent")


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
