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
"""

from __future__ import annotations

import os
from typing import Callable, Protocol

DEFAULT_MODEL = os.environ.get("ATP_GENERATORS_DEFAULT_MODEL", "ollama/qwen3:8b")


class LlmError(RuntimeError):
    """Raised by an LLM provider when the call fails for any reason
    (non-200, network, malformed response, missing model)."""


class LlmCall(Protocol):
    def __call__(self, prompt: str, model: str | None = None) -> str: ...


def _default_provider(prompt: str, model: str | None = None) -> str:
    """Production provider — delegates to ATP `bridge_request`.

    Lazy-imports bridge_request so generators/__init__.py can be loaded
    inside the bridge process (which imports generators) without the
    circular dependency.
    """
    # Imported here, not at module load, to break the cycle described
    # in the module docstring.
    from bridge.openclaw_bridge import bridge_request, BridgeError

    payload: dict = {"text": prompt, "model": model or DEFAULT_MODEL}
    try:
        result = bridge_request(payload)
    except BridgeError as e:
        raise LlmError(f"bridge_request failed: {e}") from e

    # bridge_request returns the full ATP execution result. Extract the
    # synthesized text from the canonical location; tolerate a couple of
    # shape variants seen across providers.
    if isinstance(result, dict):
        for key in ("text", "answer", "output", "response"):
            v = result.get(key)
            if isinstance(v, str) and v:
                return v
        manifest = result.get("manifest") or {}
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


def call_llm(prompt: str, model: str | None = None) -> str:
    """Single-shot LLM call. Raises LlmError on any failure."""
    return _provider(prompt, model)
