import os

import click
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:3000'


@click.group()
def cli():
    """ Songlike - a bot to ameliorate your Spotify experience """
    click.echo("Test")
    if False:
        birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

        results = spotify.artist_albums(birdy_uri, album_type='album')
        albums = results['items']
        while results['next']:
            results = spotify.next(results)
            albums.extend(results['items'])

        for album in albums:
            click.echo(album['name'])


@cli.command()
def auth():
    """Ask for user credentials"""
    # get credentials and save them locally
    click.echo("Getting user credentials, a browser window will open")
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path='.tokens'))

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])


if __name__ == '__main__':
    auth()
