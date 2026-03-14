"""Resolve ATP products and build the v0.5 Slice A-C preparation contracts."""

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


def build_resolution_to_handoff_intent_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
    resolution_contract: dict[str, Any],
    manifest_id: str = "",
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice B resolution-to-handoff intent contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the resolution-to-handoff intent contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the resolution-to-handoff intent contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    if not resolution_contract_id:
        raise ValueError("Slice A resolution contract is required for the resolution-to-handoff intent contract.")

    product_target = str(resolution_contract.get("product_target", {}).get("product", "")).strip()
    capability_target = str(resolution_contract.get("capability_target", {}).get("capability", "")).strip()
    if not product_target or not capability_target:
        raise ValueError("Resolved product and capability targets are required for the handoff intent contract.")

    execution_intent = str((classification or {}).get("execution_intent", "unknown")).strip() or "unknown"
    request_type = str((classification or {}).get("request_type", "unknown")).strip() or "unknown"
    rationale_codes = [
        "resolution_to_handoff_intent_contract",
        "handoff_preparation_without_routing_selection",
        "handoff_target_inherited_from_resolution_contract",
    ]

    return {
        "contract_id": f"resolution-to-handoff-intent-{request_id}",
        "contract_version": "v0.5-slice-b",
        "request_id": request_id,
        "run_id": run_id,
        "handoff_scope": "resolution_to_handoff_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "contract_version": str(resolution_contract.get("contract_version", "")),
            "resolution_scope": str(resolution_contract.get("resolution_scope", "")),
            "product_target": product_target,
            "capability_target": capability_target,
        },
        "handoff_intent": {
            "intent": "prepare_structured_product_handoff",
            "intent_stage": "pre_routing",
            "target_product": product_target,
            "target_capability": capability_target,
            "execution_intent": execution_intent,
        },
        "handoff_rationale": {
            "request_type": request_type,
            "execution_intent": execution_intent,
            "rationale_codes": rationale_codes,
            "summary": "ATP is preparing a bounded handoff intent toward the resolved product/capability target.",
        },
        "traceability": {
            "manifest_id": manifest_id,
            "request_to_product_resolution_contract_id": resolution_contract_id,
            "classification_request_type": request_type,
            "classification_execution_intent": execution_intent,
        },
        "notes": [
            "This contract prepares handoff intent only.",
            "It is distinct from classification, routing, provider selection, and broader orchestration.",
        ],
    }


def build_product_execution_preparation_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    task_manifest: dict[str, Any],
    product_context: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice C product execution preparation contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the product execution preparation contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the product execution preparation contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    if not resolution_contract_id or not handoff_intent_contract_id:
        raise ValueError("Slice A and Slice B contracts are required for the execution preparation contract.")

    manifest_id = str(task_manifest.get("manifest_id", "")).strip()
    product_target = str(resolution_contract.get("product_target", {}).get("product", "")).strip()
    capability_target = str(resolution_contract.get("capability_target", {}).get("capability", "")).strip()
    handoff_intent = str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")).strip()
    profile_ref = str(product_context.get("profile_ref", "")).strip()
    evidence_bundle_id = str(evidence_bundle.get("bundle_id", "")).strip()
    if not manifest_id or not product_target or not capability_target or not handoff_intent or not profile_ref:
        raise ValueError("Task manifest, resolved target, handoff intent, and product context are required.")

    return {
        "contract_id": f"product-execution-preparation-{request_id}",
        "contract_version": "v0.5-slice-c",
        "request_id": request_id,
        "run_id": run_id,
        "preparation_scope": "product_execution_preparation_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "resolution_scope": str(resolution_contract.get("resolution_scope", "")),
            "product_target": product_target,
            "capability_target": capability_target,
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_scope": str(handoff_intent_contract.get("handoff_scope", "")),
            "handoff_intent": handoff_intent,
        },
        "execution_preparation": {
            "preparation_mode": "pre_routing_pre_provider",
            "target_product": product_target,
            "target_capability": capability_target,
            "task_manifest_id": manifest_id,
            "product_context_profile": profile_ref,
            "evidence_bundle_id": evidence_bundle_id,
            "required_capabilities": list(task_manifest.get("required_capabilities", [])),
        },
        "preparation_rationale": {
            "rationale_codes": [
                "product_execution_preparation_contract",
                "pre_routing_pre_provider_preparation_only",
                "preparation_package_composed_from_manifest_context_evidence",
            ],
            "summary": "ATP is preparing a bounded execution package before routing, provider selection, and execution.",
            "module_scope_count": len(list(product_context.get("module_scope", []))),
            "selected_evidence_count": len(list(evidence_bundle.get("selected_artifacts", []))),
        },
        "traceability": {
            "task_manifest_id": manifest_id,
            "product_context_profile": profile_ref,
            "evidence_bundle_id": evidence_bundle_id,
            "request_to_product_resolution_contract_id": resolution_contract_id,
            "resolution_to_handoff_intent_contract_id": handoff_intent_contract_id,
        },
        "notes": [
            "This contract prepares a product execution package only.",
            "It is distinct from handoff intent, routing, provider selection, execution result, and broader orchestration.",
        ],
    }
