"""Resolve ATP products and build the v0.5 Slice A request-to-product contract."""

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

    return {**registry_entry, "registry_entry_ref": registry_path}


def _load_profile(profile_ref: str) -> dict[str, Any]:
    try:
        profile = load_yaml_mapping(profile_ref)
    except RequestLoadError as exc:
        raise ProductResolutionError(f"Profile ref not found: {profile_ref}") from exc

    if not profile.get("product"):
        raise ProductResolutionError(f"Invalid profile file: {profile_ref}")

    return profile


def _select_capability_target(
    classification: dict[str, Any] | None,
    profile: dict[str, Any],
) -> tuple[str, str]:
    if classification:
        classified_capability = str(classification.get("capability", "")).strip()
        if classified_capability and classified_capability != "unspecified":
            return classified_capability, "classification.capability"

    component_scope = profile.get("component_scope", [])
    if isinstance(component_scope, list) and component_scope:
        first_component = str(component_scope[0]).strip()
        if first_component:
            return first_component, "profile.component_scope"

    return "product_resolution", "resolution.default"


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
        "registry_entry_ref": registry_entry.get("registry_entry_ref", ""),
        "status": registry_entry.get("status", "unknown"),
        "profile_ref": profile_ref,
        "profile": profile,
        "policy_refs": policy_refs,
        "policies": policies,
    }


def build_request_to_product_resolution_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
    resolution: dict[str, Any],
    manifest_id: str = "",
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice A request-to-product resolution contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the request-to-product resolution contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the request-to-product resolution contract.")

    product_target = str(resolution.get("product", "")).strip()
    if not product_target:
        raise ValueError("resolved product is required for the request-to-product resolution contract.")

    capability_target, capability_source = _select_capability_target(
        classification,
        dict(resolution.get("profile", {})),
    )
    requested_product = str(normalized_request.get("product", "")).strip()
    classified_product = str((classification or {}).get("product", "")).strip()
    rationale_codes = [
        "request_to_product_resolution_contract",
        "product_target_resolved_from_registry",
        "capability_target_selected_without_routing",
    ]
    if requested_product and requested_product != "unknown":
        product_source = "normalized_request.product"
        rationale_codes.append("product_target_from_request")
    else:
        product_source = "classification.product"
        rationale_codes.append("product_target_from_classification")

    return {
        "contract_id": f"request-to-product-resolution-{request_id}",
        "contract_version": "v0.5-slice-a",
        "request_id": request_id,
        "run_id": run_id,
        "resolution_scope": "request_to_product_only",
        "product_target": {
            "product": product_target,
            "product_type": str(resolution.get("product_type", "unknown")),
            "repo_boundary": str(resolution.get("repo_boundary", "unknown")),
            "status": str(resolution.get("status", "unknown")),
        },
        "capability_target": {
            "capability": capability_target,
            "source": capability_source,
        },
        "resolution_rationale": {
            "product_source": product_source,
            "requested_product": requested_product or "unspecified",
            "classified_product": classified_product or "unspecified",
            "profile_ref": str(resolution.get("profile_ref", "")),
            "registry_entry_ref": str(resolution.get("registry_entry_ref", "")),
            "policy_refs": list(resolution.get("policy_refs", [])),
            "rationale_codes": rationale_codes,
        },
        "traceability": {
            "manifest_id": manifest_id,
            "classification_request_type": str((classification or {}).get("request_type", "unknown")),
            "classification_execution_intent": str((classification or {}).get("execution_intent", "unknown")),
            "classification_capability": str((classification or {}).get("capability", "unspecified")),
            "profile_ref": str(resolution.get("profile_ref", "")),
            "repo_boundary": str(resolution.get("repo_boundary", "unknown")),
        },
        "notes": [
            "This contract resolves request intent to a product target and capability target only.",
            "It is distinct from classification, routing, provider selection, and broader orchestration.",
        ],
    }
