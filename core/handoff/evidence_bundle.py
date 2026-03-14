"""Evidence bundle handoff model for ATP M8."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class EvidenceBundle:
    """Dict-based handoff payload for selected evidence."""

    bundle_id: str
    request_id: str
    product: str
    selected_artifacts: list[dict[str, object]] = field(default_factory=list)
    authoritative_refs: list[dict[str, object]] = field(default_factory=list)
    manifest_reference: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["handoff_type"] = "evidence_bundle"
        return payload


def build_evidence_bundle(
    selected_artifacts: list[dict[str, object]],
    request_id: str = "request-unknown",
    product: str = "unknown",
    bundle_id: str | None = None,
    authoritative_refs: list[dict[str, object]] | None = None,
    manifest_reference: str = "",
) -> dict[str, object]:
    """Build a minimal evidence_bundle payload."""

    resolved_bundle_id = bundle_id or f"handoff-evidence-{request_id}"
    return EvidenceBundle(
        bundle_id=resolved_bundle_id,
        request_id=request_id,
        product=product,
        selected_artifacts=list(selected_artifacts),
        authoritative_refs=list(authoritative_refs or []),
        manifest_reference=manifest_reference,
        notes=["ATP v0 evidence bundle handoff summary."],
    ).to_dict()
