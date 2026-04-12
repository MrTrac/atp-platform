"""Optional AOKP knowledge context enrichment for ATP bridge requests.

When enabled, queries the AOKP knowledge platform to enrich incoming
requests with relevant context before execution. Disabled by default.
Graceful degradation: AOKP being unavailable never blocks execution.
"""

from __future__ import annotations

import os
from typing import Any

from adapters.aokp.aokp_adapter import check_health, query_knowledge


AOKP_ENABLED = os.environ.get("ATP_AOKP_ENABLED", "").lower() in ("1", "true", "yes")
AOKP_BASE_URL = os.environ.get("ATP_AOKP_URL", "http://localhost:3002")


def enrich_context(incoming: dict[str, Any]) -> dict[str, Any]:
    """Optionally enrich an incoming bridge request with AOKP knowledge.

    Adds an ``aokp_context`` key to the returned dict if enrichment
    succeeds. Never mutates ``text``, ``model``, or ``context``.
    Returns the incoming dict unchanged if AOKP is disabled or unavailable.

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
    enriched["aokp_context"] = {
        "context_text": result["context_text"],
        "hit_count": len(result["hits"]),
        "manifest": result["manifest"],
    }
    return enriched
