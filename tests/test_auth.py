from fastapi.testclient import TestClient
from app.main import app


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "newuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_login(client):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code == 401
