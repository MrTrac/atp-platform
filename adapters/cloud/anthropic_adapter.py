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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.pricing import calculate_cost
from core.retry import with_retry


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
    """Build the Anthropic Messages API payload.

    Supports v1.9.0 agentic capabilities:
    - ``tools`` — function/tool definitions for tool use
    - ``tool_choice`` — control how/when tools are used
    - ``json_mode`` — when true, append JSON-only system instruction
    - vision — image inputs are passed through messages naturally (Anthropic
      content blocks support `{"type": "image", "source": {...}}`)
    """
    messages: list[dict[str, Any]] = []
    if request.get("messages"):
        messages = list(request["messages"])
    elif request.get("prompt"):
        messages = [{"role": "user", "content": str(request["prompt"])}]

    payload: dict[str, Any] = {
        "model": request["model"],
        "messages": messages,
        "max_tokens": request.get("options", {}).get("max_tokens", DEFAULT_MAX_TOKENS),
    }

    # System prompt (v1.0)
    system_prompt = request.get("context", "")
    # JSON mode: append instruction to system prompt
    if request.get("json_mode"):
        json_instruction = "Respond ONLY with valid JSON. No markdown, no commentary. Pure JSON output only."
        system_prompt = f"{system_prompt}\n\n{json_instruction}".strip() if system_prompt else json_instruction
    if system_prompt:
        payload["system"] = system_prompt

    # Tool use (v1.9.0)
    if request.get("tools"):
        payload["tools"] = list(request["tools"])
        if request.get("tool_choice"):
            payload["tool_choice"] = request["tool_choice"]

    if request.get("options"):
        opts = request["options"]
        if "temperature" in opts:
            payload["temperature"] = opts["temperature"]
        if "top_p" in opts:
            payload["top_p"] = opts["top_p"]

    return payload


def _validate_completion(response_body: dict[str, Any]) -> bool:
    """Completion validation: non-empty text or tool_use block."""
    content_blocks = response_body.get("content", [])
    for block in content_blocks:
        block_type = block.get("type")
        if block_type == "text" and (block.get("text") or "").strip():
            return True
        # Tool use is also a valid completion (model decided to call a tool)
        if block_type == "tool_use" and block.get("name"):
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


def _extract_tool_calls(response_body: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract tool_use blocks from Anthropic response."""
    tool_calls: list[dict[str, Any]] = []
    for block in response_body.get("content", []):
        if block.get("type") == "tool_use":
            tool_calls.append({
                "id": block.get("id", ""),
                "name": block.get("name", ""),
                "input": block.get("input", {}),
            })
    return tool_calls


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

    # Check API key: request body → environment variable
    api_key = request.get("api_key") or _get_api_key()
    if not api_key:
        return _error_result(
            "ANTHROPIC_API_KEY not set. Provide api_key in request or set the environment variable.",
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

    # Per-model timeout override
    from core.config import get_timeout_for_model
    effective_timeout = get_timeout_for_model(request["model"], timeout)

    def _do_request() -> dict[str, Any]:
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
        with urlopen(http_request, timeout=effective_timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)

    try:
        body = with_retry(_do_request)
    except HTTPError as exc:
        # Capture the actual error body from Anthropic for diagnostics
        error_body = ""
        try:
            error_body = exc.read().decode("utf-8", errors="replace")
            error_detail = json.loads(error_body).get("error", {}).get("message", "")
        except Exception:
            error_detail = error_body[:500] if error_body else ""
        detail_suffix = f" — {error_detail}" if error_detail else ""
        return _error_result(
            f"Anthropic API error {exc.code}: {exc.reason}{detail_suffix}",
            request["model"],
            timestamp,
            start_time,
        )
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

    # Artifact manifest with cost tracking (per-model pricing from registry)
    token_count = _extract_token_count(body)
    usage = body.get("usage", {})
    input_tokens = int(usage.get("input_tokens", 0))
    output_tokens = int(usage.get("output_tokens", 0))
    cost_usd = calculate_cost(
        request["model"], input_tokens, output_tokens, provider="anthropic"
    )

    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": token_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completion_validated": is_valid,
        "cost_usd": cost_usd,
    }

    # Tool calls (v1.9.0)
    tool_calls = _extract_tool_calls(body)
    stop_reason = body.get("stop_reason")

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
    if tool_calls:
        result["tool_calls"] = tool_calls
        manifest["stop_reason"] = stop_reason
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


# ---------------------------------------------------------------------------
# Streaming (v2.0.0)
# ---------------------------------------------------------------------------

def execute_anthropic_stream(
    request: dict[str, Any],
    *,
    api_url: str = ANTHROPIC_API_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    abort_event: "threading.Event | None" = None,
):
    """Stream LLM inference via Anthropic Messages API with SSE.

    Yields tuples of (event_kind, data) where event_kind is one of:
    - "token"     — incremental text chunk (str)
    - "tool_call" — complete tool_use block (dict)
    - "manifest"  — final manifest (dict) emitted at end
    - "error"     — error message (dict with message + error_code)
    - "aborted"   — request aborted by client (dict with reason)

    Uses Anthropic's stream=True with SSE responses.
    """
    import threading  # noqa: F401

    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = request.get("api_key") or _get_api_key()
    if not api_key:
        yield ("error", {"message": "ANTHROPIC_API_KEY not set", "error_code": "contract_violation"})
        return

    try:
        _validate_input(request)
    except AnthropicAdapterError as exc:
        yield ("error", {"message": str(exc), "error_code": "contract_violation"})
        return

    payload = _build_payload(request)
    payload["stream"] = True

    from core.config import get_timeout_for_model
    effective_timeout = get_timeout_for_model(request["model"], timeout)

    http_request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "Accept": "text/event-stream",
        },
        method="POST",
    )

    accumulated_text: list[str] = []
    accumulated_tool_calls: list[dict[str, Any]] = []
    current_tool_input: list[str] = []
    current_tool: dict[str, Any] | None = None
    input_tokens = 0
    output_tokens = 0
    stop_reason: str | None = None

    try:
        with urlopen(http_request, timeout=effective_timeout) as resp:
            for raw_line in resp:
                if abort_event is not None and abort_event.is_set():
                    yield ("aborted", {"reason": "client_cancelled"})
                    return
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if not data_str or data_str == "[DONE]":
                    continue
                try:
                    event_obj = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event_type = event_obj.get("type", "")

                if event_type == "content_block_delta":
                    delta = event_obj.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            accumulated_text.append(text)
                            yield ("token", {"text": text})
                    elif delta.get("type") == "input_json_delta":
                        # Partial tool input JSON
                        current_tool_input.append(delta.get("partial_json", ""))

                elif event_type == "content_block_start":
                    block = event_obj.get("content_block", {})
                    if block.get("type") == "tool_use":
                        current_tool = {
                            "id": block.get("id", ""),
                            "name": block.get("name", ""),
                            "input": {},
                        }
                        current_tool_input = []

                elif event_type == "content_block_stop":
                    if current_tool is not None:
                        try:
                            current_tool["input"] = json.loads("".join(current_tool_input)) if current_tool_input else {}
                        except json.JSONDecodeError:
                            current_tool["input"] = {"_raw": "".join(current_tool_input)}
                        accumulated_tool_calls.append(current_tool)
                        yield ("tool_call", dict(current_tool))
                        current_tool = None

                elif event_type == "message_delta":
                    usage = event_obj.get("usage", {})
                    if "output_tokens" in usage:
                        output_tokens = int(usage["output_tokens"])
                    delta = event_obj.get("delta", {})
                    if delta.get("stop_reason"):
                        stop_reason = delta["stop_reason"]

                elif event_type == "message_start":
                    msg = event_obj.get("message", {})
                    usage = msg.get("usage", {})
                    if "input_tokens" in usage:
                        input_tokens = int(usage["input_tokens"])

    except HTTPError as exc:
        error_body = ""
        try:
            error_body = exc.read().decode("utf-8", errors="replace")
            error_detail = json.loads(error_body).get("error", {}).get("message", "")
        except Exception:
            error_detail = error_body[:500] if error_body else ""
        from core.error_codes import classify_error
        msg = f"Anthropic API error {exc.code}: {exc.reason}"
        if error_detail:
            msg = f"{msg} — {error_detail}"
        yield ("error", {"message": msg, "error_code": classify_error(msg).code})
        return
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        from core.error_codes import classify_error
        msg = f"Anthropic stream failed: {exc}"
        yield ("error", {"message": msg, "error_code": classify_error(msg).code})
        return

    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    cost_usd = calculate_cost(request["model"], input_tokens, output_tokens, provider="anthropic")
    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": input_tokens + output_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completion_validated": bool(accumulated_text or accumulated_tool_calls),
        "cost_usd": cost_usd,
        "stop_reason": stop_reason,
        "tool_calls_count": len(accumulated_tool_calls),
    }
    yield ("manifest", {"manifest": manifest})
