"""Map ATP routing results to execution adapters for M6.

Provider dispatch is registry-driven via EXECUTOR_MAP rather than
hardcoded conditionals, allowing new providers to be registered
without modifying this module's dispatch logic.
"""

from __future__ import annotations

from typing import Any, Callable

from adapters.subprocess.local_exec_adapter import LocalExecutionError, execute_local
from adapters.ssh_remote.ssh_exec_adapter import execute_remote
from adapters.ollama.ollama_adapter import execute_ollama
from adapters.cloud.anthropic_adapter import execute_anthropic
from core.routing.escalation_policy import should_escalate


class ExecutionError(ValueError):
    """Raised when ATP cannot execute the selected route."""


DEFAULT_CLOUD_MODEL = "claude-sonnet-4-20250514"


def _build_llm_request(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Extract model, prompt, and context from ATP request for LLM adapters."""
    payload = normalized_request.get("payload", {})
    model = routing_result.get("selected_provider_model") or payload.get("model", "")

    prompt = payload.get("input_text") or payload.get("prompt", "")
    messages = payload.get("messages")
    context = payload.get("context") or payload.get("system_prompt", "")

    request: dict[str, Any] = {"model": model}
    if messages:
        request["messages"] = messages
    else:
        request["prompt"] = prompt
    if context:
        request["context"] = context
    if payload.get("options"):
        request["options"] = payload["options"]

    # Carry escalation fields for policy evaluation
    if payload.get("force_cloud") is True:
        request["force_cloud"] = True
    if payload.get("escalation_trigger"):
        request["escalation_trigger"] = payload["escalation_trigger"]
    # Pass through per-request API key for cloud providers
    if payload.get("api_key"):
        request["api_key"] = payload["api_key"]

    return request


def _normalize_adapter_result(result: dict[str, Any], adapter_path: str) -> dict[str, Any]:
    """Bridge an LLM adapter result to the shape output_normalizer expects."""
    succeeded = result.get("status") == "success"
    return {
        "exit_code": 0 if succeeded else 1,
        "stdout": result.get("output", ""),
        "stderr": result.get("error") or "",
        "command": [],
        "status": "completed" if succeeded else "failed",
        "notes": [
            f"Executed through {adapter_path}",
            f"provider={result.get('provider')}, model={result.get('model')}",
        ],
        "ollama_manifest": result.get("manifest"),
        "ollama_routing": {
            "route_type": result.get("route_type"),
            "provider": result.get("provider"),
            "escalation_triggered": result.get("escalation_triggered", False),
        },
    }


def _try_escalate(
    llm_request: dict[str, Any],
    local_result: dict[str, Any],
) -> dict[str, Any] | None:
    """Check escalation policy and call cloud adapter if triggered.

    Returns the cloud result (normalized) if escalated, or None if not.
    """
    do_escalate, reason = should_escalate(llm_request, local_result)
    if not do_escalate:
        return None

    cloud_request = dict(llm_request)
    cloud_request["model"] = cloud_request.get("model") or DEFAULT_CLOUD_MODEL
    # Always use the cloud default model for escalation
    cloud_request["model"] = DEFAULT_CLOUD_MODEL

    cloud_raw = execute_anthropic(cloud_request)
    normalized = _normalize_adapter_result(
        cloud_raw, "adapters/cloud/anthropic_adapter.py"
    )
    normalized["escalation"] = {
        "escalated": True,
        "reason": reason,
        "local_status": local_result.get("status"),
    }
    return normalized


# ---------------------------------------------------------------------------
# Adapter handler functions — one per provider
# ---------------------------------------------------------------------------

def _handle_non_llm(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Handle non-LLM local subprocess execution."""
    try:
        return execute_local(normalized_request)
    except LocalExecutionError as exc:
        raise ExecutionError(str(exc)) from exc


def _handle_ollama(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Handle Ollama local LLM execution with escalation policy."""
    llm_request = _build_llm_request(normalized_request, routing_result)
    raw_result = execute_ollama(llm_request)

    escalated = _try_escalate(llm_request, raw_result)
    if escalated is not None:
        return escalated

    return _normalize_adapter_result(
        raw_result, "adapters/ollama/ollama_adapter.py"
    )


def _handle_anthropic(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Handle Anthropic cloud LLM execution."""
    llm_request = _build_llm_request(normalized_request, routing_result)
    raw_result = execute_anthropic(llm_request)
    return _normalize_adapter_result(
        raw_result, "adapters/cloud/anthropic_adapter.py"
    )


# ---------------------------------------------------------------------------
# Registry-driven dispatch map
# ---------------------------------------------------------------------------

ExecutorHandler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

EXECUTOR_MAP: dict[str, ExecutorHandler] = {
    "non_llm_execution": _handle_non_llm,
    "ollama": _handle_ollama,
    "anthropic": _handle_anthropic,
}


def register_executor(provider: str, handler: ExecutorHandler) -> None:
    """Register a new provider handler at runtime."""
    EXECUTOR_MAP[provider] = handler


def invoke_executor(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Invoke the adapter mapped from the selected provider."""

    provider = routing_result.get("selected_provider")
    node = routing_result.get("selected_node")

    handler = EXECUTOR_MAP.get(provider or "")
    if handler is not None:
        return handler(normalized_request, routing_result)

    # Fallback: unknown provider with a node → attempt SSH remote (deferred)
    if provider and node:
        return execute_remote(normalized_request)

    raise ExecutionError("Unsupported execution route.")
