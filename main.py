import click

from spottools import sync_liked_with_playlist


@click.group()
def cli():
    """ Spotlike - a bot to ameliorate your Spotify experience """


@cli.command()
@click.option('--name', help="Liked playlist name", default='Liked playlist')
def sync(name):
    """ Syncronize all your liked songs with a playlist - so you can share them with others """
    click.echo(f"Syncing the liked songs with the '{name}'")
    sync_liked_with_playlist(name)

    # for liked_song in liked_songs():
    #     print(liked_song)


if __name__ == '__main__':
    sync()
