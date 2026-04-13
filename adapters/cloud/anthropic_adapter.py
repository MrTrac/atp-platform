"""ATP Anthropic cloud adapter — cloud LLM inference via Anthropic Messages API.

Same provider-agnostic interface as the Ollama adapter:
- Same input contract: {model, prompt/messages, context, options}
- Same output structure: {status, route_type, provider, model, output, manifest, ...}

Differences:
- route_type = "cloud"
- escalation_triggered = True (cloud calls are escalation by design)
- Requires ANTHROPIC_API_KEY environment variable
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 120


class AnthropicAdapterError(ValueError):
    """Raised when the Anthropic adapter cannot fulfil a request."""


def _get_api_key() -> str | None:
    """Read API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")


def _validate_input(request: dict[str, Any]) -> None:
    """Execution contract: require model + prompt/messages."""
    if not request.get("model"):
        raise AnthropicAdapterError("Execution contract violated: 'model' is required.")
    if not request.get("prompt") and not request.get("messages"):
        raise AnthropicAdapterError(
            "Execution contract violated: 'prompt' or 'messages' is required."
        )


def _build_payload(request: dict[str, Any]) -> dict[str, Any]:
    """Build the Anthropic Messages API payload."""
    messages: list[dict[str, str]] = []
    if request.get("messages"):
        messages = list(request["messages"])
    elif request.get("prompt"):
        messages = [{"role": "user", "content": str(request["prompt"])}]

    payload: dict[str, Any] = {
        "model": request["model"],
        "messages": messages,
        "max_tokens": request.get("options", {}).get("max_tokens", DEFAULT_MAX_TOKENS),
    }

    if request.get("context"):
        payload["system"] = str(request["context"])

    if request.get("options"):
        opts = request["options"]
        if "temperature" in opts:
            payload["temperature"] = opts["temperature"]
        if "top_p" in opts:
            payload["top_p"] = opts["top_p"]

    return payload


def _validate_completion(response_body: dict[str, Any]) -> bool:
    """Completion validation: non-empty, non-error response."""
    content_blocks = response_body.get("content", [])
    for block in content_blocks:
        if block.get("type") == "text" and (block.get("text") or "").strip():
            return True
    return False


def _extract_output(response_body: dict[str, Any]) -> str:
    """Extract text from Anthropic response content blocks."""
    parts: list[str] = []
    for block in response_body.get("content", []):
        if block.get("type") == "text":
            text = (block.get("text") or "").strip()
            if text:
                parts.append(text)
    return "\n\n".join(parts)


def _extract_token_count(response_body: dict[str, Any]) -> int | None:
    """Extract token count from Anthropic usage field."""
    usage = response_body.get("usage")
    if usage:
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        return int(input_tokens) + int(output_tokens)
    return None


def execute_anthropic(
    request: dict[str, Any],
    *,
    api_url: str = ANTHROPIC_API_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Execute an LLM inference request via Anthropic and return structured result.

    Parameters
    ----------
    request : dict
        Must contain ``model`` and either ``prompt`` or ``messages``.
        Optional: ``context`` (system prompt), ``options`` (temperature, max_tokens, etc.).
    api_url : str
        Anthropic Messages API URL.
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    dict
        Structured result with status, output, manifest, and routing metadata.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    # Check API key first
    api_key = _get_api_key()
    if not api_key:
        return _error_result(
            "ANTHROPIC_API_KEY environment variable is not set.",
            request.get("model") or DEFAULT_MODEL,
            timestamp,
            start_time,
        )

    # Execution contract validation
    try:
        _validate_input(request)
    except AnthropicAdapterError as exc:
        return _error_result(str(exc), request.get("model"), timestamp, start_time)

    payload = _build_payload(request)

    try:
        http_request = Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
            },
            method="POST",
        )
        with urlopen(http_request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            body = json.loads(raw)
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return _error_result(
            f"Anthropic request failed: {exc}",
            request["model"],
            timestamp,
            start_time,
        )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    # Completion validation
    is_valid = _validate_completion(body)
    output_text = _extract_output(body)

    # Artifact manifest with cost tracking
    token_count = _extract_token_count(body)
    usage = body.get("usage", {})
    input_tokens = int(usage.get("input_tokens", 0))
    output_tokens = int(usage.get("output_tokens", 0))
    # Claude Sonnet 4: $3/MTok input, $15/MTok output (approximate)
    cost_usd = (input_tokens * 3 + output_tokens * 15) / 1_000_000

    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": token_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completion_validated": is_valid,
        "cost_usd": round(cost_usd, 6),
    }

    error_msg = None if is_valid else "Completion validation failed: empty response."

    # Structured result — same shape as Ollama adapter
    result: dict[str, Any] = {
        "status": "success" if is_valid else "failed",
        "route_type": "cloud",
        "provider": "anthropic",
        "model": request["model"],
        "output": output_text,
        "manifest": manifest,
        "escalation_triggered": True,
        "error": error_msg,
    }
    if error_msg:
        from core.error_codes import classify_error, to_dict
        result["error_classification"] = to_dict(classify_error(error_msg))
    return result


def _error_result(
    message: str,
    model: str | None,
    timestamp: str,
    start_time: float,
) -> dict[str, Any]:
    """Build a structured error result."""
    from core.error_codes import classify_error, to_dict

    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    return {
        "status": "failed",
        "route_type": "cloud",
        "provider": "anthropic",
        "model": model or "unknown",
        "output": "",
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": elapsed_ms,
            "token_count": None,
            "completion_validated": False,
            "cost_usd": 0.0,
        },
        "escalation_triggered": True,
        "error": message,
        "error_classification": to_dict(classify_error(message)),
    }
