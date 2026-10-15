"""LLM provider abstraction for ATP synthesis generators.

Why this exists: AOKP `synthesizer.ts:73-150` calls an LLM in a loop
(synthesize → quality-check → retry). The ATP port needs the same
capability but without binding the generators package to the bridge
dispatch chain — that creates a circular import (bridge_server →
generators → bridge_request → bridge_server).

Design: the generators package owns the *interface* (an LlmCall
callable), the *default implementation* lives one indirection away
in `_default_provider()` (lazy-imports bridge_request the first
time it runs), and tests can `set_llm_provider(fake)` to swap in
a deterministic stub.

Provider contract:
    def my_provider(prompt: str, model: str | None = None) -> str:
        '''Return the LLM's text response. Raise LlmError on failure.'''

A provider MAY also accept a keyword `system` (a system prompt kept separate from the user prompt, as AOKP's synthesis does). `call_llm(prompt, model, system=...)`
passes it only to a provider that declares it (or **kwargs); for any other provider the system text is put in front of the prompt, so existing providers keep working.
"""

from __future__ import annotations

import inspect
import os
from typing import Callable, Protocol

# Empty = let bridge_request apply the bridge's own default (anthropic / DEFAULT_MODEL in bridge/openclaw_bridge.py), so there is ONE source for it.
# Never default to a provider the executor has no handler for: "ollama/..." resolved to provider "ollama", fell through to the deferred SSH stub and
# every llm_mode=real call without an explicit model failed (Ollama adapter removed in 2.6.0; no local LLM on macOS, Global_Mac_No_Ollama_Rule).
DEFAULT_MODEL = os.environ.get("ATP_GENERATORS_DEFAULT_MODEL", "")


class LlmError(RuntimeError):
    """Raised by an LLM provider when the call fails for any reason
    (non-200, network, malformed response, missing model)."""


class LlmCall(Protocol):
    def __call__(self, prompt: str, model: str | None = None) -> str: ...


def _default_provider(prompt: str, model: str | None = None, system: str | None = None) -> str:
    """Production provider — delegates to ATP `bridge_request` (`system` travels as the request's `context`, which the cloud adapters send as the system prompt).

    Lazy-imports bridge_request so generators/__init__.py can be loaded
    inside the bridge process (which imports generators) without the
    circular dependency.
    """
    # Imported here, not at module load, to break the cycle described
    # in the module docstring.
    from bridge.openclaw_bridge import bridge_request, BridgeError

    payload: dict = {"text": prompt, "model": model or DEFAULT_MODEL}
    if system:
        payload["context"] = system
    try:
        result = bridge_request(payload)
    except BridgeError as e:
        raise LlmError(f"bridge_request failed: {e}") from e

    # bridge_request returns ATP's CLI-execution-shaped result. The LLM
    # text lives in `stdout` (verified live 2026-05-03, when the default was
    # the since-removed ollama/qwen3:8b provider — keys: execution_id, request_id, product,
    # selected_provider, selected_node, command, exit_code, stdout,
    # stderr, status, source_stage, notes, bridge, ollama_manifest,
    # ollama_routing). Status field is "succeeded" on success.
    if isinstance(result, dict):
        # Refuse non-success even if stdout has content (avoid silent
        # delivery of partial / error stdout).
        status = str(result.get("status", "")).lower()
        if status and status not in {"succeeded", "ok", "success"}:
            stderr = str(result.get("stderr") or "")[:200]
            raise LlmError(
                f"bridge_request status={status!r} exit_code={result.get('exit_code')} "
                f"stderr={stderr}"
            )
        for key in ("stdout", "text", "answer", "output", "response"):
            v = result.get(key)
            if isinstance(v, str) and v.strip():
                return v
        manifest = result.get("manifest") or result.get("ollama_manifest") or {}
        if isinstance(manifest, dict) and isinstance(manifest.get("text"), str):
            return manifest["text"]
    raise LlmError(f"bridge_request returned unexpected shape: {type(result).__name__}")


_provider: LlmCall = _default_provider


def set_llm_provider(callable_: LlmCall) -> None:
    """Install a custom provider — primarily for tests + dependency
    injection from non-default hosts (e.g. an external evaluator that
    routes through a different LLM)."""
    global _provider
    _provider = callable_


def reset_llm_provider() -> None:
    """Restore the default (bridge_request) provider."""
    global _provider
    _provider = _default_provider


def _accepts_system(provider: Callable[..., str]) -> bool:
    try:
        params = inspect.signature(provider).parameters
    except (TypeError, ValueError):
        return False
    return "system" in params or any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())


def call_llm(prompt: str, model: str | None = None, system: str | None = None) -> str:
    """Single-shot LLM call. Raises LlmError on any failure. Without `system` it behaves exactly as before."""
    if not system:
        return _provider(prompt, model)
    if _accepts_system(_provider):
        return _provider(prompt, model, system=system)  # type: ignore[call-arg]
    return _provider(f"{system}\n\n{prompt}", model)
