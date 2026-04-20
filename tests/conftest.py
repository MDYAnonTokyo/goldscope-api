from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from goldscope.core.config import get_settings
from goldscope.db.bootstrap import bootstrap_database
from goldscope.db.session import create_engine_for_url


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "test_goldscope.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-1234567890")
    monkeypatch.setenv("ENVIRONMENT", "test")

    get_settings.cache_clear()
    create_engine_for_url.cache_clear()

    from goldscope.main import app

    bootstrap_database()
    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()
    create_engine_for_url.cache_clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    register_payload = {"email": "student@example.com", "password": "supersecure123"}
    client.post("/auth/register", json=register_payload)
    response = client.post("/auth/login", json=register_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
