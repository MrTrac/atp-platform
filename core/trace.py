"""G9 cross-module observability — W3C trace context + JSONL recording.

Implements the G9 Observability Mandate from AI_OS Doctrine v5.0 §1:
every cross-module HTTP call must emit a traceparent header and append
a structured record to ~/.aios/state/cross_module_trace.jsonl.

Schema (locked 5-year per Doctrine v5 G9):
    ts              ISO 8601 UTC timestamp
    request_id      16-char hex identifier
    traceparent     W3C format: 00-<32hex>-<16hex>-01
    source_module   always "atp"
    target_module   e.g. "aokp", "tdf", "aios-flow"
    route           HTTP endpoint path
    method          HTTP method
    status          "ok" | "error"
    duration_ms     round-trip latency in milliseconds
    contract_version e.g. "AOKP_ATP_v2.3"
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

_TRACE_FILE = Path.home() / ".aios" / "state" / "cross_module_trace.jsonl"
_SOURCE_MODULE = "atp"


def generate_request_id() -> str:
    """Return a 16-char hex request ID."""
    return uuid.uuid4().hex[:16]


def build_traceparent(request_id: str) -> str:
    """Build a W3C traceparent string from a request ID.

    Pads or truncates to produce: 00-<32hex>-<16hex>-01
    """
    tid = request_id.ljust(32, "0")[:32]
    sid = request_id[:16].ljust(16, "0")
    return f"00-{tid}-{sid}-01"


def trace_headers(request_id: str) -> dict[str, str]:
    """Return outbound G9 trace headers for an HTTP call."""
    return {
        "x-request-id": request_id,
        "traceparent": build_traceparent(request_id),
        "x-source-module": _SOURCE_MODULE,
    }


def record_trace(
    *,
    request_id: str,
    target_module: str,
    route: str,
    method: str = "POST",
    status: str = "ok",
    duration_ms: int = 0,
    contract_version: str = "",
) -> None:
    """Append a cross-module trace record to the JSONL trace file.

    Silent-fail: never raises, never blocks the caller.
    """
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "traceparent": build_traceparent(request_id),
        "source_module": _SOURCE_MODULE,
        "target_module": target_module,
        "route": route,
        "method": method,
        "status": status,
        "duration_ms": duration_ms,
        "contract_version": contract_version,
    }
    try:
        _TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _TRACE_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        _TRACE_FILE.chmod(0o600)
    except Exception:  # noqa: BLE001
        pass
