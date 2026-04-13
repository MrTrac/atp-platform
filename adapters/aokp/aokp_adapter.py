"""ATP AOKP adapter — knowledge retrieval via AOKP v2.3.x HTTP APIs.

Provides context enrichment by querying the AOKP knowledge platform.
AOKP is a context source, not an executor — results enrich request
context before execution, never replace execution output.

Capabilities: knowledge_retrieval, graph_query, chat, graph_rag,
temporal_analysis, health_check.

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
    url = f"{base_url}/api/health"

    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return {
            "status": "ok",
            "provider": "aokp",
            "aokp_version": body.get("version", "unknown"),
            "aokp_health": body.get("status", "unknown"),
            "aokp_checks": body.get("checks", {}),
            "timestamp": timestamp,
        }
    except (URLError, OSError, json.JSONDecodeError, ValueError):
        return {
            "status": "unavailable",
            "provider": "aokp",
            "aokp_version": None,
            "aokp_health": None,
            "aokp_checks": None,
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


def query_chat(
    request: dict[str, Any],
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Query AOKP unified chat endpoint with NVI and pipeline routing.

    Parameters
    ----------
    request : dict
        Must contain ``query``. Optional: ``pipeline``, ``sessionId``.

    Returns
    -------
    dict
        Structured result with answer, sections, suggestions, citations.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    query = (request.get("query") or "").strip()
    if not query:
        return _chat_error_result("'query' is required.", timestamp, start_time)

    payload: dict[str, Any] = {"query": query}
    if request.get("pipeline"):
        payload["pipeline"] = request["pipeline"]
    if request.get("sessionId"):
        payload["sessionId"] = request["sessionId"]

    url = f"{base_url}/api/chat"

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
        return _chat_error_result(f"AOKP chat request failed: {exc}", timestamp, start_time)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return {
        "status": "success" if body.get("answer") else "empty",
        "provider": "aokp",
        "answer": body.get("answer", ""),
        "sections": body.get("sections", []),
        "suggestions": body.get("suggestions", []),
        "citations": body.get("citations", []),
        "locale": body.get("locale", "en"),
        "pipeline": body.get("pipeline", "unknown"),
        "qualityScore": body.get("qualityScore"),
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "query": query,
            "pipeline": body.get("pipeline", "unknown"),
            "locale": body.get("locale", "en"),
        },
        "error": None,
    }


def query_graph_rag(
    request: dict[str, Any],
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Query AOKP GraphRAG endpoint for community-based search.

    Parameters
    ----------
    request : dict
        Must contain ``query``. Optional: ``mode`` (local/global).
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    query = (request.get("query") or "").strip()
    if not query:
        return _error_result("'query' is required.", timestamp, start_time)

    payload: dict[str, Any] = {"query": query}
    if request.get("mode"):
        payload["mode"] = request["mode"]

    url = f"{base_url}/api/graph-rag"

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
        return _error_result(f"AOKP graph-rag request failed: {exc}", timestamp, start_time)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return {
        "status": "success",
        "provider": "aokp",
        "result": body,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "query": query,
            "mode": request.get("mode", "local"),
        },
        "error": None,
    }


def query_temporal(
    request: dict[str, Any],
    *,
    base_url: str = AOKP_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Query AOKP temporal causal knowledge graph.

    Parameters
    ----------
    request : dict
        Must contain ``query``. Optional: ``direction`` (forward/root_cause).
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    query = (request.get("query") or "").strip()
    if not query:
        return _error_result("'query' is required.", timestamp, start_time)

    payload: dict[str, Any] = {"query": query}
    if request.get("direction"):
        payload["direction"] = request["direction"]

    url = f"{base_url}/api/temporal-graph"

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
        return _error_result(f"AOKP temporal-graph request failed: {exc}", timestamp, start_time)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return {
        "status": "success",
        "provider": "aokp",
        "result": body,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "query": query,
            "direction": request.get("direction", "forward"),
        },
        "error": None,
    }


def _chat_error_result(message: str, timestamp: str, start_time: float) -> dict[str, Any]:
    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    return {
        "status": "failed",
        "provider": "aokp",
        "answer": "",
        "sections": [],
        "suggestions": [],
        "citations": [],
        "locale": None,
        "pipeline": None,
        "qualityScore": None,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "query": None,
            "pipeline": None,
            "locale": None,
        },
        "error": message,
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
