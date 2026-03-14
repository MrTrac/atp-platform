"""SSH execution adapter placeholder for ATP M6."""

from __future__ import annotations

from typing import Any


def execute_remote(execution_request: dict[str, Any]) -> dict[str, Any]:
    """Return a clear deferred remote execution result."""

    return {
        "command": execution_request.get("payload", {}).get("command_argv", []),
        "exit_code": None,
        "stdout": "",
        "stderr": "Remote SSH execution is deferred in ATP M6.",
        "status": "deferred",
        "notes": ["SSH remote execution is not implemented in M6."],
    }
