"""Determine close-or-continue semantics for ATP M8."""

from __future__ import annotations

from typing import Any


def close_or_continue(approval_result: dict[str, Any]) -> str:
    """Return the next run decision from approval status."""

    approval_status = str(approval_result.get("approval_status", "needs_attention"))
    if approval_status == "approved":
        return "close"
    if approval_status == "needs_attention":
        return "continue_pending"
    return "close_rejected"
