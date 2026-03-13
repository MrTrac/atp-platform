"""Build ATP M4 product context payloads."""

from __future__ import annotations

from typing import Any


def build_product_context(resolution: dict[str, Any]) -> dict[str, Any]:
    """Build a minimal product context from a resolution result."""

    product = str(resolution.get("product", "")).strip()
    repo_boundary = str(resolution.get("repo_boundary", "")).strip()
    profile_ref = str(resolution.get("profile_ref", "")).strip()
    profile = resolution.get("profile", {})
    policies = list(resolution.get("policies", []))

    if not product or not repo_boundary or not profile_ref or not isinstance(profile, dict):
        raise ValueError("Missing required resolution inputs for product context.")

    return {
        "product": product,
        "repo_boundary": repo_boundary,
        "profile_ref": profile_ref,
        "module_scope": list(profile.get("module_scope", [])),
        "component_scope": list(profile.get("component_scope", [])),
        "policy_refs": list(resolution.get("policy_refs", [])),
        "policy_names": [policy.get("policy_name", "unknown") for policy in policies],
        "context_notes": list(profile.get("notes", [])),
    }
