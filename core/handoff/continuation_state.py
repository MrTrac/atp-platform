"""Continue-pending operational continuity model for ATP v0.3 Slice C."""

from __future__ import annotations

from typing import Any


def build_continuation_state(
    run_id: str,
    request_id: str,
    close_decision: str,
    exchange_boundary_decision: dict[str, Any],
    exchange_summary: dict[str, Any],
    handoff_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Build the minimal explicit continuation state for continue-pending runs."""

    continuation_required = close_decision == "continue_pending"
    if continuation_required:
        current_source = "exchange_current_task" if exchange_summary.get("materialized") else "run_handoff"
        continuity_status = "continuation_pending"
        continuity_refs = {
            "exchange_root": exchange_summary.get("exchange_root", ""),
            "exchange_bundle_id": handoff_outputs.get("exchange_bundle", {}).get("exchange_id", ""),
            "evidence_bundle_id": handoff_outputs.get("evidence_bundle", {}).get("bundle_id", ""),
            "manifest_reference": handoff_outputs.get("manifest_reference", {}).get("manifest_reference", ""),
        }
        reason_codes = ["continue_pending_current_source_established"]
    else:
        current_source = "none"
        continuity_status = "continuation_not_required"
        continuity_refs = {
            "exchange_root": "",
            "exchange_bundle_id": "",
            "evidence_bundle_id": "",
            "manifest_reference": handoff_outputs.get("manifest_reference", {}).get("manifest_reference", ""),
        }
        reason_codes = ["continuation_not_required_for_closed_run"]

    return {
        "continuation_id": f"continuation-{run_id}",
        "run_id": run_id,
        "request_id": request_id,
        "close_or_continue": close_decision,
        "continuation_required": continuation_required,
        "continuity_status": continuity_status,
        "current_source": current_source,
        "exchange_boundary_decision_id": exchange_boundary_decision.get("decision_id", ""),
        "exchange_boundary_mode": exchange_boundary_decision.get("boundary_mode", ""),
        "exchange_materialization_status": exchange_boundary_decision.get("exchange_materialization_status", ""),
        "continuity_artifacts": list(handoff_outputs.get("evidence_bundle", {}).get("selected_artifacts", [])),
        "authoritative_refs": list(handoff_outputs.get("evidence_bundle", {}).get("authoritative_refs", [])),
        "continuity_refs": continuity_refs,
        "reason_codes": reason_codes,
        "notes": [
            "Slice C only establishes minimal continue_pending operational continuity.",
            "No scheduler, queue, or persistence subsystem is introduced here.",
        ],
    }
