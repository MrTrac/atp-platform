"""ATP OpenAI cloud adapter — cloud LLM inference via OpenAI Chat Completions API.

Same provider-agnostic interface as the Ollama and Anthropic adapters:
- Same input contract: {model, prompt/messages, context, options, api_key}
- Same output structure: {status, route_type, provider, model, output, manifest, ...}

Differences:
- route_type = "cloud"
- escalation_triggered = True (cloud calls are escalation by design)
- Requires OPENAI_API_KEY environment variable (or api_key in request)
- Uses Authorization: Bearer header

Supports: gpt-4, gpt-4o, gpt-5, o1, o3 model families.
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


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 120


class OpenAIAdapterError(ValueError):
    """Raised when the OpenAI adapter cannot fulfil a request."""


def _get_api_key() -> str | None:
    """Read API key from environment."""
    return os.environ.get("OPENAI_API_KEY")


def _validate_input(request: dict[str, Any]) -> None:
    """Execution contract: require model + prompt/messages."""
    if not request.get("model"):
        raise OpenAIAdapterError("Execution contract violated: 'model' is required.")
    if not request.get("prompt") and not request.get("messages"):
        raise OpenAIAdapterError(
            "Execution contract violated: 'prompt' or 'messages' is required."
        )


def _build_payload(request: dict[str, Any]) -> dict[str, Any]:
    """Build the OpenAI Chat Completions API payload.

    Supports v1.9.0 agentic capabilities:
    - ``tools`` — function/tool definitions for tool use
    - ``tool_choice`` — control how/when tools are used
    - ``json_mode`` — when true, sets response_format = {"type": "json_object"}
    - vision — image inputs are passed through messages naturally (OpenAI
      content parts support `{"type": "image_url", "image_url": {...}}`)
    """
    messages: list[dict[str, Any]] = []

    # System prompt first if context provided
    if request.get("context"):
        messages.append({"role": "system", "content": str(request["context"])})

    if request.get("messages"):
        messages.extend(list(request["messages"]))
    elif request.get("prompt"):
        messages.append({"role": "user", "content": str(request["prompt"])})

    payload: dict[str, Any] = {
        "model": request["model"],
        "messages": messages,
    }

    opts = request.get("options") or {}
    # o1/o3 reasoning models use max_completion_tokens, others use max_tokens
    model = request["model"]
    if model.startswith("o1") or model.startswith("o3"):
        payload["max_completion_tokens"] = opts.get("max_tokens", DEFAULT_MAX_TOKENS)
    else:
        payload["max_tokens"] = opts.get("max_tokens", DEFAULT_MAX_TOKENS)

    if "temperature" in opts:
        payload["temperature"] = opts["temperature"]
    if "top_p" in opts:
        payload["top_p"] = opts["top_p"]

    # JSON mode (v1.9.0)
    if request.get("json_mode"):
        payload["response_format"] = {"type": "json_object"}

    # Tool use (v1.9.0)
    if request.get("tools"):
        payload["tools"] = list(request["tools"])
        if request.get("tool_choice"):
            payload["tool_choice"] = request["tool_choice"]

    return payload


def _validate_completion(response_body: dict[str, Any]) -> bool:
    """Completion validation: non-empty content OR tool_calls present."""
    choices = response_body.get("choices", [])
    for choice in choices:
        message = choice.get("message", {})
        content = (message.get("content") or "").strip()
        if content:
            return True
        # Tool calls are also valid completion (model decided to call functions)
        if message.get("tool_calls"):
            return True
    return False


def _extract_output(response_body: dict[str, Any]) -> str:
    """Extract text from OpenAI response choices."""
    parts: list[str] = []
    for choice in response_body.get("choices", []):
        message = choice.get("message", {})
        content = (message.get("content") or "").strip()
        if content:
            parts.append(content)
    return "\n\n".join(parts)


def _extract_tool_calls(response_body: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract tool_calls from OpenAI response choices."""
    tool_calls: list[dict[str, Any]] = []
    for choice in response_body.get("choices", []):
        message = choice.get("message", {})
        for call in (message.get("tool_calls") or []):
            func = call.get("function", {})
            arguments_raw = func.get("arguments", "{}")
            # OpenAI returns arguments as a JSON string; parse for caller convenience
            try:
                import json as _json
                arguments = _json.loads(arguments_raw) if isinstance(arguments_raw, str) else arguments_raw
            except (ValueError, TypeError):
                arguments = {"_raw": arguments_raw}
            tool_calls.append({
                "id": call.get("id", ""),
                "name": func.get("name", ""),
                "input": arguments,
            })
    return tool_calls


def _extract_token_counts(response_body: dict[str, Any]) -> tuple[int | None, int, int]:
    """Extract (total, input, output) token counts from OpenAI usage field."""
    usage = response_body.get("usage")
    if not usage:
        return None, 0, 0
    input_tokens = int(usage.get("prompt_tokens", 0))
    output_tokens = int(usage.get("completion_tokens", 0))
    total = input_tokens + output_tokens
    return total, input_tokens, output_tokens


def execute_openai(
    request: dict[str, Any],
    *,
    api_url: str = OPENAI_API_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Execute an LLM inference request via OpenAI and return structured result.

    Parameters
    ----------
    request : dict
        Must contain ``model`` and either ``prompt`` or ``messages``.
        Optional: ``context`` (system prompt), ``options`` (temperature, max_tokens, etc.),
        ``api_key`` (overrides OPENAI_API_KEY env var).
    api_url : str
        OpenAI Chat Completions API URL.
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    dict
        Structured result with status, output, manifest, and routing metadata.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    # API key: request body → env var fallback
    api_key = request.get("api_key") or _get_api_key()
    if not api_key:
        return _error_result(
            "OPENAI_API_KEY not set. Provide api_key in request or set the environment variable.",
            request.get("model") or DEFAULT_MODEL,
            timestamp,
            start_time,
        )

    # Execution contract
    try:
        _validate_input(request)
    except OpenAIAdapterError as exc:
        return _error_result(str(exc), request.get("model"), timestamp, start_time)

    payload = _build_payload(request)

    # Per-model timeout override (e.g., o1 reasoning needs 600s)
    from core.config import get_timeout_for_model
    effective_timeout = get_timeout_for_model(request["model"], timeout)

    def _do_request() -> dict[str, Any]:
        http_request = Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urlopen(http_request, timeout=effective_timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)

    # Wrap in retry for 429/502/503/504/network errors
    try:
        body = with_retry(_do_request)
    except HTTPError as exc:
        error_body = ""
        try:
            error_body = exc.read().decode("utf-8", errors="replace")
            error_detail = json.loads(error_body).get("error", {}).get("message", "")
        except Exception:
            error_detail = error_body[:500] if error_body else ""
        detail_suffix = f" — {error_detail}" if error_detail else ""
        return _error_result(
            f"OpenAI HTTP {exc.code}: {exc.reason}{detail_suffix}",
            request["model"],
            timestamp,
            start_time,
        )
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        return _error_result(
            f"OpenAI request failed: {exc}",
            request["model"],
            timestamp,
            start_time,
        )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    is_valid = _validate_completion(body)
    output_text = _extract_output(body)
    total_tokens, input_tokens, output_tokens = _extract_token_counts(body)
    cost_usd = calculate_cost(request["model"], input_tokens, output_tokens, provider="openai")

    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": total_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completion_validated": is_valid,
        "cost_usd": cost_usd,
    }

    # Tool calls (v1.9.0)
    tool_calls = _extract_tool_calls(body)
    finish_reason = (body.get("choices") or [{}])[0].get("finish_reason")

    error_msg = None if is_valid else "Completion validation failed: empty response."

    result: dict[str, Any] = {
        "status": "success" if is_valid else "failed",
        "route_type": "cloud",
        "provider": "openai",
        "model": request["model"],
        "output": output_text,
        "manifest": manifest,
        "escalation_triggered": True,
        "error": error_msg,
    }
    if tool_calls:
        result["tool_calls"] = tool_calls
        manifest["finish_reason"] = finish_reason
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
        "provider": "openai",
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

def execute_openai_stream(
    request: dict[str, Any],
    *,
    api_url: str = OPENAI_API_URL,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    abort_event: "threading.Event | None" = None,
):
    """Stream LLM inference via OpenAI Chat Completions API with SSE.

    Yields tuples of (event_kind, data) where event_kind is one of:
    - "token"     — incremental text chunk (str)
    - "tool_call" — complete tool_call (dict) emitted when finish_reason=tool_calls
    - "manifest"  — final manifest (dict) emitted at end
    - "error"     — error message (dict with message + error_code)
    - "aborted"   — request aborted by client (dict with reason)
    """
    import threading  # noqa: F401

    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = request.get("api_key") or _get_api_key()
    if not api_key:
        yield ("error", {"message": "OPENAI_API_KEY not set", "error_code": "contract_violation"})
        return

    try:
        _validate_input(request)
    except OpenAIAdapterError as exc:
        yield ("error", {"message": str(exc), "error_code": "contract_violation"})
        return

    payload = _build_payload(request)
    payload["stream"] = True
    # OpenAI requires stream_options for usage tracking in streaming mode
    payload["stream_options"] = {"include_usage": True}

    from core.config import get_timeout_for_model
    effective_timeout = get_timeout_for_model(request["model"], timeout)

    http_request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream",
        },
        method="POST",
    )

    accumulated_text: list[str] = []
    # Tool call accumulators keyed by index (OpenAI streams tool_calls piecewise)
    tool_call_builders: dict[int, dict[str, Any]] = {}
    input_tokens = 0
    output_tokens = 0
    finish_reason: str | None = None

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
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                # Usage on final chunk when stream_options.include_usage=true
                usage = chunk.get("usage")
                if usage:
                    input_tokens = int(usage.get("prompt_tokens", 0))
                    output_tokens = int(usage.get("completion_tokens", 0))

                choices = chunk.get("choices", [])
                if not choices:
                    continue
                choice = choices[0]
                delta = choice.get("delta", {})

                # Text delta
                content_delta = delta.get("content")
                if content_delta:
                    accumulated_text.append(content_delta)
                    yield ("token", {"text": content_delta})

                # Tool call deltas — OpenAI streams these piecewise
                for tc in (delta.get("tool_calls") or []):
                    idx = tc.get("index", 0)
                    builder = tool_call_builders.setdefault(idx, {"id": "", "name": "", "_args_parts": []})
                    if tc.get("id"):
                        builder["id"] = tc["id"]
                    func = tc.get("function", {})
                    if func.get("name"):
                        builder["name"] = func["name"]
                    if func.get("arguments"):
                        builder["_args_parts"].append(func["arguments"])

                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]

    except HTTPError as exc:
        error_body = ""
        try:
            error_body = exc.read().decode("utf-8", errors="replace")
            error_detail = json.loads(error_body).get("error", {}).get("message", "")
        except Exception:
            error_detail = error_body[:500] if error_body else ""
        from core.error_codes import classify_error
        msg = f"OpenAI HTTP {exc.code}: {exc.reason}"
        if error_detail:
            msg = f"{msg} — {error_detail}"
        yield ("error", {"message": msg, "error_code": classify_error(msg).code})
        return
    except (URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        from core.error_codes import classify_error
        msg = f"OpenAI stream failed: {exc}"
        yield ("error", {"message": msg, "error_code": classify_error(msg).code})
        return

    # Finalize tool calls from accumulated deltas
    finalized_tool_calls: list[dict[str, Any]] = []
    for idx in sorted(tool_call_builders.keys()):
        b = tool_call_builders[idx]
        args_raw = "".join(b["_args_parts"])
        try:
            args = json.loads(args_raw) if args_raw else {}
        except json.JSONDecodeError:
            args = {"_raw": args_raw}
        finalized_tool_calls.append({"id": b["id"], "name": b["name"], "input": args})

    for tc in finalized_tool_calls:
        yield ("tool_call", dict(tc))

    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    cost_usd = calculate_cost(request["model"], input_tokens, output_tokens, provider="openai")
    manifest = {
        "timestamp": timestamp,
        "response_time_ms": elapsed_ms,
        "token_count": (input_tokens + output_tokens) if (input_tokens or output_tokens) else None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completion_validated": bool(accumulated_text or finalized_tool_calls),
        "cost_usd": cost_usd,
        "finish_reason": finish_reason,
        "tool_calls_count": len(finalized_tool_calls),
    }
    yield ("manifest", {"manifest": manifest})
