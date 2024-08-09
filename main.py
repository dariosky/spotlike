import logging

import click

from spottools import SpotUserActions


@click.group()
def cli():
    """Spotlike - a bot to ameliorate your Spotify experience"""


@cli.command()
@click.option("--name", help="Liked playlist name", default="Liked playlist")
@click.option("--fast", help="Perform a fast sync", default=False, is_flag=True)
def sync(name, fast):
    """Synchronise all your liked songs with a playlist"""
    click.echo(f"Syncing the liked songs with '{name}'")
    act = SpotUserActions()
    act.sync_liked_with_playlist(name, full=not fast)


@cli.command()
def remove_duplicates():
    """Look for duplicate-likes - keep the oldest"""
    click.echo("Looking for duplicates in your liked songs")
    act = SpotUserActions()
    act.remove_liked_duplicates()


@cli.command()
def auto_like_recurrent():
    click.echo("Looking for recurrent songs to like")
    act = SpotUserActions()
    act.auto_like_recurrent()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
    )
    logging.getLogger("spotlike").setLevel(logging.DEBUG)
    cli()
    # remove_duplicates()
    # auto_like_recurrent()
