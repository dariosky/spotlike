from config.utils import get_current_version, Environments, get_project_root, get_db_uri


class BaseConfig:
    version = get_current_version()
    name = "Environment name"
    debug = False
    project_root = get_project_root()
    db_uri = get_db_uri("DB_URI")


class Production(BaseConfig):
    env = Environments.production


class Local(BaseConfig):
    env = Environments.local
    debug = True
