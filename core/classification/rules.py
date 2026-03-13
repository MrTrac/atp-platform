"""Rule helpers for ATP M1-M2 request classification."""

from __future__ import annotations

from typing import Any


def infer_domain(request: dict[str, Any]) -> str:
    """Infer the top-level domain from product and payload hints."""

    product = str(request.get("product", "")).strip().upper()
    payload = request.get("payload", {})
    input_text = str(payload.get("input_text", "")).lower()

    if product in {"ATP", "TDF"}:
        return "platform"
    if "test" in input_text:
        return "quality"
    if "build" in input_text or "package" in input_text:
        return "delivery"
    return "general"


def infer_product_type(request: dict[str, Any]) -> str:
    """Infer the coarse product type for the seed flow."""

    product = str(request.get("product", "")).strip().upper()
    if product == "ATP":
        return "platform"
    if product:
        return "product"
    return "unknown"


def infer_request_type(request: dict[str, Any]) -> str:
    """Infer request_type from explicit value or text hints."""

    request_type = str(request.get("request_type", "")).strip()
    if request_type and request_type != "unspecified":
        return request_type

    payload = request.get("payload", {})
    input_text = str(payload.get("input_text", "")).lower()

    if "bug" in input_text or "fix" in input_text:
        return "fix"
    if "test" in input_text:
        return "test"
    if "review" in input_text or "inspect" in input_text:
        return "review"
    return "implementation"


def infer_execution_intent(request: dict[str, Any]) -> str:
    """Infer execution_intent from explicit value or request hints."""

    execution_intent = str(request.get("execution_intent", "")).strip()
    if execution_intent and execution_intent != "unspecified":
        return execution_intent

    request_type = infer_request_type(request)
    if request_type == "test":
        return "validate"
    if request_type == "review":
        return "inspect"
    if request_type == "fix":
        return "update"
    return "preview"


def build_rule_trace(request: dict[str, Any]) -> list[str]:
    """Return a small trace describing which rule family produced the result."""

    product = str(request.get("product", "unknown")).lower()
    return [
        "mode:rule_based",
        f"product:{product or 'unknown'}",
        f"request_type:{infer_request_type(request)}",
    ]
