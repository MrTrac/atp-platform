"""Map ATP routing results to execution adapters for M6."""

from __future__ import annotations

from typing import Any

from adapters.subprocess.local_exec_adapter import LocalExecutionError, execute_local
from adapters.ssh_remote.ssh_exec_adapter import execute_remote


class ExecutionError(ValueError):
    """Raised when ATP cannot execute the selected route."""


def invoke_executor(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Invoke the adapter mapped from the selected provider and node."""

    provider = routing_result.get("selected_provider")
    node = routing_result.get("selected_node")

    if provider == "non_llm_execution" and node == "local_mac":
        try:
            return execute_local(normalized_request)
        except LocalExecutionError as exc:
            raise ExecutionError(str(exc)) from exc

    if provider and node:
        return execute_remote(normalized_request)

    raise ExecutionError("Unsupported execution route.")
