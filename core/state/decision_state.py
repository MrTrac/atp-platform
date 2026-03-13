"""Decision state definitions for ATP M1-M2."""

from __future__ import annotations

from dataclasses import dataclass, asdict


class DecisionState:
    """Enum-like early decision states for pre-approval ATP flow."""

    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class DecisionRecord:
    """Minimal decision-state payload for future approval and review stages."""

    approval_gate: str = DecisionState.DEFERRED
    review_state: str = DecisionState.NOT_REQUIRED

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation."""

        return asdict(self)


def initial_decision_state() -> dict[str, str]:
    """Return the default early decision state."""

    return DecisionRecord().to_dict()
