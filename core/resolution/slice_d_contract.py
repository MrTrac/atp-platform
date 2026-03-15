"""ATP v1.0 Slice D — Compatibility layer.

Authority implementation: core.decision_control.contract.
This module re-exports from authority and provides build_decision_transition_control_contract
for callers that need the composite contract shape. Do not add duplicate authority logic here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from core.decision_control.contract import (
    DECISION_CLASSES,
    DECISION_RESULTS,
    TRANSITION_CLASSES,
    SliceDContractError,
    build_decision_record,
    build_transition_record,
    validate_decision_record,
    validate_transition_record,
)

__all__ = [
    "DECISION_CLASSES",
    "DECISION_RESULTS",
    "TRANSITION_CLASSES",
    "SliceDContractError",
    "build_decision_record",
    "build_transition_record",
    "build_decision_transition_control_contract",
    "validate_decision_record",
    "validate_transition_record",
]


def _derive_decision_and_transition_from_continuity(
    operational_continuity_contract: dict[str, Any],
) -> tuple[str, str, str]:
    """Derive decision_class, decision_result, transition_class from Slice C continuity state."""
    oc_state = operational_continuity_contract.get("operational_continuity_state", {})
    continuity_state = str(oc_state.get("continuity_state", "")).strip()

    if continuity_state == "approved_continuity_ready":
        return "conditional_binding_decision", "allow", "allowed_transition"
    if continuity_state == "rejected_continuity_closed":
        return "blocking_decision", "block", "blocked_transition"
    if continuity_state == "held_continuity_pending":
        return "conditional_binding_decision", "defer", "deferred_transition"
    if continuity_state == "deferred_continuity_deferred":
        return "conditional_binding_decision", "defer", "deferred_transition"

    return "observational_decision", "defer", "deferred_transition"


def build_decision_transition_control_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    operational_continuity_gate_followup_state_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build composite Slice D contract. Uses authority core.decision_control."""
    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise SliceDContractError("request_id is required for the decision transition control contract.")

    if not str(run_id).strip():
        raise SliceDContractError("run_id is required for the decision transition control contract.")

    oc_contract = operational_continuity_gate_followup_state_contract
    decision_class, decision_result, transition_class = _derive_decision_and_transition_from_continuity(
        oc_contract
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    actor = "conditional_binding_authority" if decision_class != "observational_decision" else "observational_authority"
    oc_state = oc_contract.get("operational_continuity_state", {})
    continuity_state = str(oc_state.get("continuity_state", "")).strip()

    decision_record = build_decision_record(
        request_id=request_id,
        run_id=run_id,
        operational_continuity_state_contract=oc_contract,
        decision_actor="atp_control_contract",
        decision_authority=actor,
        decision_class=decision_class,
        rationale_summary=f"Decision derived from Slice C continuity state '{continuity_state}'.",
        evidence_summary="operational_continuity_gate_followup_state_contract",
        requested_transition=transition_class,
        decision_result=decision_result,
        created_at=ts,
    )

    source_state_ref = decision_record["source_state_ref"]
    resulting_state_or_move = continuity_state if decision_result in ("allow", "conditional") else f"{continuity_state}_transition_{decision_result}"

    transition_record = build_transition_record(
        request_id=request_id,
        run_id=run_id,
        source_state_ref=source_state_ref,
        decision_record=decision_record,
        transition_class=transition_class,
        permission_block_basis="continuity_state_derived",
        resulting_state_or_move=resulting_state_or_move,
        status_summary=f"{transition_class} from {continuity_state}",
        created_at=ts,
    )

    transition_record_compat = dict(transition_record)
    transition_record_compat["resulting_state"] = transition_record["resulting_state_or_move"]

    return {
        "contract_id": f"decision-transition-control-{request_id}",
        "contract_version": "v1.0-slice-d",
        "request_id": request_id,
        "run_id": run_id,
        "scope": "operational_decision_transition_control_only",
        "operational_continuity_gate_followup_state_ref": {
            "contract_id": oc_contract.get("contract_id", ""),
            "continuity_state": continuity_state,
            "state_status": str(oc_state.get("state_status", "")).strip(),
        },
        "decision_record": decision_record,
        "transition_record": transition_record_compat,
        "traceability": {
            "source_state_contract_id": oc_contract.get("contract_id", ""),
            "decision_record_id": decision_record["record_id"],
            "transition_record_id": transition_record["record_id"],
            "chain": "source_state -> decision -> permission_block -> transition -> resulting_state",
        },
        "notes": [
            "This contract records a bounded decision and transition control only.",
            "It is distinct from approval UI, workflow engines, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }
