from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from .utils import get_auth_headers

client = TestClient(app)


def test_borrow_book(client):
    headers = get_auth_headers(client)

    # Create test book first
    author_data = {
        "name": "Borrow Author",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "Book to Borrow",
        "isbn": 9786177171807,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    book_response = client.post("/books/", json=book_data, headers=headers)
    book_id = book_response.json()["id"]

    # Borrow the book
    borrow_data = {
        "book_id": book_id,
        "borrower_name": "Test Borrower"
    }
    response = client.post("/borrow", json=borrow_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["book_id"] == book_id
    assert response.json()["borrower_name"] == "Test Borrower"


def test_borrow_unavailable_book(client):
    headers = get_auth_headers(client)
    # Create and borrow a book
    author_data = {
        "name": "Unavailable Author",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "Unavailable Book",
        "isbn": 9786177171808,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    book_response = client.post("/books/", json=book_data, headers=headers)
    book_id = book_response.json()["id"]

    # First borrow
    borrow_data = {
        "book_id": book_id,
        "borrower_name": "First Borrower"
    }
    client.post("/borrow", json=borrow_data, headers=headers)

    # Try to borrow again
    borrow_data["borrower_name"] = "Second Borrower"
    response = client.post("/borrow", json=borrow_data, headers=headers)
    assert response.status_code == 400
    assert "not available" in response.json()["detail"]


def test_return_book(client):
    headers = get_auth_headers(client)
    # Create and borrow a book
    author_data = {
        "name": "Return Author",
        "birthdate": str(date(1990, 1, 1))
    }
    author_response = client.post(
        "/authors/", json=author_data, headers=headers)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "Book to Return",
        "isbn": 9786177171809,
        "publish_date": str(date(2020, 1, 1)),
        "author_id": author_id,
        "genre_ids": [1],
        "publisher_id": 1
    }
    book_response = client.post("/books/", json=book_data, headers=headers)
    book_id = book_response.json()["id"]

    # Borrow the book
    borrow_data = {
        "book_id": book_id,
        "borrower_name": "Return Tester"
    }
    borrow_response = client.post("/borrow", json=borrow_data, headers=headers)
    borrowing_id = borrow_response.json()["id"]

    # Return the book
    response = client.post(f"/return/{borrowing_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["return_date"] is not None
