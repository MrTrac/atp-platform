"""Execution adapter contract for ATP.

Provides both a Protocol for structural subtyping and TypedDict
definitions for static analysis of LLM adapter input/output shapes.
"""

from __future__ import annotations

from typing import Any, Protocol, TypedDict


# ---------------------------------------------------------------------------
# Typed shapes for LLM adapters (optional static annotation)
# ---------------------------------------------------------------------------

class LLMRequest(TypedDict, total=False):
    """Input shape for LLM execution adapters."""
    model: str
    prompt: str
    messages: list[dict[str, str]]
    context: str
    options: dict[str, Any]
    force_cloud: bool
    escalation_trigger: str


class LLMResult(TypedDict, total=False):
    """Output shape from LLM execution adapters."""
    status: str
    route_type: str
    provider: str
    model: str
    output: str
    error: str
    manifest: dict[str, Any]
    escalation_triggered: bool


class LocalExecResult(TypedDict, total=False):
    """Output shape from local subprocess execution adapters."""
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    status: str
    notes: list[str]


# ---------------------------------------------------------------------------
# Protocol contract (unchanged behavioral interface)
# ---------------------------------------------------------------------------

class ExecutionAdapter(Protocol):
    """Execution adapters accept ATP-native dict inputs and return raw dict outputs."""

    def execute(self, execution_request: dict[str, Any]) -> dict[str, Any]:
        """Execute a prepared ATP request payload."""

