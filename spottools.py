import logging
from functools import partial

import click
import spotipy

# will get credentials and save them locally
redirect_uri = 'http://localhost:3000'
scope = ",".join(
    ("user-library-read", 'playlist-read-private',
     "playlist-modify-public", "playlist-modify-private")
)

logger = logging.getLogger(__name__)


class SpotUserActions:
    def __init__(self):
        self.spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=scope,
                                                                         cache_path='.tokens',
                                                                         redirect_uri=redirect_uri))

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
        playlist_tracks = self.get_spotify_list(self.spotify.playlist_tracks(playlist['id']))
        likes = self.liked_songs()

        to_add, to_del = sync_merge(likes, playlist_tracks, full=full)

        click.echo(f"Adding {len(to_add)} songs / removing {len(to_del)}")

        # we add and remove all the needed tracks
        for all_tracks, method in ((to_add, partial(self.spotify.user_playlist_add_tracks, position=0)),
                                   (to_del, self.spotify.user_playlist_remove_all_occurrences_of_tracks)):
            # we do our operations in chunks of 100 tracks
            for tracks in reverse_block_chunks(all_tracks, 100):
                method(
                    self.spotify.current_user()['id'], playlist['id'],
                    tracks=tracks,
                )

    def liked_songs(self):
        yield from self.get_spotify_list(
            self.spotify.current_user_saved_tracks()
        )


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
                                      and in_playlist['added_at'] <= liked['added_at']
        ):
            to_add.append(liked['track']['id'])
            liked = next(likes, None)
            continue

        # a condition to exit - is when we find something in_playlist that is older than the current liked song
        if liked and in_playlist and (in_playlist['added_at'] <= liked['added_at']):
            break

        if liked and (not in_playlist or liked['track']['id'] != in_playlist['track']['id']):
            # if what we have
            logger.info(f"Adding the non-liked {liked['track']['name']}")
            to_add.append(liked['track']['id'])
            liked = next(likes, None)
        elif liked and in_playlist and in_playlist['track']['id'] not in to_add:
            # if the song in the PL is newer, we should probably remove it
            logger.info(f"Removing the non-liked {in_playlist['track']['name']}")
            to_del.append(in_playlist['track']['id'])
            in_playlist = next(playlist_tracks, None)

        if not liked and not in_playlist:  # we iterated everything
            break

    return to_add, to_del


def sync_merge(likes, playlist_tracks, full=True):
    # ... and in the end that's what we want to know
    if full:
        return sync_merge_full(likes, playlist_tracks)
    else:
        return sync_merge_fast(likes, playlist_tracks)
