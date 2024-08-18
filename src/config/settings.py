import os

from config.utils import get_current_version, Environments, get_project_root, get_db_uri


class BaseConfig:
    version = get_current_version()
    name = "Environment name"
    debug = False
    project_root = get_project_root()
    hostname = "https://spotlike.dariosky.it/"

    db_uri = get_db_uri("DB_URI")
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    session_secret = os.environ["SESSION_SECRET_KEY"]


class Production(BaseConfig):
    env = Environments.production


class Local(BaseConfig):
    env = Environments.local
    debug = True
    hostname = "http://localhost:8000"
