"""In-flight request tracker for ATP v2.0.0 cancellation support.

Tracks active bridge requests so they can be cancelled via DELETE /runs/<id>.
Uses a threading.Event per request — adapters check the event to abort
in-flight HTTP calls (or check between streaming chunks).

Thread-safe: all operations protected by a single lock.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import NamedTuple


class InFlightEntry(NamedTuple):
    request_id: str
    abort_event: threading.Event
    started_at: str
    provider: str
    model: str


_LOCK = threading.Lock()
_IN_FLIGHT: dict[str, InFlightEntry] = {}


def register(request_id: str, provider: str = "unknown", model: str = "unknown") -> threading.Event:
    """Register a new in-flight request and return its abort event.

    The caller (bridge handler) creates the event via this call, passes it
    to the adapter, and removes the entry via ``unregister()`` in finally.
    """
    event = threading.Event()
    entry = InFlightEntry(
        request_id=request_id,
        abort_event=event,
        started_at=datetime.now(timezone.utc).isoformat(),
        provider=provider,
        model=model,
    )
    with _LOCK:
        _IN_FLIGHT[request_id] = entry
    return event


def unregister(request_id: str) -> None:
    """Remove an in-flight entry (call in finally block after request completes)."""
    with _LOCK:
        _IN_FLIGHT.pop(request_id, None)


def cancel(request_id: str) -> bool:
    """Set the abort event for a request. Returns True if request was active."""
    with _LOCK:
        entry = _IN_FLIGHT.get(request_id)
    if entry is None:
        return False
    entry.abort_event.set()
    return True


def is_active(request_id: str) -> bool:
    """Check if a request is currently in flight."""
    with _LOCK:
        return request_id in _IN_FLIGHT


def list_active() -> list[dict]:
    """Snapshot of all in-flight requests."""
    with _LOCK:
        snapshot = list(_IN_FLIGHT.values())
    return [
        {
            "request_id": e.request_id,
            "started_at": e.started_at,
            "provider": e.provider,
            "model": e.model,
            "aborted": e.abort_event.is_set(),
        }
        for e in snapshot
    ]


def get_abort_event(request_id: str) -> threading.Event | None:
    """Look up the abort event for a request (used by adapters)."""
    with _LOCK:
        entry = _IN_FLIGHT.get(request_id)
    return entry.abort_event if entry else None


# Test helper — clears all in-flight entries
def _reset() -> None:
    with _LOCK:
        _IN_FLIGHT.clear()
