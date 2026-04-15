"""SSE (Server-Sent Events) formatting for ATP v2.0.0 streaming.

Emits structured events that AIOS-OC and other clients can consume.
Each event is a JSON object on a `data:` line, terminated by blank line.

Event types:
- ``start``     — request accepted, includes request_id + model + provider
- ``token``     — incremental output chunk (text or tool delta)
- ``manifest``  — final manifest after stream ends (tokens, cost, etc.)
- ``error``     — error during streaming (with error_classification)
- ``done``      — clean end of stream
- ``aborted``   — stream cancelled by client
"""

from __future__ import annotations

import json
from typing import Any


def format_event(event: str, data: dict[str, Any]) -> bytes:
    """Format a single SSE event as bytes for HTTP wfile."""
    payload = json.dumps({"event": event, **data})
    # SSE spec: event:<name>\ndata:<json>\n\n
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


def format_start(request_id: str, provider: str, model: str) -> bytes:
    return format_event("start", {
        "request_id": request_id,
        "provider": provider,
        "model": model,
    })


def format_token(text: str, *, index: int = 0) -> bytes:
    return format_event("token", {"text": text, "index": index})


def format_tool_delta(tool_call: dict[str, Any]) -> bytes:
    """Emit a tool_call_delta event (partial tool invocation)."""
    return format_event("tool_call", tool_call)


def format_manifest(manifest: dict[str, Any]) -> bytes:
    return format_event("manifest", {"manifest": manifest})


def format_error(message: str, error_code: str | None = None) -> bytes:
    data: dict[str, Any] = {"error": message}
    if error_code:
        data["error_code"] = error_code
    return format_event("error", data)


def format_done() -> bytes:
    return format_event("done", {})


def format_aborted(reason: str = "client_cancelled") -> bytes:
    return format_event("aborted", {"reason": reason})
