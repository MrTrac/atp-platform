"""Run state definitions for ATP M1-M4."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone


def utc_now() -> str:
    """Return a compact UTC timestamp."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class RunState:
    """Enum-like run state names locked for early ATP stages."""

    RECEIVED = "RECEIVED"
    NORMALIZED = "NORMALIZED"
    CLASSIFIED = "CLASSIFIED"
    RESOLVED = "RESOLVED"
    CONTEXT_PACKAGED = "CONTEXT_PACKAGED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class RunRecord:
    """Minimal in-memory run record used by early CLI preview flows."""

    run_id: str
    request_id: str
    state: str
    current_stage: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation."""

        return asdict(self)


def build_run_record(run_id: str, request_id: str, state: str = RunState.RECEIVED) -> dict[str, str]:
    """Create a minimal run record for M1-M4 previews."""

    timestamp = utc_now()
    record = RunRecord(
        run_id=run_id,
        request_id=request_id,
        state=state,
        current_stage=state,
        created_at=timestamp,
        updated_at=timestamp,
    )
    return record.to_dict()
