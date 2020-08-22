import click
import spotipy
from cachetools.func import ttl_cache

# will get credentials and save them locally
redirect_uri = 'http://localhost:3000'
scope = ",".join(
    ("user-library-read", 'playlist-read-private',
     "playlist-modify-public", "playlist-modify-private")
)
spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=scope, cache_path='.tokens',
                                                            redirect_uri=redirect_uri))


def get_spotify_list(results):
    while True:
        for item in results['items']:
            yield item
        if results['next']:
            results = spotify.next(results)
        else:
            break


@ttl_cache(ttl=1 * 60)  # cached for a minute
def get_all_playlists():
    """ Return all the playlists of the user """
    return [
        p
        for p in get_spotify_list(
            spotify.current_user_playlists()
        )
    ]


def get_or_create_playlist(name):
    playlists = get_all_playlists()
    same_name_playlists = list(filter(lambda p: p['name'] == name, playlists))
    if not same_name_playlists:
        click.echo(f"Creating a new playlist {name}")
        playlist = spotify.user_playlist_create(spotify.current_user()['id'],
                                                description="All the song you like - synced by Spotlike",
                                                name=name, public=False)
    else:
        if len(same_name_playlists) > 1:
            click.echo(f"Warning: We have multiple playlist with the name {name}", color='green')
        playlist = same_name_playlists[0]  # getting the first

    print(playlist)


def sync_liked_with_playlist(name):
    playlist = get_or_create_playlist(name)


def liked_songs():
    yield from get_spotify_list(
        spotify.current_user_saved_tracks()
    )
