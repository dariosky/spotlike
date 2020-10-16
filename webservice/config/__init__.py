import json
import os


def get_config(environment):
    webservice_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     os.pardir,
                     os.pardir))
    config_path = f"{webservice_path}/spotlike.cfg.{environment.lower()}.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    assert "SECRET_KEY" in config
    return config
