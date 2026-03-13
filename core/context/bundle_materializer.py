"""Materialize ATP M4 evidence bundle payloads in memory."""

from __future__ import annotations

from typing import Any


def materialize_bundle(
    request_id: str,
    product: str,
    evidence_selection: dict[str, list[dict[str, Any]]],
    manifest_reference: str,
) -> dict[str, Any]:
    """Build a stable in-memory evidence bundle structure."""

    if not request_id or not product or not manifest_reference:
        raise ValueError("Missing request_id, product, or manifest_reference for evidence bundle.")

    selected_artifacts = list(evidence_selection.get("selected_artifacts", []))
    authoritative_refs = list(evidence_selection.get("authoritative_refs", []))

    return {
        "bundle_id": f"evidence-bundle-{request_id}",
        "request_id": request_id,
        "product": product,
        "selected_artifacts": selected_artifacts,
        "authoritative_refs": authoritative_refs,
        "manifest_reference": manifest_reference,
        "notes": ["M4 in-memory bundle only. No filesystem or workspace materialization."],
    }
