"""Typed error classification for ATP execution results.

Provides structured error codes that inform governance routing
and escalation decisions. Each error code carries metadata about
whether the error is recoverable and whether the request needs modification.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class ErrorClassification(NamedTuple):
    code: str
    category: str
    recoverable: bool
    requires_modification: bool


# ---------------------------------------------------------------------------
# Error code registry
# ---------------------------------------------------------------------------

NETWORK_ERROR = ErrorClassification(
    code="network_error",
    category="transient",
    recoverable=True,
    requires_modification=False,
)

TIMEOUT = ErrorClassification(
    code="timeout",
    category="transient",
    recoverable=True,
    requires_modification=False,
)

CONTRACT_VIOLATION = ErrorClassification(
    code="contract_violation",
    category="permanent",
    recoverable=False,
    requires_modification=True,
)

COMPLETION_VALIDATION_FAILED = ErrorClassification(
    code="completion_validation_failed",
    category="permanent",
    recoverable=False,
    requires_modification=True,
)

PROVIDER_UNAVAILABLE = ErrorClassification(
    code="provider_unavailable",
    category="transient",
    recoverable=True,
    requires_modification=False,
)

QUOTA_EXCEEDED = ErrorClassification(
    code="quota_exceeded",
    category="transient",
    recoverable=True,
    requires_modification=True,
)

UNKNOWN_ERROR = ErrorClassification(
    code="unknown_error",
    category="unknown",
    recoverable=False,
    requires_modification=False,
)

# Lookup table
_REGISTRY: dict[str, ErrorClassification] = {
    ec.code: ec
    for ec in [
        NETWORK_ERROR,
        TIMEOUT,
        CONTRACT_VIOLATION,
        COMPLETION_VALIDATION_FAILED,
        PROVIDER_UNAVAILABLE,
        QUOTA_EXCEEDED,
        UNKNOWN_ERROR,
    ]
}


def classify_error(error_message: str) -> ErrorClassification:
    """Classify an error message into a typed error code."""
    lower = error_message.lower()

    if "timeout" in lower or "timed out" in lower:
        return TIMEOUT
    if "refused" in lower or "urlopen" in lower or "connection" in lower:
        return NETWORK_ERROR
    if "contract" in lower or "required" in lower or "violated" in lower:
        return CONTRACT_VIOLATION
    if "empty response" in lower or "completion validation" in lower:
        return COMPLETION_VALIDATION_FAILED
    if "unavailable" in lower or "not reachable" in lower:
        return PROVIDER_UNAVAILABLE
    if "quota" in lower or "rate limit" in lower or "429" in lower:
        return QUOTA_EXCEEDED

    return UNKNOWN_ERROR


def get_error_code(code: str) -> ErrorClassification:
    """Look up an error classification by code string."""
    return _REGISTRY.get(code, UNKNOWN_ERROR)


def to_dict(ec: ErrorClassification) -> dict[str, Any]:
    """Convert ErrorClassification to dict for JSON serialization."""
    return {
        "code": ec.code,
        "category": ec.category,
        "recoverable": ec.recoverable,
        "requires_modification": ec.requires_modification,
    }
