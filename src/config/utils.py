import os
import tomllib
from enum import Enum
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class Environments(str, Enum):
    production = "production"
    local = "local"


def get_current_version():
    path = get_project_root() / "pyproject.toml"
    with open(path, "rb") as f:
        pyproject = tomllib.load(f)
        return pyproject["tool"]["poetry"]["version"]


def get_db_uri(
    env_name="DB_URI", default="sqlite:///db.sqlite", db_uri: str | None = None
):
    if db_uri is None:
        db_uri = os.environ.get(env_name, default)
    db_uri = db_uri.replace("mysql://", "mysql+pymysql://")

    if db_uri.startswith("mysql+pymysql://") and "charset=" not in db_uri:
        db_uri += ("?" if "?" not in db_uri else "&") + "charset=utf8mb4"
    return db_uri
