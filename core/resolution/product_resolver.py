"""Resolve ATP M3 products from registry, profile, and policy references."""

from __future__ import annotations

from typing import Any

from core.intake.loader import RequestLoadError
from core.resolution.policy_loader import PolicyLoadError, load_policies
from core.resolution.registry_io import load_yaml_mapping


class ProductResolutionError(ValueError):
    """Raised when a product cannot be resolved."""


def _select_product(
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
) -> str:
    product = str(normalized_request.get("product", "")).strip()
    if product and product != "unknown":
        return product.upper()

    if classification:
        classified_product = str(classification.get("product", "")).strip()
        if classified_product and classified_product != "unknown":
            return classified_product.upper()

    raise ProductResolutionError("Product could not be resolved from request.")


def _load_registry_entry(product: str) -> dict[str, Any]:
    registry_path = f"registry/products/{product}.yaml"
    try:
        registry_entry = load_yaml_mapping(registry_path)
    except RequestLoadError as exc:
        raise ProductResolutionError(f"Product registry entry not found: {product}") from exc

    if not registry_entry.get("profile_ref"):
        raise ProductResolutionError(f"Missing profile_ref for product: {product}")

    return registry_entry


def _load_profile(profile_ref: str) -> dict[str, Any]:
    try:
        profile = load_yaml_mapping(profile_ref)
    except RequestLoadError as exc:
        raise ProductResolutionError(f"Profile ref not found: {profile_ref}") from exc

    if not profile.get("product"):
        raise ProductResolutionError(f"Invalid profile file: {profile_ref}")

    return profile


def resolve_product(
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve a product from file-based registry, profile, and policies."""

    product = _select_product(normalized_request, classification)
    registry_entry = _load_registry_entry(product)
    profile_ref = str(registry_entry["profile_ref"])
    policy_refs = list(registry_entry.get("policy_refs", []))

    try:
        profile = _load_profile(profile_ref)
        policies = load_policies(policy_refs)
    except PolicyLoadError as exc:
        raise ProductResolutionError(str(exc)) from exc

    return {
        "product": registry_entry["product"],
        "product_type": registry_entry.get("product_type", "unknown"),
        "repo_boundary": registry_entry.get("repo_boundary", "unknown"),
        "status": registry_entry.get("status", "unknown"),
        "profile_ref": profile_ref,
        "profile": profile,
        "policy_refs": policy_refs,
        "policies": policies,
    }
