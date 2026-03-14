"""Build ATP M8 finalization summaries."""

from __future__ import annotations

from typing import Any


def derive_final_status(approval_result: dict[str, Any]) -> str:
    """Map approval status to the stable ATP v0 finalization status."""

    approval_status = str(approval_result.get("approval_status", "needs_attention"))
    if approval_status == "approved":
        return "completed"
    if approval_status == "rejected":
        return "rejected"
    return "attention_required"


def finalize_run(
    execution_result: dict[str, Any],
    artifact_summary: dict[str, Any],
    validation_summary: dict[str, Any],
    review_decision: dict[str, Any],
    approval_result: dict[str, Any],
    handoff_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Build a stable finalization summary."""

    request_id = str(execution_result.get("request_id", "request-unknown"))
    approval_status = str(approval_result.get("approval_status", "needs_attention"))
    final_status = derive_final_status(approval_result)

    return {
        "finalization_id": f"finalization-{request_id}",
        "request_id": request_id,
        "final_status": final_status,
        "selected_provider": execution_result.get("selected_provider", "unknown"),
        "selected_node": execution_result.get("selected_node", "unknown"),
        "validation_status": validation_summary.get("validation_status", "incomplete"),
        "review_status": review_decision.get("review_status", "revise"),
        "approval_status": approval_status,
        "authoritative_artifacts": list(artifact_summary.get("authoritative_artifacts", [])),
        "handoff_refs": {
            "inline_context": handoff_outputs.get("inline_context", {}).get("handoff_type", ""),
            "evidence_bundle": handoff_outputs.get("evidence_bundle", {}).get("bundle_id", ""),
            "exchange_bundle": handoff_outputs.get("exchange_bundle", {}).get("exchange_id", ""),
            "manifest_reference": handoff_outputs.get("manifest_reference", {}).get("manifest_reference", ""),
        },
        "notes": ["ATP v0 finalization summary only. No external finalization side effects."],
    }
