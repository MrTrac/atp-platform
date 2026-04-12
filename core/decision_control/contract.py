"""Decision control runtime contract authority for ATP v1.0 Slice D.

ATP v1.0.3 — Operational Decision / State Transition Control Contract.
Source-of-truth: docs/archive/reports/ATP_v1_0_Slice_D_Decision_Transition_Control_Contract.md
Traceability: source state -> decision -> permission/block -> transition -> resulting state.
"""

from __future__ import annotations

from typing import Any

# Decision classes per Slice D contract
DECISION_CLASSES = frozenset({
    "observational_decision",
    "advisory_decision",
    "conditional_binding_decision",
    "blocking_decision",
})

# Decision result (permission/block) per Slice D contract
DECISION_RESULTS = frozenset({
    "allow",
    "conditional",
    "defer",
    "block",
    "loop_back",
})

# Transition classes per Slice D contract
TRANSITION_CLASSES = frozenset({
    "allowed_transition",
    "conditional_transition",
    "deferred_transition",
    "blocked_transition",
    "loop_back_transition",
})

SLICE_C_CONTRACT_ID_PREFIX = "operational-continuity-gate-followup-state-"
SLICE_C_STATE_SCOPE = "operational_continuity_gate_followup_state_only"
DECISION_TO_TRANSITION = {
    "allow": "allowed_transition",
    "conditional": "conditional_transition",
    "defer": "deferred_transition",
    "block": "blocked_transition",
    "loop_back": "loop_back_transition",
}


class DecisionContractError(ValueError):
    """Raised when a Slice D contract field is invalid or missing."""


def _require_non_empty(value: Any, field_name: str) -> str:
    if value is None:
        raise DecisionContractError(f"Missing required field: {field_name}")
    v = str(value).strip()
    if not v:
        raise DecisionContractError(f"Empty required field: {field_name}")
    return v


def _require_one_of(value: Any, allowed: frozenset[str], field_name: str) -> str:
    v = _require_non_empty(value, field_name)
    if v not in allowed:
        raise DecisionContractError(
            f"Invalid {field_name}: {v!r}. Must be one of: {sorted(allowed)}"
        )
    return v


def _validate_source_state_ref(ref: Any, *, field_name: str = "source_state_ref") -> dict[str, Any]:
    if ref is None:
        raise DecisionContractError(f"Missing required field: {field_name}")
    if not isinstance(ref, dict):
        contract_id = _require_non_empty(ref, field_name)
        if not contract_id.startswith(SLICE_C_CONTRACT_ID_PREFIX):
            raise DecisionContractError(
                f"{field_name} must reference canonical Slice C contract_id."
            )
        return {"contract_id": contract_id}

    contract_id = _require_non_empty(ref.get("contract_id"), f"{field_name}.contract_id")
    if not contract_id.startswith(SLICE_C_CONTRACT_ID_PREFIX):
        raise DecisionContractError(
            f"{field_name}.contract_id must reference canonical Slice C continuity-state contract."
        )
    _require_non_empty(ref.get("state_scope"), f"{field_name}.state_scope")
    if ref.get("state_scope") != SLICE_C_STATE_SCOPE:
        raise DecisionContractError(
            f"{field_name}.state_scope must be {SLICE_C_STATE_SCOPE!r}."
        )
    _require_non_empty(ref.get("continuity_state"), f"{field_name}.continuity_state")
    return ref


def _validate_decision_semantics(record: dict[str, Any]) -> None:
    decision_class = _require_one_of(
        record.get("decision_class"),
        DECISION_CLASSES,
        "decision_class",
    )
    decision_result = _require_one_of(
        record.get("decision_result"),
        DECISION_RESULTS,
        "decision_result",
    )
    permission_block_result = _require_non_empty(
        record.get("permission_block_result"),
        "permission_block_result",
    )
    if permission_block_result != decision_result:
        raise DecisionContractError(
            "permission_block_result must match decision_result for Slice D traceability."
        )
    if decision_class in {"observational_decision", "advisory_decision"} and decision_result == "allow":
        raise DecisionContractError(
            f"{decision_class} cannot create binding allow result."
        )
    if decision_class == "blocking_decision" and decision_result != "block":
        raise DecisionContractError(
            "blocking_decision must produce decision_result='block'."
        )
    if decision_class == "conditional_binding_decision" and decision_result == "block":
        raise DecisionContractError(
            "conditional_binding_decision cannot produce decision_result='block'."
        )


def _validate_transition_semantics(record: dict[str, Any]) -> None:
    decision_ref = record.get("decision_record_ref")
    if not isinstance(decision_ref, dict):
        raise DecisionContractError(
            "decision_record_ref must be a dict with traceability fields."
        )
    _require_non_empty(decision_ref.get("record_id"), "decision_record_ref.record_id")
    decision_class = _require_one_of(
        decision_ref.get("decision_class"),
        DECISION_CLASSES,
        "decision_record_ref.decision_class",
    )
    decision_result = _require_one_of(
        decision_ref.get("decision_result"),
        DECISION_RESULTS,
        "decision_record_ref.decision_result",
    )
    transition_class = _require_one_of(
        record.get("transition_class"),
        TRANSITION_CLASSES,
        "transition_class",
    )
    expected_transition = DECISION_TO_TRANSITION[decision_result]
    if transition_class != expected_transition:
        raise DecisionContractError(
            "transition_class must align with decision_record_ref.decision_result."
        )
    if decision_class in {"observational_decision", "advisory_decision"} and transition_class == "allowed_transition":
        raise DecisionContractError(
            f"{decision_class} cannot justify allowed_transition."
        )


def validate_decision_record(record: dict[str, Any]) -> None:
    """Validate decision record has required fields and valid enums.

    Raises DecisionContractError if invalid.
    """
    _require_non_empty(record.get("record_id"), "record_id")
    _validate_source_state_ref(record.get("source_state_ref"))
    _require_non_empty(record.get("decision_actor"), "decision_actor")
    _require_non_empty(record.get("decision_authority"), "decision_authority")
    _require_non_empty(record.get("rationale_summary"), "rationale_summary")
    _require_non_empty(record.get("evidence_summary"), "evidence_summary")
    _require_non_empty(record.get("requested_transition"), "requested_transition")
    _validate_decision_semantics(record)


def validate_transition_record(record: dict[str, Any]) -> None:
    """Validate transition record has required fields and valid enums.

    Raises DecisionContractError if invalid.
    """
    _require_non_empty(record.get("record_id"), "record_id")
    _validate_source_state_ref(record.get("source_state_ref"))
    if record.get("decision_record_ref") is None:
        raise DecisionContractError("Missing required field: decision_record_ref")
    _require_non_empty(record.get("permission_block_basis"), "permission_block_basis")
    _require_non_empty(
        record.get("resulting_state_or_move"),
        "resulting_state_or_move",
    )
    _require_non_empty(record.get("status_summary"), "status_summary")
    _validate_transition_semantics(record)


def build_decision_record(
    request_id: str,
    run_id: str,
    operational_continuity_state_contract: dict[str, Any],
    decision_actor: str,
    decision_authority: str,
    decision_class: str,
    rationale_summary: str,
    evidence_summary: str,
    requested_transition: str,
    decision_result: str,
    *,
    record_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a Slice D decision record linked to Slice C continuity state."""
    if decision_class not in DECISION_CLASSES:
        raise DecisionContractError(
            f"decision_class must be one of {sorted(DECISION_CLASSES)}"
        )
    if decision_result not in DECISION_RESULTS:
        raise DecisionContractError(
            f"decision_result must be one of {sorted(DECISION_RESULTS)}"
        )

    contract_id = str(
        operational_continuity_state_contract.get("contract_id", "")
    ).strip()
    if not contract_id:
        raise DecisionContractError(
            "operational_continuity_state_contract must contain contract_id (Slice C source)."
        )
    if not contract_id.startswith(SLICE_C_CONTRACT_ID_PREFIX):
        raise DecisionContractError(
            "operational_continuity_state_contract.contract_id must reference canonical Slice C continuity-state contract."
        )
    state_scope = str(
        operational_continuity_state_contract.get("state_scope", "")
    ).strip()
    if state_scope and state_scope != SLICE_C_STATE_SCOPE:
        raise DecisionContractError(
            f"operational_continuity_state_contract.state_scope must be {SLICE_C_STATE_SCOPE!r}."
        )
    continuity_state = ""
    oc_state = operational_continuity_state_contract.get("operational_continuity_state")
    if isinstance(oc_state, dict):
        continuity_state = str(oc_state.get("continuity_state", "")).strip()
    if not continuity_state:
        raise DecisionContractError(
            "operational_continuity_state_contract.operational_continuity_state.continuity_state is required."
        )

    rid = record_id or f"decision-{request_id}-{run_id}"
    source_state_ref = {
        "contract_id": contract_id,
        "state_scope": state_scope or SLICE_C_STATE_SCOPE,
        "continuity_state": continuity_state,
        "request_id": request_id,
        "run_id": run_id,
    }

    out = {
        "record_id": rid,
        "contract_version": "v1.0-slice-d",
        "request_id": request_id,
        "run_id": run_id,
        "source_state_ref": source_state_ref,
        "decision_actor": _require_non_empty(decision_actor, "decision_actor"),
        "decision_authority": _require_non_empty(decision_authority, "decision_authority"),
        "decision_class": decision_class,
        "rationale_summary": _require_non_empty(rationale_summary, "rationale_summary"),
        "evidence_summary": _require_non_empty(evidence_summary, "evidence_summary"),
        "requested_transition": _require_non_empty(
            requested_transition, "requested_transition"
        ),
        "decision_result": decision_result,
        "permission_block_result": decision_result,
    }
    if created_at is not None:
        out["created_at"] = str(created_at).strip()
    return out


def build_transition_record(
    request_id: str,
    run_id: str,
    source_state_ref: dict[str, Any],
    decision_record: dict[str, Any],
    transition_class: str,
    permission_block_basis: str,
    resulting_state_or_move: str,
    status_summary: str,
    *,
    record_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a Slice D transition record linked to source state and decision record."""
    if transition_class not in TRANSITION_CLASSES:
        raise DecisionContractError(
            f"transition_class must be one of {sorted(TRANSITION_CLASSES)}"
        )

    decision_record_id = str(decision_record.get("record_id", "")).strip()
    if not decision_record_id:
        raise DecisionContractError(
            "decision_record must contain record_id for traceability."
        )

    rid = record_id or f"transition-{request_id}-{run_id}"
    decision_record_ref = {
        "record_id": decision_record_id,
        "decision_class": _require_one_of(
            decision_record.get("decision_class"),
            DECISION_CLASSES,
            "decision_record.decision_class",
        ),
        "decision_result": _require_one_of(
            decision_record.get("decision_result"),
            DECISION_RESULTS,
            "decision_record.decision_result",
        ),
    }

    out = {
        "record_id": rid,
        "contract_version": "v1.0-slice-d",
        "request_id": request_id,
        "run_id": run_id,
        "source_state_ref": source_state_ref,
        "decision_record_ref": decision_record_ref,
        "transition_class": transition_class,
        "permission_block_basis": _require_non_empty(
            permission_block_basis, "permission_block_basis"
        ),
        "resulting_state_or_move": _require_non_empty(
            resulting_state_or_move, "resulting_state_or_move"
        ),
        "status_summary": _require_non_empty(status_summary, "status_summary"),
    }
    if created_at is not None:
        out["created_at"] = str(created_at).strip()
    return out
