"""Minimal handoff adapter contract for ATP M6."""

from __future__ import annotations

from typing import Any, Protocol


class HandoffAdapter(Protocol):
    """Handoff adapters accept ATP-native bundle payloads."""

    def handoff(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Hand off a prepared ATP payload."""

