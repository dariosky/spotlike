import json
import os


def get_config(environment):
    webservice_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
    config_path = f"{webservice_path}/spotlike.cfg.{environment.lower()}.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    assert "SECRET_KEY" in config
    return config


def activate_config(config=None):
    if config is None:
        environment = os.environ.get("ENV", "dev")
        config = get_config(environment)
    for envfield in ("SPOTIPY_CLIENT_SECRET", "SPOTIPY_CLIENT_ID"):
        # pass some config to the env - for spotipy
        if envfield in config:
            os.environ[envfield] = config[envfield]
