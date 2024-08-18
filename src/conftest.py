import os

import pytest
from sqlmodel import Session, SQLModel
from starlette.testclient import TestClient


def get_test_db_engine(**kwargs):
    from db.main import get_db_engine

    engine = get_db_engine(db_uri="sqlite://")  # in-memory
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True, scope="session")
def anyio_backend():  # pragma: no cover
    return "asyncio"


@pytest.fixture(autouse=True, scope="session")
def session_secret():
    os.environ["SESSION_SECRET_KEY"] = "TEST_SESSION_SECRET"


@pytest.fixture(autouse=True)
def mocked_db_connection(mocker):
    return mocker.patch("db.main.get_db_engine", side_effect=get_test_db_engine)


@pytest.fixture(name="db_session", scope="session")
def session_fixture():
    engine = get_test_db_engine()
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(name="client", scope="session")
async def test_app_fixture(db_session):
    from db.main import get_session
    from app import make_app

    def get_session_override():
        return db_session

    app = make_app()
    app.dependency_overrides[get_session] = get_session_override
    await app.router.startup()
    client = TestClient(app)
    client.db_session = db_session

    yield client

    await app.router.shutdown()
    app.dependency_overrides.clear()
