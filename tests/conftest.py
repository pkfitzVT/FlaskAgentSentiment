import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.db_writer import Base  # import Declarative base for tables
from app.web import create_app


@pytest.fixture(scope="session")
def _test_db_url():
    # SQLite in-memory database for the whole test session
    url = "sqlite+pysqlite:///:memory:"
    os.environ["DATABASE_URL"] = url
    return url


@pytest.fixture(scope="session")
def _engine(_test_db_url):
    engine = create_engine(_test_db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(_engine):
    # Override get_session to use the in-memory DB
    from app.agents import db_writer

    db_writer.get_session = lambda: sessionmaker(bind=_engine)()

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
