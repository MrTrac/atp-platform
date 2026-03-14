"""Exchange boundary decision model for ATP v0.3 Slice A."""

from __future__ import annotations

from typing import Any


def build_exchange_boundary_decision(
    run_id: str,
    request_id: str,
    close_decision: str,
    handoff_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Determine whether handoff stays run-local or becomes an external-boundary candidate."""

    if close_decision == "continue_pending":
        boundary_mode = "external_exchange_candidate"
        requires_exchange_boundary = True
        reason_codes = ["continue_pending_requires_external_handoff_boundary"]
    elif close_decision == "close_rejected":
        boundary_mode = "run_local_handoff"
        requires_exchange_boundary = False
        reason_codes = ["close_rejected_keeps_handoff_inside_current_run"]
    else:
        boundary_mode = "run_local_handoff"
        requires_exchange_boundary = False
        reason_codes = ["closed_run_keeps_handoff_inside_current_run"]

    return {
        "decision_id": f"exchange-boundary-{run_id}",
        "run_id": run_id,
        "request_id": request_id,
        "close_or_continue": close_decision,
        "boundary_mode": boundary_mode,
        "requires_exchange_boundary": requires_exchange_boundary,
        "exchange_materialization_status": "deferred",
        "manifest_reference": handoff_outputs.get("manifest_reference", {}).get("manifest_reference", ""),
        "evidence_bundle_id": handoff_outputs.get("evidence_bundle", {}).get("bundle_id", ""),
        "reason_codes": reason_codes,
        "notes": [
            "Slice A only decides boundary eligibility.",
            "External exchange materialization remains deferred until Slice B.",
        ],
    }
