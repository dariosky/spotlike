import contextlib
import logging
import os
from functools import lru_cache
from urllib.parse import urlparse, quote_plus

from sqlalchemy import QueuePool
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session

from config import settings


logger = logging.getLogger(__file__)


@contextlib.contextmanager
def db_session_context(db_session: Session = None, session_getter=None):
    keep_session = True
    try:
        if db_session is None:
            db_session = next((session_getter or get_session)())
            keep_session = False
        yield db_session
    finally:
        if keep_session is False:
            db_session.close()


@lru_cache(maxsize=10)
def get_db_engine(*, db_uri=settings.db_uri, db_name=None, host=None, schema=None):
    if db_name or host or schema:
        if "//" in db_uri and "@" in db_uri:  # url-encode the credentials
            # some string magic - to urlparse the DB credentials in the secret
            start = db_uri.find("//")
            end = db_uri.find("@")
            credentials = db_uri[start + 2 : end].split(":")
            db_uri = (
                f'{db_uri[:start]}//'
                f'{":".join(map(quote_plus, credentials))}{db_uri[end:]}'
            )
        parts = urlparse(db_uri)
        if schema:
            parts = parts._replace(scheme=schema)
        if db_name:
            parts = parts._replace(path=f"/{db_name}")
        if host:
            # this is a custom rewrite for when the host contains auth
            if parts.username or parts.password:
                host_without_auth = host.split("@")[-1]
                auth_parts = ":".join(
                    [token for token in (parts.username, parts.password) if token]
                )
                new_netloc = f"{auth_parts}@{host_without_auth}"
            else:
                new_netloc = host
            parts = parts._replace(netloc=new_netloc)
        db_uri = parts.geturl()
    if db_uri.startswith("sqlite:"):
        connect_args = {"check_same_thread": False}
        extra_args = dict(poolclass=StaticPool)
    else:
        connect_args = {}
        extra_args = dict(pool_pre_ping=True, poolclass=QueuePool, pool_recycle=3600)
    engine = create_engine(
        db_uri,
        # echo=settings.debug,
        connect_args=connect_args,
        **extra_args,
    )
    return engine


def update_database():  # pragma: no cover
    """Init the DB or run the Alembic migrations"""
    import alembic.config

    logger.info(f"{settings.title} v{settings.version}")
    if not os.path.isfile("alembic.ini"):
        os.chdir(settings.project_root)
    try:
        alembic.config.main(
            argv=[
                "--raiseerr",
                "upgrade",
                "head",
            ]
        )
    except Exception as e:
        logger.exception(f"Cannot run DB migrations: {e}")


def get_session(params=None):
    engine = get_db_engine(**(params or {}))
    with Session(engine, expire_on_commit=False) as session:
        try:
            yield session
        except Exception as e:
            logger.exception(f"Error in the DB - rolling back: {e}")
            session.rollback()
            raise
