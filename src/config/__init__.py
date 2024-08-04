import os

from config.settings import Local, Production, BaseConfig
from config.utils import Environments

# this can be a conditional import
configurations: dict[str, type[BaseConfig]] = {
    Environments.local: Local,
    Environments.production: Production,
}

chosen_env = os.environ.get("ENV")
settings = configurations.get(chosen_env, Local)
