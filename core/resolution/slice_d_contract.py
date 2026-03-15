"""ATP v1.0 Slice D — Operational Decision / State Transition Control Contract.

Materializes runtime contract shape for:
  source state -> decision -> permission/block -> transition -> resulting state

Slice D là control-contract slice. Không phải workflow engine, execution engine,
approval UI, hay recovery engine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DECISION_CLASSES = (
    "observational_decision",
    "advisory_decision",
    "conditional_binding_decision",
    "blocking_decision",
)
DECISION_RESULTS = ("allow", "conditional", "defer", "block", "loop_back")
TRANSITION_CLASSES = (
    "allowed_transition",
    "conditional_transition",
    "deferred_transition",
    "blocked_transition",
    "loop_back_transition",
)


def validate_decision_record(record: dict[str, Any]) -> None:
    """Validate decision record has required fields. Raises ValueError if invalid."""
    required = (
        "record_id",
        "source_state_ref",
        "decision_actor",
        "decision_authority",
        "decision_class",
        "rationale_summary",
        "evidence_summary",
        "requested_transition",
        "decision_result",
    )
    for field in required:
        val = record.get(field)
        if val is None or (isinstance(val, str) and not str(val).strip()):
            raise ValueError(f"Decision record missing required field: {field}")

    dc = str(record.get("decision_class", "")).strip()
    if dc not in DECISION_CLASSES:
        raise ValueError(f"Invalid decision_class: {dc}. Must be one of {DECISION_CLASSES}")

    dr = str(record.get("decision_result", "")).strip()
    if dr not in DECISION_RESULTS:
        raise ValueError(f"Invalid decision_result: {dr}. Must be one of {DECISION_RESULTS}")


def validate_transition_record(record: dict[str, Any]) -> None:
    """Validate transition record has required fields. Raises ValueError if invalid."""
    required = (
        "record_id",
        "source_state_ref",
        "decision_record_ref",
        "transition_class",
        "permission_block_basis",
        "resulting_state",
    )
    for field in required:
        val = record.get(field)
        if val is None or (isinstance(val, str) and not str(val).strip()):
            raise ValueError(f"Transition record missing required field: {field}")

    tc = str(record.get("transition_class", "")).strip()
    if tc not in TRANSITION_CLASSES:
        raise ValueError(f"Invalid transition_class: {tc}. Must be one of {TRANSITION_CLASSES}")


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
    """Build the explicit v1.0 Slice D decision / transition control contract.

    Source state comes from Slice C operational continuity contract.
    Decision and transition are derived from continuity state semantics.
    """
    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the decision transition control contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the decision transition control contract.")

    oc_contract = operational_continuity_gate_followup_state_contract
    oc_contract_id = str(oc_contract.get("contract_id", "")).strip()
    if not oc_contract_id:
        raise ValueError(
            "operational_continuity_gate_followup_state_contract is required for Slice D decision transition control."
        )

    oc_state = oc_contract.get("operational_continuity_state", {})
    continuity_state = str(oc_state.get("continuity_state", "")).strip()
    state_status = str(oc_state.get("state_status", "")).strip()
    continuity_signal = str(oc_state.get("continuity_signal", "")).strip()

    decision_class, decision_result, transition_class = _derive_decision_and_transition_from_continuity(
        oc_contract
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    decision_record_id = f"decision-{request_id}-{run_id}"
    transition_record_id = f"transition-{request_id}-{run_id}"

    decision_record = {
        "record_id": decision_record_id,
        "source_state_ref": {
            "contract_id": oc_contract_id,
            "continuity_state": continuity_state,
            "state_status": state_status,
        },
        "decision_actor": "atp_control_contract",
        "decision_authority": "conditional_binding_authority" if decision_class != "observational_decision" else "observational_authority",
        "decision_class": decision_class,
        "rationale_summary": f"Decision derived from Slice C continuity state '{continuity_state}'.",
        "evidence_summary": "operational_continuity_gate_followup_state_contract",
        "requested_transition": transition_class,
        "decision_result": decision_result,
        "created_at": ts,
    }
    validate_decision_record(decision_record)

    resulting_state = continuity_state if decision_result in ("allow", "conditional") else f"{continuity_state}_transition_{decision_result}"

    transition_record = {
        "record_id": transition_record_id,
        "source_state_ref": {
            "contract_id": oc_contract_id,
            "continuity_state": continuity_state,
        },
        "decision_record_ref": decision_record_id,
        "transition_class": transition_class,
        "permission_block_basis": "continuity_state_derived",
        "resulting_state": resulting_state,
        "status_summary": f"{transition_class} from {continuity_state}",
        "created_at": ts,
    }
    validate_transition_record(transition_record)

    return {
        "contract_id": f"decision-transition-control-{request_id}",
        "contract_version": "v1.0-slice-d",
        "request_id": request_id,
        "run_id": run_id,
        "scope": "operational_decision_transition_control_only",
        "operational_continuity_gate_followup_state_ref": {
            "contract_id": oc_contract_id,
            "continuity_state": continuity_state,
            "state_status": state_status,
        },
        "decision_record": decision_record,
        "transition_record": transition_record,
        "traceability": {
            "source_state_contract_id": oc_contract_id,
            "decision_record_id": decision_record_id,
            "transition_record_id": transition_record_id,
            "chain": "source_state -> decision -> permission_block -> transition -> resulting_state",
        },
        "notes": [
            "This contract records a bounded decision and transition control only.",
            "It is distinct from approval UI, workflow engines, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }
