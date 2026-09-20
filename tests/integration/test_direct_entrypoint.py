from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def test_main_file_can_be_executed_directly(tmp_path: Path) -> None:
    port = 8771
    environment = os.environ.copy()
    environment.update(
        {
            "APP_PORT": str(port),
            "OAUTH_CLIENT_ID": "test-client",
            "OAUTH_CLIENT_SECRET": "test-client-secret",
            "OAUTH_JWT_SECRET": "test-jwt-secret-that-is-at-least-32-bytes",
        }
    )
    conflicting_package = tmp_path / "app"
    conflicting_package.mkdir()
    (conflicting_package / "__init__.py").write_text("", encoding="utf-8")
    environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(tmp_path), environment.get("PYTHONPATH")))
    )
    main_file = Path(__file__).parents[2] / "app" / "main.py"
    process = subprocess.Popen(
        (sys.executable, str(main_file)),
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        for _ in range(50):
            if process.poll() is not None:
                raise AssertionError(process.stderr.read() if process.stderr else "")
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/health", timeout=1
                )
            except urllib.error.HTTPError as error:
                assert error.code == 401
                break
            except urllib.error.URLError:
                time.sleep(0.1)
        else:
            raise AssertionError("直接执行 app/main.py 后服务未启动")
    finally:
        process.terminate()
        process.wait(timeout=5)
