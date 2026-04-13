"""OpenClaw → ATP bridge: translate external requests into the ATP execution layer.

Accepts a JSON payload from the OpenClaw gateway (or CLI) and routes it
through the ATP executor to a local LLM via the Ollama adapter.

Usage (CLI):
    python3 bridge/openclaw_bridge.py '<json>'

    JSON fields:
        text    (required) — the prompt / task description
        model   (optional) — provider/model, e.g. "ollama/qwen3:14b"
        context (optional) — system prompt injected before the user message

Returns a JSON object on stdout with the full ATP execution result.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

from bridge.context_enrichment import enrich_context
from core.execution.executor import invoke_executor
from core.execution.output_normalizer import normalize_output


DEFAULT_MODEL = "qwen3:14b"
DEFAULT_PROVIDER = "ollama"


class BridgeError(ValueError):
    """Raised when the bridge cannot process the incoming request."""


def _parse_model_spec(model_spec: str) -> tuple[str, str]:
    """Parse 'provider/model' into (provider, model). Default provider: ollama."""
    if not model_spec:
        return DEFAULT_PROVIDER, DEFAULT_MODEL
    if "/" in model_spec:
        provider, _, model = model_spec.partition("/")
        provider = provider.strip() or DEFAULT_PROVIDER
        model = model.strip() or DEFAULT_MODEL
        return provider, model
    # Auto-detect provider from well-known model name prefixes
    name = model_spec.strip()
    if name.startswith("claude"):
        return "anthropic", name
    if name.startswith("gpt-") or name.startswith("o1") or name.startswith("o3"):
        return "openai", name
    return DEFAULT_PROVIDER, name


def bridge_request(incoming: dict[str, Any]) -> dict[str, Any]:
    """Transform an OpenClaw request into an ATP execution result.

    Parameters
    ----------
    incoming : dict
        Must contain ``text``.  Optional: ``model``, ``context``.

    Returns
    -------
    dict
        Full ATP execution result including manifest and routing metadata.
    """
    text = (incoming.get("text") or "").strip()
    if not text:
        raise BridgeError("'text' is required and must be non-empty.")

    provider, model = _parse_model_spec(incoming.get("model", ""))

    request_id = f"bridge-{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build the ATP normalized_request shape the executor expects
    normalized_request: dict[str, Any] = {
        "request_id": request_id,
        "product": "ATP",
        "request_type": "implementation",
        "execution_intent": "preview",
        "payload": {
            "input_text": text,
            "model": model,
        },
    }
    if incoming.get("context"):
        normalized_request["payload"]["context"] = str(incoming["context"])
    if incoming.get("options"):
        normalized_request["payload"]["options"] = incoming["options"]
    if incoming.get("api_key"):
        normalized_request["payload"]["api_key"] = incoming["api_key"]

    # Optional AOKP knowledge context enrichment
    enriched = enrich_context(incoming)
    if enriched.get("aokp_context"):
        knowledge_block = enriched["aokp_context"]["context_text"]
        existing_context = normalized_request["payload"].get("context", "")
        normalized_request["payload"]["context"] = (
            f"{existing_context}\n\n--- Knowledge Context (AOKP) ---\n{knowledge_block}"
            if existing_context else knowledge_block
        )

    # Build the routing result that steers the executor to the right adapter
    routing_result: dict[str, Any] = {
        "route_id": f"route-{request_id}",
        "request_id": request_id,
        "product": "ATP",
        "selected_provider": provider,
        "selected_node": "local_mac",
        "selected_provider_model": model,
        "execution_path": "local_ollama",
        "status": "selected",
        "reason_codes": ["bridge_direct_route"],
    }

    # Execute through the ATP executor layer
    raw_result = invoke_executor(normalized_request, routing_result)

    # Normalize into the standard ATP output shape
    normalized = normalize_output(
        raw_result=raw_result,
        request_id=request_id,
        product="ATP",
        routing_result=routing_result,
    )

    # Enrich with bridge metadata and ollama manifest
    normalized["bridge"] = {
        "source": "openclaw",
        "bridge_timestamp": timestamp,
        "original_model_spec": incoming.get("model", ""),
        "resolved_provider": provider,
        "resolved_model": model,
    }
    if raw_result.get("ollama_manifest"):
        normalized["ollama_manifest"] = raw_result["ollama_manifest"]
    if raw_result.get("ollama_routing"):
        normalized["ollama_routing"] = raw_result["ollama_routing"]
    if enriched.get("aokp_context"):
        normalized["aokp_enrichment"] = enriched["aokp_context"]["manifest"]

    return normalized


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: parse JSON arg, run bridge, print result."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: python3 bridge/openclaw_bridge.py '<json>'"}))
        sys.exit(1)

    try:
        incoming = json.loads(args[0])
    except (json.JSONDecodeError, IndexError) as exc:
        print(json.dumps({"error": f"Invalid JSON input: {exc}"}))
        sys.exit(1)

    try:
        result = bridge_request(incoming)
        print(json.dumps(result, indent=2))
    except BridgeError as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"error": f"Bridge execution failed: {exc}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
