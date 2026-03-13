"""Build ATP M5 routing result payloads."""

from __future__ import annotations

from typing import Any


def build_routing_result(
    request_id: str,
    product: str,
    required_capabilities: list[str],
    candidate_providers: list[str],
    candidate_nodes: list[str],
    selected_provider: str,
    selected_node: str,
    reason_codes: list[str],
    cost_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a stable routing result structure."""

    return {
        "route_id": f"route-{request_id}",
        "request_id": request_id,
        "product": product,
        "required_capabilities": list(required_capabilities),
        "candidate_providers": list(candidate_providers),
        "candidate_nodes": list(candidate_nodes),
        "selected_provider": selected_provider,
        "selected_node": selected_node,
        "reason_codes": list(reason_codes),
        "cost_summary": dict(cost_summary),
        "status": "selected",
    }
