"""Select ATP M4 evidence artifacts for next-step continuity."""

from __future__ import annotations

from typing import Any


ALLOWED_ARTIFACT_TYPES = {
    "request_raw",
    "request_normalized",
    "classification",
    "resolution",
    "task_manifest",
    "product_context",
}


def select_evidence(artifacts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Select the core artifacts needed for later packaging stages."""

    selected: list[dict[str, Any]] = []
    authoritative_refs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for artifact in artifacts:
        artifact_id = str(artifact.get("artifact_id", "")).strip()
        artifact_type = str(artifact.get("artifact_type", "")).strip()
        if not artifact_id or artifact_type not in ALLOWED_ARTIFACT_TYPES or artifact_id in seen_ids:
            continue

        selected_artifact = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "artifact_freshness": artifact.get("artifact_freshness", "current"),
            "authoritative": bool(artifact.get("authoritative", False)),
        }
        selected.append(selected_artifact)
        seen_ids.add(artifact_id)

        if selected_artifact["authoritative"]:
            authoritative_refs.append(
                {
                    "artifact_id": artifact_id,
                    "manifest_reference": artifact.get("manifest_reference", ""),
                }
            )

    return {
        "selected_artifacts": selected,
        "authoritative_refs": authoritative_refs,
    }
