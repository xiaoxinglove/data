from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

SECRET = "test-jwt-secret-that-is-at-least-32-bytes"
OTHER_SECRET = "another-jwt-secret-that-is-32-bytes-long"
ISSUER = "forestry-mvp"
AUDIENCE = "forestry-api"
CLIENT = ("test-client", "test-client-secret")


def _token(secret: str = SECRET, **claims: object) -> str:
    now = datetime.now(UTC)
    payload: dict[str, object] = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "test-client",
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "scope": "health:read",
    }
    payload.update(claims)
    return jwt.encode(payload, secret, algorithm="HS256")


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_valid_token_is_accepted(client: TestClient) -> None:
    assert client.get("/health", headers=_auth(_token())).status_code == 200


def test_expired_token_is_rejected(client: TestClient) -> None:
    expired = _token(exp=datetime.now(UTC) - timedelta(minutes=1))
    assert client.get("/health", headers=_auth(expired)).status_code == 401


def test_token_from_unknown_issuer_is_rejected(client: TestClient) -> None:
    token = _token(iss="someone-else")
    assert client.get("/health", headers=_auth(token)).status_code == 401


def test_token_for_other_audience_is_rejected(client: TestClient) -> None:
    token = _token(aud="other-api")
    assert client.get("/health", headers=_auth(token)).status_code == 401


def test_token_signed_with_other_secret_is_rejected(client: TestClient) -> None:
    token = _token(secret=OTHER_SECRET)
    assert client.get("/health", headers=_auth(token)).status_code == 401


def test_malformed_token_is_rejected(client: TestClient) -> None:
    assert client.get("/health", headers=_auth("not-a-jwt")).status_code == 401


def test_token_without_required_scope_is_forbidden(client: TestClient) -> None:
    token = _token(scope="documents:write")
    assert client.get("/health", headers=_auth(token)).status_code == 403


def test_token_endpoint_rejects_unsupported_grant(client: TestClient) -> None:
    response = client.post(
        "/oauth/token", auth=CLIENT, data={"grant_type": "password"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_grant_type"


def test_token_endpoint_rejects_unknown_scope(client: TestClient) -> None:
    response = client.post(
        "/oauth/token",
        auth=CLIENT,
        data={"grant_type": "client_credentials", "scope": "admin:all"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid_scope"


def test_token_endpoint_unavailable_when_unconfigured(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OAUTH_JWT_SECRET", raising=False)
    response = client.post(
        "/oauth/token", auth=CLIENT, data={"grant_type": "client_credentials"}
    )
    assert response.status_code == 503


def test_resource_unavailable_when_unconfigured(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OAUTH_JWT_SECRET", "too-short")
    assert client.get("/health", headers=_auth(_token())).status_code == 503
