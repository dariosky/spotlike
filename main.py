import click

from spottools import SpotUserActions


@click.group()
def cli():
    """ Spotlike - a bot to ameliorate your Spotify experience """


@cli.command()
@click.option('--name', help="Liked playlist name", default='Liked playlist')
@click.option('--fast', help="Perform a fast sync", default=False)
def sync(name, fast):
    """ Syncronize all your liked songs with a playlist - so you can share them with others """
    click.echo(f"Syncing the liked songs with '{name}'")
    act = SpotUserActions()
    act.sync_liked_with_playlist(name, full=not fast)


if __name__ == '__main__':
    sync()
