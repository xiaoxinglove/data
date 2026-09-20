from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast

BASE_URL = "http://127.0.0.1:8765"
GLM_URL = "http://127.0.0.1:8766"


class FakeGLMHandler(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        type(self).calls += 1
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        assert payload["model"] == "zai-org/GLM-5.3"
        assert "森林防火" in payload["messages"][1]["content"]
        body = json.dumps(
            {"choices": [{"message": {"content": "进入林区不得携带火种。"}}]}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def request(
    path: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, object]]:
    request_headers = {} if headers is None else headers
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read()
            return response.status, cast(
                dict[str, object], json.loads(body.decode("utf-8"))
            )
    except urllib.error.HTTPError as error:
        return error.code, cast(
            dict[str, object], json.loads(error.read().decode("utf-8"))
        )


def json_request(
    path: str, payload: dict[str, str], token: str
) -> tuple[int, dict[str, object]]:
    return request(
        path,
        method="POST",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )


def get_token() -> str:
    credentials = base64.b64encode(b"test-client:test-client-secret").decode()
    status, body = request(
        "/oauth/token",
        method="POST",
        data=urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "scope": ("health:read chat:use documents:write enterprise:write"),
            }
        ).encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    assert status == 200
    token = body["access_token"]
    assert isinstance(token, str)
    return token


def wait_until_started() -> None:
    for _ in range(50):
        try:
            status, _ = request("/health")
            if status == 401:
                return
        except urllib.error.URLError, ConnectionError:
            time.sleep(0.1)
    raise RuntimeError("服务未在 5 秒内启动")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        FakeGLMHandler.calls = 0
        glm_server = ThreadingHTTPServer(("127.0.0.1", 8766), FakeGLMHandler)
        glm_thread = threading.Thread(target=glm_server.serve_forever, daemon=True)
        glm_thread.start()

        environment = os.environ.copy()
        environment.update(
            {
                "KNOWLEDGE_BASE_PATH": str(Path(directory) / "documents.json"),
                "GLM_API_KEY": "test-key",
                "GLM_BASE_URL": f"{GLM_URL}/v1",
                "GLM_MODEL": "zai-org/GLM-5.3",
                "OAUTH_CLIENT_ID": "test-client",
                "OAUTH_CLIENT_SECRET": "test-client-secret",
                "OAUTH_JWT_SECRET": "test-jwt-secret-that-is-at-least-32-bytes",
            }
        )
        process = subprocess.Popen(
            (
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8765",
            ),
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_until_started()
            token = get_token()
            status, health = request(
                "/health", headers={"Authorization": f"Bearer {token}"}
            )
            assert status == 200 and health == {"status": "healthy"}

            status, created = json_request(
                "/documents",
                {"title": "森林防火", "content": "严禁携带火种进入林区。"},
                token,
            )
            document = created["document"]
            assert status == 201 and isinstance(document, dict)
            assert document["title"] == "森林防火"

            status, matched = json_request(
                "/chat", {"query": "森林防火有哪些要求"}, token
            )
            assert status == 200
            assert matched["answer"] == "进入林区不得携带火种。"
            sources = matched["sources"]
            assert isinstance(sources, list)
            assert sources[0]["title"] == "森林防火"
            assert FakeGLMHandler.calls == 1

            status, answer = json_request("/chat", {"query": "海洋潮汐观测"}, token)
            assert status == 200
            assert answer == {"answer": "未找到相关资料", "sources": []}
            assert FakeGLMHandler.calls == 1

            status, _ = json_request("/enterprise/wecom", {"event": "ping"}, token)
            assert status == 501
        finally:
            process.terminate()
            process.wait(timeout=5)
            glm_server.shutdown()
            glm_server.server_close()
    print("HTTP endpoint check passed")


if __name__ == "__main__":
    main()
