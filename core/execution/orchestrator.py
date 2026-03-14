"""Orchestrate ATP M6 execution from routing results and packaged context."""

from __future__ import annotations

from typing import Any

from core.execution.executor import ExecutionError, invoke_executor
from core.execution.output_normalizer import normalize_output


def execute_run(
    normalized_request: dict[str, Any],
    resolution: dict[str, Any],
    task_manifest: dict[str, Any],
    product_context: dict[str, Any],
    evidence_bundle: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    """Execute the supported ATP M6 path and normalize the result."""

    _ = task_manifest, product_context, evidence_bundle
    raw_result = invoke_executor(normalized_request, routing_result)
    return normalize_output(
        raw_result=raw_result,
        request_id=str(normalized_request.get("request_id", "")),
        product=str(resolution.get("product", "")),
        routing_result=routing_result,
    )
