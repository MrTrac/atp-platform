"""Helpers for ATP M1-M2 run state transitions."""

from __future__ import annotations

from typing import Any

from core.state.run_state import utc_now


def build_transition_record(
    run_id: str,
    from_state: str | None,
    to_state: str,
    stage: str,
    detail: str = "",
) -> dict[str, Any]:
    """Build a transition record without persisting it."""

    return {
        "run_id": run_id,
        "from_state": from_state,
        "to_state": to_state,
        "stage": stage,
        "detail": detail,
        "recorded_at": utc_now(),
    }


def advance_run_state(run_record: dict[str, Any], to_state: str, detail: str = "") -> dict[str, Any]:
    """Return an updated run record plus its latest transition record."""

    updated = dict(run_record)
    transition = build_transition_record(
        run_id=str(updated.get("run_id", "run-unknown")),
        from_state=updated.get("state"),
        to_state=to_state,
        stage=to_state,
        detail=detail,
    )
    updated["state"] = to_state
    updated["current_stage"] = to_state
    updated["updated_at"] = transition["recorded_at"]
    updated["latest_transition"] = transition
    return updated
