from __future__ import annotations

import subprocess

import pytest

from scripts.check import Command, run_steps


def test_checker_stops_after_first_failed_layer() -> None:
    calls: list[Command] = []

    def fail_in_integration(command: Command) -> None:
        calls.append(command)
        if command == ("integration",):
            raise subprocess.CalledProcessError(1, command)

    with pytest.raises(subprocess.CalledProcessError):
        run_steps(
            (
                ("unit", ("unit",)),
                ("integration", ("integration",)),
                ("e2e", ("e2e",)),
            ),
            runner=fail_in_integration,
        )

    assert calls == [("unit",), ("integration",)]
