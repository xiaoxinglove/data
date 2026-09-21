from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path

Command = tuple[str, ...]
Runner = Callable[[Command], None]

STEPS: tuple[tuple[str, Command], ...] = (
    ("静态检查", (sys.executable, "-m", "ruff", "check", ".")),
    ("类型检查", (sys.executable, "-m", "mypy")),
    ("单元测试", (sys.executable, "-m", "pytest", "tests/unit", "-q")),
    (
        "集成测试",
        (
            sys.executable,
            "-m",
            "pytest",
            "tests/integration",
            "tests/security",
            "-q",
        ),
    ),
    ("端到端测试", (sys.executable, "scripts/http_check.py")),
)


def run_command(command: Command) -> None:
    subprocess.run(command, check=True)


def run_steps(
    steps: Sequence[tuple[str, Command]], runner: Runner = run_command
) -> None:
    for name, command in steps:
        print(f"\n== {name} ==", flush=True)
        runner(command)


def write_result(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "feature": "F001",
                "status": "passing",
                "verified_at": datetime.now(UTC).isoformat(),
                "git_commit": _git_commit(),
                "evidence": "ruff + mypy --strict + unit + integration + HTTP e2e",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _git_commit() -> str:
    return subprocess.run(
        ("git", "rev-parse", "HEAD"),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    run_steps(STEPS)
    write_result(Path(".check_data/F001.json"))
    print("\nF001 verification passed", flush=True)


if __name__ == "__main__":
    main()
