import os

import pytest
from sqlmodel import Session, SQLModel
from starlette.testclient import TestClient

from db.main import get_session, get_db_engine
from app import make_app


def get_test_db_engine(**kwargs):
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


@pytest.fixture(autouse=True)
def referenced_network_names(mocker):
    return mocker.patch(
        "reference_data.get_network_names",
        return_value={"BTC": "Bitcoin", "ETH": "Ethereum"},
    )


@pytest.fixture(autouse=True)
def mock_slack(mocker):
    return mocker.patch(
        "rbl.utils.slack_utils.post_message",
    )


@pytest.fixture(name="db_session", scope="session")
def session_fixture():
    engine = get_test_db_engine()
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(name="client", scope="session")
async def test_app_fixture(db_session):
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
