import logging
import os

from spottools import SpotUserActions
from store import User, initdb
from webservice.config import get_config

logger = logging.getLogger('spotlike.cron')


def run_all_jobs():
    environment = os.environ.get('ENV', 'dev')
    config = get_config(environment)
    for envfield in ('SPOTIPY_CLIENT_SECRET', 'SPOTIPY_CLIENT_ID'):
        # pass some config to the env - for spotipy
        if envfield in config:
            os.environ[envfield] = config[envfield]

    initdb()
    for user in User.select():
        logger.debug(f"Processing {user}")
        act = SpotUserActions(user)
        # act.auto_like_recurrent()
        act.remove_liked_duplicates()
        act.sync_liked_with_playlist(name='Liked playlist')
        act.collect_recent()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    logging.getLogger('spotlike').setLevel(logging.DEBUG)

    run_all_jobs()
