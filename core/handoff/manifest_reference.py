"""Manifest reference seed model for ATP M1-M2."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ManifestReference:
    """Reference to an authoritative manifest artifact."""

    artifact_id: str
    manifest_reference: str
    authoritative: bool = True

    def to_dict(self) -> dict[str, object]:
        """Return a serializable handoff payload."""

        payload = asdict(self)
        payload["handoff_type"] = "manifest_reference"
        return payload


def build_manifest_reference(artifact_id: str, manifest_reference: str) -> dict[str, object]:
    """Build a minimal manifest_reference payload."""

    return ManifestReference(
        artifact_id=artifact_id,
        manifest_reference=manifest_reference,
    ).to_dict()
