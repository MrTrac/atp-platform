"""Normalize raw adapter output into ATP M6 execution results."""

from __future__ import annotations

from typing import Any


def normalize_output(
    raw_result: dict[str, Any],
    request_id: str,
    product: str,
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Return a stable normalized ATP execution result."""

    exit_code = raw_result.get("exit_code")
    if exit_code is None:
        status = raw_result.get("status", "deferred")
    else:
        status = "succeeded" if exit_code == 0 else "failed"

    return {
        "execution_id": f"execution-{request_id}",
        "request_id": request_id,
        "product": product,
        "selected_provider": routing_result.get("selected_provider", "unknown"),
        "selected_node": routing_result.get("selected_node", "unknown"),
        "command": raw_result.get("command", []),
        "exit_code": exit_code,
        "stdout": raw_result.get("stdout", ""),
        "stderr": raw_result.get("stderr", ""),
        "status": status,
        "notes": list(raw_result.get("notes", [])),
    }
