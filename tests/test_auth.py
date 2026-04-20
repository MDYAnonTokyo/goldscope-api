from fastapi.testclient import TestClient


def test_register_and_login_success(client: TestClient) -> None:
    register_response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "strongpass123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"

    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "strongpass123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"


def test_duplicate_registration_returns_409(client: TestClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "strongpass123"}
    client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)
    assert second_response.status_code == 409


def test_invalid_login_returns_401(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "auth@example.com", "password": "strongpass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "auth@example.com", "password": "wrongpass123"},
    )
    assert login_response.status_code == 401
