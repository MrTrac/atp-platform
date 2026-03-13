"""Evidence bundle seed model for ATP M1-M2."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class EvidenceBundle:
    """Small evidence bundle payload for later handoff stages."""

    artifacts: list[dict[str, object]] = field(default_factory=list)
    authoritative: bool = True

    def to_dict(self) -> dict[str, object]:
        """Return a serializable handoff payload."""

        payload = asdict(self)
        payload["handoff_type"] = "evidence_bundle"
        return payload


def build_evidence_bundle(artifacts: list[dict[str, object]]) -> dict[str, object]:
    """Build a minimal evidence_bundle payload."""

    return EvidenceBundle(artifacts=list(artifacts)).to_dict()
