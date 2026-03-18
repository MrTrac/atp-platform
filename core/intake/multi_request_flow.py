"""Bounded multi-request Slice 02 flow aggregation helpers."""

from __future__ import annotations

from typing import Any

from core.intake.request_flow import prepare_single_ai_request_flow


def prepare_multi_request_flow(
    request_inputs: list[tuple[str, dict[str, Any]]],
    *,
    run_id: str = "multi-flow-preview-0001",
) -> dict[str, Any]:
    """Prepare multiple bounded Slice 02 request flows in explicit input order."""

    request_flows: list[dict[str, Any]] = []
    request_ids: list[str] = []
    flow_ids: list[str] = []

    for index, (request_file, raw_request) in enumerate(request_inputs, start=1):
        item_run_id = f"{run_id}-item-{index:02d}"
        summary = prepare_single_ai_request_flow(raw_request, run_id=item_run_id)
        request_ids.append(str(summary["request_id"]))
        flow_ids.append(str(summary["flow_id"]))
        request_flows.append(
            {
                "request_file": request_file,
                "run_id": item_run_id,
                "summary": summary,
            }
        )

    return {
        "multi_request_id": f"{run_id}-multi-request-flow",
        "processing_mode": "sequential_operator_controlled",
        "ordering_basis": "input_order",
        "request_count": len(request_inputs),
        "accepted_request_count": len(request_inputs),
        "supported_flow": "bounded_multi_request_intake_to_single_ai_package",
        "request_ids": request_ids,
        "flow_ids": flow_ids,
        "notes": [
            "This surface prepares multiple Slice 02 request flows in explicit input order only.",
            "No queue, scheduler, background execution, or orchestration is performed here.",
        ],
        "request_flows": request_flows,
    }
