from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.database import get_db
from app.main import app
from .utils import get_auth_headers

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_book(client):
    headers = get_auth_headers(client)

    # Send author
    author_data = {
        "name": "Test Author 2",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    assert author_response.status_code == 200
    author_id = author_response.json()["id"]

    # Create a book
    book_data = {
        "title": "Test Book",
        "isbn": 9786177171804,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    response = client.post("/books/", json=book_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"
    assert response.json()["isbn"] == 9786177171804


def test_create_book_invalid_isbn(client):
    headers = get_auth_headers(client)
    book_data = {
        "title": "Test Book",
        "isbn": 123,  # Invalid ISBN (not 13 digits)
        "publish_date": str(date(2020, 1, 1)),
        "author_id": 1,
        "genre_ids": [1],
        "publisher_id": 1
    }
    response = client.post("/books/", json=book_data, headers=headers)
    assert response.status_code == 422  # Validation error


def test_get_books(client):
    headers = get_auth_headers(client)
    # Use the test author created in setup_test_data
    author_id = 1  # First author in test database

    # Create multiple books
    books_data = [
        {
            "title": f"Test Book {i}",
            "isbn": int(f"978617717180{i}"),
            "publish_date": str(date(2020, 1, 1)),
            "author_id": author_id,
            "genre_ids": [1],
            "publisher_id": 1
        } for i in range(3)
    ]

    for book in books_data:
        client.post("/books/", json=book, headers=headers)

    # Test pagination and sorting
    response = client.get("/books/?skip=0&limit=2&sort_by=title")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_book_history(client):
    headers = get_auth_headers(client)
    # Create test book
    author_data = {
        "name": "History Author",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "History Test Book",
        "isbn": 9786177171899,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    book_response = client.post("/books/", json=book_data, headers=headers)
    book_id = book_response.json()["id"]

    # Get book history
    response = client.get(f"/books/{book_id}/history", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_book_future_date(client):
    headers = get_auth_headers(client)
    book_data = {
        "title": "Future Book 4",
        "isbn": 9786177171844,
        "publish_date": str(date(2026, 1, 1)),
        "author_id": 1,
        "genre_ids": [1],
        "publisher_id": 1
    }
    response = client.post("/books/", json=book_data, headers=headers)
    assert response.status_code == 422
