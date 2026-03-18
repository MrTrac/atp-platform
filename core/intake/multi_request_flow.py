"""Bounded multi-request Slice 02 flow aggregation helpers."""

from __future__ import annotations

from typing import Any

from core.session_tracking import build_execution_session_summary

from core.intake.request_flow import prepare_single_ai_request_flow


def build_multi_request_flow_summary(
    prepared_request_flows: list[dict[str, Any]],
    *,
    run_id: str = "multi-flow-preview-0001",
) -> dict[str, Any]:
    """Build an aggregate summary for multiple prepared Slice 02 request flows."""

    request_flows: list[dict[str, Any]] = []
    request_ids: list[str] = []
    flow_ids: list[str] = []

    for item in prepared_request_flows:
        request_file = str(item["request_file"])
        item_run_id = str(item["run_id"])
        summary = dict(item["summary"])
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
        "request_count": len(prepared_request_flows),
        "accepted_request_count": len(prepared_request_flows),
        "supported_flow": "bounded_multi_request_intake_to_single_ai_package",
        "notes": [
            "This surface prepares multiple Slice 02 request flows in explicit input order only.",
            "No queue, scheduler, background execution, or orchestration is performed here.",
        ],
        "session_summary": build_execution_session_summary(
            request_files=[str(item["request_file"]) for item in prepared_request_flows],
            request_ids=request_ids,
        ),
        "request_ids": request_ids,
        "flow_ids": flow_ids,
        "request_flows": request_flows,
    }
