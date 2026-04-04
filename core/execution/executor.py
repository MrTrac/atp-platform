"""Map ATP routing results to execution adapters for M6."""

from __future__ import annotations

from typing import Any

from adapters.subprocess.local_exec_adapter import LocalExecutionError, execute_local
from adapters.ssh_remote.ssh_exec_adapter import execute_remote
from adapters.ollama.ollama_adapter import execute_ollama


class ExecutionError(ValueError):
    """Raised when ATP cannot execute the selected route."""


def _build_ollama_request(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Extract model, prompt, and context from ATP request for the Ollama adapter."""
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
    return request


def _normalize_ollama_result(result: dict[str, Any]) -> dict[str, Any]:
    """Bridge Ollama adapter result to the shape output_normalizer expects."""
    succeeded = result.get("status") == "success"
    return {
        "exit_code": 0 if succeeded else 1,
        "stdout": result.get("output", ""),
        "stderr": result.get("error") or "",
        "command": [],
        "status": "completed" if succeeded else "failed",
        "notes": [
            "Executed through adapters/ollama/ollama_adapter.py",
            f"provider={result.get('provider')}, model={result.get('model')}",
        ],
        "ollama_manifest": result.get("manifest"),
        "ollama_routing": {
            "route_type": result.get("route_type"),
            "provider": result.get("provider"),
            "escalation_triggered": result.get("escalation_triggered", False),
        },
    }


def invoke_executor(
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Invoke the adapter mapped from the selected provider and node."""

    provider = routing_result.get("selected_provider")
    node = routing_result.get("selected_node")

    if provider == "non_llm_execution" and node == "local_mac":
        try:
            return execute_local(normalized_request)
        except LocalExecutionError as exc:
            raise ExecutionError(str(exc)) from exc

    if provider == "ollama":
        ollama_request = _build_ollama_request(normalized_request, routing_result)
        raw_result = execute_ollama(ollama_request)
        return _normalize_ollama_result(raw_result)

    if provider and node:
        return execute_remote(normalized_request)

    raise ExecutionError("Unsupported execution route.")
