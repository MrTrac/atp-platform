"""Prepare ATP M5 routing inputs from context packaging outputs."""

from __future__ import annotations

from typing import Any

from core.intake.loader import RequestLoadError
from core.resolution.registry_io import load_yaml_mapping


class RoutePreparationError(ValueError):
    """Raised when routing preparation cannot be completed."""


def _derive_required_capabilities(
    normalized_request: dict[str, Any],
    classification: dict[str, Any],
    task_manifest: dict[str, Any],
) -> list[str]:
    manifest_capabilities = list(task_manifest.get("required_capabilities", []))
    if manifest_capabilities:
        return manifest_capabilities

    explicit_capability = str(normalized_request.get("metadata", {}).get("capability", "")).strip()
    if explicit_capability and explicit_capability != "unspecified":
        return [explicit_capability]

    request_type = str(classification.get("request_type", "")).strip()
    execution_intent = str(classification.get("execution_intent", "")).strip()

    if request_type == "test" or execution_intent == "validate":
        return ["test_operation"]
    if request_type == "review" or execution_intent == "inspect":
        return ["lint_operation"]
    if request_type == "fix" or execution_intent == "update":
        return ["git_operation"]
    return ["shell_execution"]


def _load_capability(capability_name: str) -> dict[str, Any]:
    try:
        return load_yaml_mapping(f"registry/capabilities/{capability_name}.yaml")
    except RequestLoadError as exc:
        raise RoutePreparationError(f"Capability not found: {capability_name}") from exc


def _load_provider(provider_name: str) -> dict[str, Any]:
    try:
        return load_yaml_mapping(f"registry/providers/{provider_name}.yaml")
    except RequestLoadError as exc:
        raise RoutePreparationError(f"Provider not found: {provider_name}") from exc


def _load_node(node_name: str) -> dict[str, Any]:
    try:
        return load_yaml_mapping(f"registry/nodes/{node_name}.yaml")
    except RequestLoadError as exc:
        raise RoutePreparationError(f"Node not found: {node_name}") from exc


def prepare_route(
    normalized_request: dict[str, Any],
    classification: dict[str, Any],
    resolution: dict[str, Any],
    task_manifest: dict[str, Any],
    product_context: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Build shallow routing preparation data for M5."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    product = str(resolution.get("product", "")).strip()
    if not request_id or not product:
        raise RoutePreparationError("Missing request_id or product for route preparation.")

    required_capabilities = _derive_required_capabilities(
        normalized_request,
        classification,
        task_manifest,
    )
    capability_details = [_load_capability(capability_name) for capability_name in required_capabilities]

    routing_policy_refs = [
        policy_ref for policy_ref in product_context.get("policy_refs", []) if "routing" in policy_ref
    ]
    cost_policy_refs = [
        policy_ref for policy_ref in product_context.get("policy_refs", []) if "cost" in policy_ref
    ]

    provider_names = ["non_llm_execution"]
    candidate_providers = [_load_provider(provider_name) for provider_name in provider_names]
    node_names = ["local_mac"]
    candidate_nodes = [_load_node(node_name) for node_name in node_names]

    return {
        "request_id": request_id,
        "product": product,
        "required_capabilities": required_capabilities,
        "capability_details": capability_details,
        "candidate_providers": candidate_providers,
        "candidate_nodes": candidate_nodes,
        "routing_policy_refs": routing_policy_refs,
        "cost_policy_refs": cost_policy_refs,
        "product_context_ref": product_context.get("profile_ref", ""),
        "manifest_reference": task_manifest.get("manifest_id", ""),
        "evidence_bundle_id": evidence_bundle.get("bundle_id", ""),
    }
