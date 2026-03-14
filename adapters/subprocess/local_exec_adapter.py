"""Safe local subprocess execution adapter for ATP M6."""

from __future__ import annotations

import subprocess
from typing import Any


class LocalExecutionError(ValueError):
    """Raised when a local execution request is invalid."""


def _coerce_command(execution_request: dict[str, Any]) -> tuple[list[str], list[str] | None]:
    payload = execution_request.get("payload", {})
    command_argv = payload.get("command_argv")
    if isinstance(command_argv, list) and command_argv and all(isinstance(part, str) for part in command_argv):
        return command_argv, command_argv

    command = payload.get("command")
    if isinstance(command, str) and command.startswith("echo ") and command.strip():
        return ["echo", command[5:]], None

    raise LocalExecutionError("Missing supported command_argv for local execution.")


def execute_local(execution_request: dict[str, Any]) -> dict[str, Any]:
    """Execute a constrained local command and capture raw subprocess output."""

    argv, explicit_argv = _coerce_command(execution_request)
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": explicit_argv or argv,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "status": "completed" if completed.returncode == 0 else "failed",
        "notes": ["Executed through adapters/subprocess/local_exec_adapter.py"],
    }
