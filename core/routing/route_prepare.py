"""Prepare ATP M5 routing inputs from context packaging outputs.

Provider and node candidates are discovered from the registry
directory rather than hardcoded, allowing new providers to be
added by dropping a YAML file without modifying this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.intake.loader import RequestLoadError, load_request
from core.resolution.registry_io import load_yaml_mapping


REGISTRY_ROOT = Path(__file__).resolve().parents[2] / "registry"


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


def _discover_active_providers() -> list[dict[str, Any]]:
    """Scan registry/providers/ for active provider YAML entries."""
    providers_dir = REGISTRY_ROOT / "providers"
    if not providers_dir.is_dir():
        return []
    providers: list[dict[str, Any]] = []
    for yaml_file in sorted(providers_dir.glob("*.yaml")):
        try:
            entry = load_request(yaml_file)
        except RequestLoadError:
            continue
        if entry.get("status") == "active":
            providers.append(entry)
    return providers


def _discover_active_nodes() -> list[dict[str, Any]]:
    """Scan registry/nodes/ for active node YAML entries."""
    nodes_dir = REGISTRY_ROOT / "nodes"
    if not nodes_dir.is_dir():
        return []
    nodes: list[dict[str, Any]] = []
    for yaml_file in sorted(nodes_dir.glob("*.yaml")):
        try:
            entry = load_request(yaml_file)
        except RequestLoadError:
            continue
        if entry.get("status") == "active":
            nodes.append(entry)
    return nodes


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

    candidate_providers = _discover_active_providers()
    candidate_nodes = _discover_active_nodes()

    if not candidate_providers:
        raise RoutePreparationError("No active providers found in registry.")
    if not candidate_nodes:
        raise RoutePreparationError("No active nodes found in registry.")

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
