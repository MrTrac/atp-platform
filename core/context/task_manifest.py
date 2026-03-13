"""Build ATP M4 task manifest payloads."""

from __future__ import annotations

from typing import Any


def _build_required_capabilities(classification: dict[str, Any]) -> list[str]:
    capability = str(classification.get("capability", "")).strip()
    if capability and capability != "unspecified":
        return [capability]
    return []


def build_task_manifest(
    normalized_request: dict[str, Any],
    classification: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    """Build a shallow task manifest for context packaging."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    product = str(resolution.get("product", normalized_request.get("product", ""))).strip()
    if not request_id or not product:
        raise ValueError("Missing request_id or product for task manifest.")

    profile = resolution.get("profile", {})
    target_scope = {
        "module_scope": list(profile.get("module_scope", [])),
        "component_scope": list(profile.get("component_scope", [])),
    }

    return {
        "manifest_id": f"task-manifest-{request_id}",
        "request_id": request_id,
        "product": product,
        "request_type": classification.get("request_type", "unspecified"),
        "execution_intent": classification.get("execution_intent", "unspecified"),
        "required_capabilities": _build_required_capabilities(classification),
        "target_scope": target_scope,
        "input_artifacts": [
            {"artifact_id": f"raw-request-{request_id}", "artifact_type": "request_raw"},
            {"artifact_id": f"normalized-request-{request_id}", "artifact_type": "request_normalized"},
            {"artifact_id": f"classification-{request_id}", "artifact_type": "classification"},
            {"artifact_id": f"resolution-{request_id}", "artifact_type": "resolution"},
        ],
        "notes": ["M4 context packaging only. No routing or execution decisions are made here."],
    }
