"""ATP AOKP adapter — knowledge retrieval via AOKP Phase 1 HTTP APIs.

Provides context enrichment by querying the AOKP knowledge platform.
AOKP is a context source, not an executor — results enrich request
context before execution, never replace execution output.

Follows the Ollama adapter pattern: stdlib urllib, structured error
results, manifest metadata on every call.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


AOKP_BASE_URL = "http://localhost:3002"
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_TOP_K = 3


class AokpAdapterError(ValueError):
    """Raised when the AOKP adapter cannot fulfil a request."""


def check_health(
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = 3,
) -> dict[str, Any]:
    """Check if AOKP is reachable and return status.

    Returns
    -------
    dict
        ``{"status": "ok", ...}`` when reachable,
        ``{"status": "unavailable", ...}`` otherwise. Never raises.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    url = f"{base_url}/api/phase1/status"

    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return {
            "status": "ok",
            "provider": "aokp",
            "aokp_status": body,
            "timestamp": timestamp,
        }
    except (URLError, OSError, json.JSONDecodeError, ValueError):
        return {
            "status": "unavailable",
            "provider": "aokp",
            "aokp_status": None,
            "timestamp": timestamp,
        }


def query_knowledge(
    request: dict[str, Any],
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Query AOKP retrieval engine for knowledge context.

    Parameters
    ----------
    request : dict
        Must contain ``query``. Optional: ``filters``, ``top_k``.

    Returns
    -------
    dict
        Structured result with hits, context_text, and manifest.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    query = (request.get("query") or "").strip()
    if not query:
        return _error_result("'query' is required and must be non-empty.", timestamp, start_time)

    top_k = request.get("top_k", DEFAULT_TOP_K)
    payload: dict[str, Any] = {"query": query, "topK": top_k}
    if request.get("filters"):
        payload["filters"] = request["filters"]

    url = f"{base_url}/api/search"

    try:
        http_req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(http_req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return _error_result(f"AOKP search request failed: {exc}", timestamp, start_time)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    hits = body.get("hits", [])
    context_text = _format_hits_as_context(hits)

    return {
        "status": "success" if hits else "empty",
        "provider": "aokp",
        "hits": hits,
        "total": body.get("total", len(hits)),
        "context_text": context_text,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "hit_count": len(hits),
            "query": query,
            "mode": body.get("mode", "unknown"),
        },
        "error": None,
    }


def query_graph(
    request: dict[str, Any],
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Query AOKP knowledge graph for entities and relations.

    Parameters
    ----------
    request : dict
        Should contain ``term`` or ``entity_id``.

    Returns
    -------
    dict
        Structured result with entities, relations, and manifest.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    term = (request.get("term") or "").strip()
    entity_id = (request.get("entity_id") or "").strip()
    if not term and not entity_id:
        return _graph_error_result("'term' or 'entity_id' is required.", timestamp, start_time)

    payload: dict[str, Any] = {"action": "query"}
    if term:
        payload["term"] = term
    if entity_id:
        payload["entityId"] = entity_id

    url = f"{base_url}/api/graph"

    try:
        http_req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(http_req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return _graph_error_result(f"AOKP graph request failed: {exc}", timestamp, start_time)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    entities = body.get("entities", [])
    relations = body.get("relations", [])

    return {
        "status": "success" if entities else "empty",
        "provider": "aokp",
        "entities": entities,
        "relations": relations,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "entity_count": len(entities),
            "relation_count": len(relations),
        },
        "error": None,
    }


def _format_hits_as_context(hits: list[dict[str, Any]]) -> str:
    """Format retrieval hits as a text block for LLM context injection."""
    if not hits:
        return ""
    lines: list[str] = []
    for i, hit in enumerate(hits, 1):
        title = hit.get("title", "Untitled")
        snippet = hit.get("snippet", "")
        authority = hit.get("authoritySignal", "unknown")
        lines.append(f"[{i}] {title} (authority: {authority})")
        if snippet:
            lines.append(f"    {snippet[:300]}")
        lines.append("")
    return "\n".join(lines).strip()


def _error_result(message: str, timestamp: str, start_time: float) -> dict[str, Any]:
    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    return {
        "status": "failed",
        "provider": "aokp",
        "hits": [],
        "total": 0,
        "context_text": "",
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "hit_count": 0,
            "query": None,
            "mode": None,
        },
        "error": message,
    }


def _graph_error_result(message: str, timestamp: str, start_time: float) -> dict[str, Any]:
    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    return {
        "status": "failed",
        "provider": "aokp",
        "entities": [],
        "relations": [],
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "entity_count": 0,
            "relation_count": 0,
        },
        "error": message,
    }
