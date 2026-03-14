"""Minimal execution adapter contract for ATP M6."""

from __future__ import annotations

from typing import Any, Protocol


class ExecutionAdapter(Protocol):
    """Execution adapters accept ATP-native dict inputs and return raw dict outputs."""

    def execute(self, execution_request: dict[str, Any]) -> dict[str, Any]:
        """Execute a prepared ATP request payload."""

