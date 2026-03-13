"""Load ATP M3 policy registry entries."""

from __future__ import annotations

from typing import Any

from core.intake.loader import RequestLoadError
from core.resolution.registry_io import load_yaml_mapping


class PolicyLoadError(ValueError):
    """Raised when a policy reference cannot be loaded."""


def _policy_ref_to_path(policy_ref: str) -> str:
    if policy_ref.startswith("registry/"):
        return policy_ref
    if "/" in policy_ref:
        return policy_ref
    return f"registry/policies/{policy_ref}.yaml"


def load_policy(policy_ref: str) -> dict[str, Any]:
    """Load one minimal policy registry entry."""

    path = _policy_ref_to_path(policy_ref)
    try:
        policy = load_yaml_mapping(path)
    except RequestLoadError as exc:
        raise PolicyLoadError(f"Policy ref not found: {policy_ref}") from exc

    if not isinstance(policy, dict) or not policy.get("policy_name"):
        raise PolicyLoadError(f"Invalid policy file: {policy_ref}")

    return policy


def load_policies(policy_refs: list[str]) -> list[dict[str, Any]]:
    """Load multiple policy registry entries in order."""

    return [load_policy(policy_ref) for policy_ref in policy_refs]
