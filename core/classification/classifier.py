"""Apply ATP M1-M3 rule-based request classification."""

from __future__ import annotations

from typing import Any

from core.classification.rules import (
    build_rule_trace,
    infer_domain,
    infer_execution_intent,
    infer_product_type,
    infer_request_type,
)


def classify_request(normalized_request: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow classification payload with stable keys."""

    request_type = infer_request_type(normalized_request)
    execution_intent = infer_execution_intent(
        {**normalized_request, "request_type": request_type}
    )

    return {
        "product": normalized_request.get("product", "unknown"),
        "domain": infer_domain(normalized_request),
        "product_type": infer_product_type(normalized_request),
        "request_type": request_type,
        "execution_intent": execution_intent,
        "capability": normalized_request.get("metadata", {}).get("capability", "unspecified"),
        "rule_trace": build_rule_trace(normalized_request),
    }
