"""Inline context seed model for ATP M1-M2."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class InlineContext:
    """Small handoff payload carrying concise human-readable context."""

    summary: str
    authoritative: bool = False
    artifact_freshness: str = "current"

    def to_dict(self) -> dict[str, object]:
        """Return a serializable handoff payload."""

        payload = asdict(self)
        payload["handoff_type"] = "inline_context"
        return payload


def build_inline_context(summary: str, authoritative: bool = False) -> dict[str, object]:
    """Build a minimal inline_context payload."""

    return InlineContext(summary=summary, authoritative=authoritative).to_dict()
