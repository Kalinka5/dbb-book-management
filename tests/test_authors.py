from fastapi.testclient import TestClient

from datetime import date

from app.main import app
from .utils import get_auth_headers

client = TestClient(app)


def test_create_author(client):
    headers = get_auth_headers(client)
    author_data = {
        "name": "New Author",
        "birthdate": str(date(1990, 1, 1))
    }
    response = client.post("/authors/", json=author_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Author"


def test_create_author_future_birthdate(client):
    headers = get_auth_headers(client)
    author_data = {
        "name": "Future Author",
        "birthdate": str(date(2026, 1, 1))
    }
    response = client.post("/authors/", json=author_data, headers=headers)
    assert response.status_code == 422


def test_create_duplicate_author(client):
    headers = get_auth_headers(client)
    author_data = {
        "name": "Duplicate Author",
        "birthdate": str(date(1990, 1, 1))
    }
    # Create first time
    client.post("/authors/", json=author_data, headers=headers)
    # Try to create again
    response = client.post("/authors/", json=author_data, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_author_books(client):
    headers = get_auth_headers(client)
    author_data = {
        "name": "Author With Books",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    author_id = author_response.json()["id"]

    # Create book
    book_data = {
        "title": "Author's Book",
        "isbn": 9786177171806,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    client.post("/books/", json=book_data, headers=headers)

    # Get author's books
    response = client.get(f"/authors/{author_id}/books")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "Author's Book"
