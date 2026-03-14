"""Inline context handoff model for ATP M8."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class InlineContext:
    """Concise handoff payload carrying essential continuity fields."""

    summary: str
    request_id: str = "request-unknown"
    product: str = "unknown"
    final_status: str = "unknown"
    review_status: str = "unknown"
    authoritative: bool = False
    artifact_freshness: str = "current"

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["handoff_type"] = "inline_context"
        return payload


def build_inline_context(
    summary: str,
    request_id: str = "request-unknown",
    product: str = "unknown",
    final_status: str = "unknown",
    review_status: str = "unknown",
    authoritative: bool = False,
) -> dict[str, object]:
    """Build a minimal inline_context payload."""

    return InlineContext(
        summary=summary,
        request_id=request_id,
        product=product,
        final_status=final_status,
        review_status=review_status,
        authoritative=authoritative,
    ).to_dict()
