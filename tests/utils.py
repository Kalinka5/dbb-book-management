from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers(client: TestClient) -> dict:
    """Get authentication headers by logging in with test user credentials"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.json()}")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
