"""Manifest reference handoff model for ATP M8."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ManifestReference:
    """Reference to an authoritative manifest or final summary artifact."""

    artifact_id: str
    manifest_reference: str
    product: str = "unknown"
    authoritative: bool = True

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["handoff_type"] = "manifest_reference"
        return payload


def build_manifest_reference(
    artifact_id: str,
    manifest_reference: str,
    product: str = "unknown",
) -> dict[str, object]:
    """Build a minimal manifest_reference payload."""

    return ManifestReference(
        artifact_id=artifact_id,
        manifest_reference=manifest_reference,
        product=product,
    ).to_dict()
