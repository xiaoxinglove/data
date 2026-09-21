from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def oauth_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OAUTH_CLIENT_ID", "test-client")
    monkeypatch.setenv("OAUTH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("OAUTH_JWT_SECRET", "test-jwt-secret-that-is-at-least-32-bytes")


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    path = tmp_path / "documents.json"
    monkeypatch.setenv("KNOWLEDGE_BASE_PATH", str(path))
    from backend import main
    from backend.store import DocumentStore

    monkeypatch.setattr(main, "store", DocumentStore(path))
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def token(client: TestClient) -> str:
    response = client.post(
        "/oauth/token",
        auth=(os.environ["OAUTH_CLIENT_ID"], os.environ["OAUTH_CLIENT_SECRET"]),
        data={
            "grant_type": "client_credentials",
            "scope": ("health:read chat:use documents:write enterprise:write"),
        },
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])
