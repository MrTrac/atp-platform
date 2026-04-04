"""ATP Ollama adapter — local LLM inference via Ollama API.

Addresses 5 pilot v1 gaps:
1. Execution contract: validates input before calling Ollama
2. Artifact manifest: captures model, timestamp, response_time_ms, token_count, status
3. Completion validation: checks response is non-empty and valid
4. Routing metadata: route_type, provider, escalation_triggered
5. Freeze/handoff protocol: returns JSON-serializable structured result
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT_SECONDS = 120


class OllamaAdapterError(ValueError):
    """Raised when the Ollama adapter cannot fulfil a request."""


def _validate_input(request: dict[str, Any]) -> None:
    """Gap 1 — Execution contract: require model, prompt/messages, context."""
    if not request.get("model"):
        raise OllamaAdapterError("Execution contract violated: 'model' is required.")
    if not request.get("prompt") and not request.get("messages"):
        raise OllamaAdapterError(
            "Execution contract violated: 'prompt' or 'messages' is required."
        )


def _build_payload(request: dict[str, Any]) -> dict[str, Any]:
    """Build the Ollama /api/chat JSON payload."""
    messages: list[dict[str, str]] = []
    if request.get("messages"):
        messages = list(request["messages"])
    elif request.get("prompt"):
        messages = [{"role": "user", "content": str(request["prompt"])}]

    if request.get("context"):
        system_msg = {"role": "system", "content": str(request["context"])}
        messages.insert(0, system_msg)

    payload: dict[str, Any] = {
        "model": request["model"],
        "messages": messages,
        "stream": False,
    }
    if request.get("options"):
        payload["options"] = request["options"]
    return payload


def _validate_completion(response_body: dict[str, Any]) -> bool:
    """Gap 3 — Completion validation: non-empty, non-error response."""
    message = response_body.get("message", {})
    content = (message.get("content") or "").strip()
    return bool(content)


def _extract_token_count(response_body: dict[str, Any]) -> int | None:
    """Extract token count from Ollama response if available."""
    eval_count = response_body.get("eval_count")
    prompt_count = response_body.get("prompt_eval_count")
    if eval_count is not None:
        total = int(eval_count)
        if prompt_count is not None:
            total += int(prompt_count)
        return total
    return None


def execute_ollama(
    request: dict[str, Any],
    *,
    base_url: str = OLLAMA_BASE_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Execute an LLM inference request via Ollama and return structured result.

    Parameters
    ----------
    request : dict
        Must contain ``model`` and either ``prompt`` or ``messages``.
        Optional: ``context`` (system prompt), ``options`` (Ollama model params).
    base_url : str
        Ollama server URL (default ``http://127.0.0.1:11434``).
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    dict
        Structured result with status, output, manifest, and routing metadata.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    # Gap 1 — Execution contract
    try:
        _validate_input(request)
    except OllamaAdapterError as exc:
        return _error_result(str(exc), request.get("model"), timestamp, start_time)

    payload = _build_payload(request)
    url = f"{base_url}/api/chat"

    try:
        http_request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(http_request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            body = json.loads(raw)
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return _error_result(
            f"Ollama request failed: {exc}",
            request["model"],
            timestamp,
            start_time,
        )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    # Gap 3 — Completion validation
    is_valid = _validate_completion(body)
    output_text = (body.get("message", {}).get("content") or "").strip()

    # Gap 2 — Artifact manifest
    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": _extract_token_count(body),
        "completion_validated": is_valid,
    }

    # Gap 5 — Freeze/handoff: structured, JSON-serializable result
    return {
        "status": "success" if is_valid else "failed",
        # Gap 4 — Routing metadata
        "route_type": "local",
        "provider": "ollama",
        "model": request["model"],
        "output": output_text,
        "manifest": manifest,
        "escalation_triggered": False,
        "error": None if is_valid else "Completion validation failed: empty response.",
    }


def _error_result(
    message: str,
    model: str | None,
    timestamp: str,
    start_time: float,
) -> dict[str, Any]:
    """Build a structured error result."""
    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    return {
        "status": "failed",
        "route_type": "local",
        "provider": "ollama",
        "model": model or "unknown",
        "output": "",
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "token_count": None,
            "completion_validated": False,
        },
        "escalation_triggered": False,
        "error": message,
    }
