"""Select ATP M5-M6 routes using deterministic capability-based rules."""

from __future__ import annotations

from typing import Any

from core.routing.routing_result import build_routing_result


class RouteSelectionError(ValueError):
    """Raised when a valid route cannot be selected."""


def _provider_supports(provider: dict[str, Any], required_capabilities: list[str]) -> bool:
    supported = set(provider.get("supported_capabilities", []))
    return all(capability in supported for capability in required_capabilities)


def _score_provider(provider: dict[str, Any], required_capabilities: list[str]) -> tuple[int, int, str]:
    provider_name = str(provider.get("provider", ""))
    preferred_provider = 0 if provider_name == "non_llm_execution" else 1
    low_cost = 0 if str(provider.get("cost_profile", "")) == "low" else 1
    capability_fit = len(required_capabilities)
    return (preferred_provider, low_cost, str(capability_fit))


def _compatible_nodes(provider: dict[str, Any], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    provider_type = str(provider.get("provider_type", ""))
    provider_supported_nodes = set(provider.get("supported_nodes", []))
    compatible: list[dict[str, Any]] = []
    for node in nodes:
        if node.get("status") != "active":
            continue
        if provider_type not in set(node.get("supported_provider_types", [])):
            continue
        if provider_supported_nodes and node.get("node") not in provider_supported_nodes:
            continue
        compatible.append(node)
    return compatible


def _score_node(node: dict[str, Any]) -> tuple[int, str]:
    node_name = str(node.get("node", ""))
    local_preference = 0 if node_name == "local_mac" else 1
    return (local_preference, node_name)


def select_route(prepared_route: dict[str, Any]) -> dict[str, Any]:
    """Select one provider and one node from prepared routing candidates."""

    required_capabilities = list(prepared_route.get("required_capabilities", []))
    providers = list(prepared_route.get("candidate_providers", []))
    nodes = list(prepared_route.get("candidate_nodes", []))

    matching_providers = [
        provider
        for provider in providers
        if provider.get("status") == "active" and _provider_supports(provider, required_capabilities)
    ]
    if not matching_providers:
        capability_label = ",".join(required_capabilities) or "unknown"
        raise RouteSelectionError(f"No provider supports capability: {capability_label}")

    selected_provider = sorted(
        matching_providers,
        key=lambda provider: _score_provider(provider, required_capabilities),
    )[0]
    compatible_nodes = _compatible_nodes(selected_provider, nodes)
    if not compatible_nodes:
        raise RouteSelectionError(
            f"No compatible node for provider: {selected_provider.get('provider', 'unknown')}"
        )

    selected_node = sorted(compatible_nodes, key=_score_node)[0]
    reason_codes = [
        "capability_supported",
        "provider_local_first",
        "node_local_mac_preferred" if selected_node.get("node") == "local_mac" else "node_selected",
    ]
    if selected_provider.get("provider") == "non_llm_execution":
        reason_codes.append("provider_non_llm_preferred")

    execution_path = "local_subprocess" if (
        selected_provider.get("provider") == "non_llm_execution"
        and selected_node.get("node") == "local_mac"
    ) else "deferred"

    cost_summary = {
        "policy_mode": "local_first",
        "provider_cost_profile": selected_provider.get("cost_profile", "unknown"),
        "explanation": "Selected the lowest-cost local-compatible route available in ATP v0.",
    }

    return build_routing_result(
        request_id=str(prepared_route.get("request_id", "")),
        product=str(prepared_route.get("product", "")),
        required_capabilities=required_capabilities,
        candidate_providers=[provider.get("provider", "unknown") for provider in matching_providers],
        candidate_nodes=[node.get("node", "unknown") for node in compatible_nodes],
        selected_provider=str(selected_provider.get("provider", "")),
        selected_node=str(selected_node.get("node", "")),
        reason_codes=reason_codes,
        cost_summary=cost_summary,
        execution_path=execution_path,
    )
