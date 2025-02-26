from fastapi.testclient import TestClient
from datetime import date
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import pytest

from app.database import Base, get_db
from app.main import app
from app import models
from app.auth.utils import get_password_hash
from app.auth.models import User

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False
    )
    session = TestingSessionLocal()

    # Start with clean tables for each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_data(db_session):
    # Create test author
    author = models.Author(
        name="Test Author",
        birthdate=date(1990, 1, 1)
    )
    db_session.add(author)

    # Create test genre
    genre = models.Genre(name="Test Genre")
    db_session.add(genre)

    # Create test publisher
    publisher = models.Publisher(
        name="Test Publisher",
        established_year=2000
    )
    db_session.add(publisher)

    db_session.commit()
    return {"author": author, "genre": genre, "publisher": publisher}


@pytest.fixture(scope="function")
def client(db_session, test_user, test_data):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
