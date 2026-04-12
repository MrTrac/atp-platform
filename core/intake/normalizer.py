"""Normalize ATP request payloads for the M1-M2 intake flow.

After normalization, an advisory schema validation pass is run against
``request.schema.yaml``. Validation warnings are collected in
``_validation_warnings`` but never block the flow.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.validation.schema_validator import validate_against_schema


def normalize_request(raw_request: dict[str, Any]) -> dict[str, Any]:
    """Normalize a request into the ATP v0 seed structure."""

    request = deepcopy(raw_request)
    metadata = request.get("metadata")
    payload = request.get("payload")

    normalized: dict[str, Any] = {
        "request_id": request.get("request_id") or "request-unknown",
        "product": request.get("product") or request.get("product_hint") or "unknown",
        "request_type": request.get("request_type") or "unspecified",
        "execution_intent": request.get("execution_intent") or "unspecified",
        "payload": payload if isinstance(payload, dict) else {},
        "metadata": metadata if isinstance(metadata, dict) else {},
    }

    if "input_text" in request and "input_text" not in normalized["payload"]:
        normalized["payload"]["input_text"] = request["input_text"]

    if "provider" in request:
        normalized["metadata"].setdefault("provider", request["provider"])
    if "adapter" in request:
        normalized["metadata"].setdefault("adapter", request["adapter"])
    if "capability" in request:
        normalized["metadata"].setdefault("capability", request["capability"])

    for key, value in request.items():
        if key not in normalized:
            normalized[key] = value

    # Advisory schema validation — warnings only, never blocks
    report = validate_against_schema(normalized, "request/request.schema.yaml")
    if not report.valid:
        normalized["_validation_warnings"] = report.errors

    return normalized
