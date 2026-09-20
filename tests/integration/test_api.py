from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_token_endpoint_rejects_bad_client(client: TestClient) -> None:
    response = client.post(
        "/oauth/token",
        auth=("test-client", "wrong"),
        data={"grant_type": "client_credentials"},
    )
    assert response.status_code == 401


def test_health_requires_health_scope(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 401

    token_response = client.post(
        "/oauth/token",
        auth=("test-client", "test-client-secret"),
        data={"grant_type": "client_credentials", "scope": "chat:use"},
    )
    response = client.get(
        "/health", headers=_bearer(str(token_response.json()["access_token"]))
    )
    assert response.status_code == 403


def test_document_and_chat_flow(
    client: TestClient,
    token: str,
) -> None:
    created = client.post(
        "/documents",
        headers=_bearer(token),
        json={"title": "森林防火", "content": "严禁携带火种进入林区。"},
    )
    assert created.status_code == 201

    with patch("app.main.call_glm", return_value="进入林区不得携带火种。"):
        response = client.post(
            "/chat",
            headers=_bearer(token),
            json={"query": "森林防火有哪些要求"},
        )
    assert response.status_code == 200
    assert response.json()["answer"] == "进入林区不得携带火种。"
    assert response.json()["sources"][0]["title"] == "森林防火"


def test_chat_rejects_blank_query(client: TestClient, token: str) -> None:
    response = client.post("/chat", headers=_bearer(token), json={"query": "   "})
    assert response.status_code == 422


def test_enterprise_is_explicitly_unimplemented(
    client: TestClient,
    token: str,
) -> None:
    response = client.post(
        "/enterprise/wecom", headers=_bearer(token), json={"event": "ping"}
    )
    assert response.status_code == 501
