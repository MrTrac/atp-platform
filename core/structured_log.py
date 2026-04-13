"""Structured JSON logging for ATP — no external dependencies.

Provides ``log_event()`` which writes JSON-lines to stderr. Each event
includes timestamp, request_id, and typed fields for audit/governance.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any


def log_event(
    event: str,
    *,
    request_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    duration_ms: int | None = None,
    status: str | None = None,
    error: str | None = None,
    error_code: str | None = None,
    tokens: int | None = None,
    cost_usd: float | None = None,
    **extra: Any,
) -> None:
    """Write a structured JSON log event to stderr.

    Parameters
    ----------
    event : str
        Event name (e.g., "bridge.request", "executor.dispatch", "escalation.triggered").
    """
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    if request_id is not None:
        record["request_id"] = request_id
    if provider is not None:
        record["provider"] = provider
    if model is not None:
        record["model"] = model
    if duration_ms is not None:
        record["duration_ms"] = duration_ms
    if status is not None:
        record["status"] = status
    if error is not None:
        record["error"] = error
    if error_code is not None:
        record["error_code"] = error_code
    if tokens is not None:
        record["tokens"] = tokens
    if cost_usd is not None:
        record["cost_usd"] = cost_usd
    if extra:
        record.update(extra)

    try:
        print(json.dumps(record), file=sys.stderr, flush=True)
    except Exception:
        pass
