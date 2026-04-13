"""Optional AOKP knowledge context enrichment for ATP bridge requests.

When enabled, queries the AOKP v2.3.x knowledge platform to enrich
incoming requests with relevant context before execution.
Disabled by default. Graceful degradation: AOKP being unavailable
never blocks execution.

Capabilities used: health check (/api/health), knowledge retrieval
(/api/search), graph query (/api/graph).
"""

from __future__ import annotations

import os
from typing import Any

from adapters.aokp.aokp_adapter import check_health, query_graph, query_knowledge


AOKP_ENABLED = os.environ.get("ATP_AOKP_ENABLED", "").lower() in ("1", "true", "yes")
AOKP_BASE_URL = os.environ.get("ATP_AOKP_URL", "http://localhost:3002")
AOKP_GRAPH_ENABLED = os.environ.get("ATP_AOKP_GRAPH", "").lower() in ("1", "true", "yes")


def enrich_context(incoming: dict[str, Any]) -> dict[str, Any]:
    """Optionally enrich an incoming bridge request with AOKP knowledge.

    Adds an ``aokp_context`` key to the returned dict if enrichment
    succeeds. Never mutates ``text``, ``model``, or ``context``.
    Returns the incoming dict unchanged if AOKP is disabled or unavailable.

    When ``ATP_AOKP_GRAPH=true``, also queries the knowledge graph for
    entity/relation context alongside retrieval hits.

    Parameters
    ----------
    incoming : dict
        The raw bridge request (must have ``text``).

    Returns
    -------
    dict
        The incoming dict, possibly with ``aokp_context`` added.
    """
    if not AOKP_ENABLED:
        return incoming

    health = check_health(base_url=AOKP_BASE_URL, timeout=3)
    if health.get("status") != "ok":
        return incoming

    query_text = (incoming.get("text") or "").strip()
    if not query_text:
        return incoming

    result = query_knowledge(
        {"query": query_text, "top_k": 3},
        base_url=AOKP_BASE_URL,
    )

    if result.get("status") != "success" or not result.get("hits"):
        return incoming

    enriched = dict(incoming)
    aokp_ctx: dict[str, Any] = {
        "context_text": result["context_text"],
        "hit_count": len(result["hits"]),
        "manifest": result["manifest"],
        "aokp_version": health.get("aokp_version", "unknown"),
    }

    if AOKP_GRAPH_ENABLED:
        graph_result = query_graph(
            {"term": query_text},
            base_url=AOKP_BASE_URL,
        )
        if graph_result.get("status") == "success":
            aokp_ctx["graph_entities"] = len(graph_result.get("entities", []))
            aokp_ctx["graph_relations"] = len(graph_result.get("relations", []))

    enriched["aokp_context"] = aokp_ctx
    return enriched
