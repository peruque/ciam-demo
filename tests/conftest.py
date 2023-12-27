import pytest
from fastapi.testclient import TestClient
from app.main import app
from httpx import Cookies


@pytest.fixture
def cookies() -> dict:
    return {
        "refresh_token": "x",
        "access_token": "y",
    }


@pytest.fixture
def authorized_client(cookies) -> TestClient:
    client = TestClient(app)
    client.cookies = Cookies(cookies=cookies)
    return client
