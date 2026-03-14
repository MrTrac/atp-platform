"""Filesystem exchange helpers for ATP M6."""

from __future__ import annotations

from typing import Any


def write_exchange_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return a shaped ATP-side exchange summary without external writes."""

    return {
        "bundle_id": bundle.get("bundle_id", "bundle-unknown"),
        "status": "in_memory_only",
        "notes": ["Production workspace exchange materialization is deferred in M6."],
    }
