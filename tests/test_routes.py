from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from bs4 import BeautifulSoup

client = TestClient(app)


def test_login_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    soup = BeautifulSoup(response._content, "html.parser")
    assert soup.find("p").text == "Click button below to login using AWS Cognito."


def test_unauthorized_profile_page():
    response = client.get("/profile")
    assert response.status_code == 422
    error_msg = response.json()["detail"][0]
    assert error_msg["type"] == "missing"
    assert error_msg["loc"] == ["cookie", "access_token"]


def test_invalid_token_profile_page(authorized_client: TestClient):
    response = authorized_client.get("/profile")
    assert response.json()["detail"] == "Invalid token"
