"""Unit tests for ATP v1.0 Slice D decision/transition control contract.

Authority implementation: core.decision_control.contract / core.decision_control.
Composite builder (compatibility): core.resolution.slice_d_contract.build_decision_transition_control_contract.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from core.decision_control import (
    DECISION_CLASSES,
    DECISION_RESULTS,
    TRANSITION_CLASSES,
    SliceDContractError,
    build_decision_record,
    build_transition_record,
    validate_decision_record,
    validate_transition_record,
)
from core.resolution.slice_d_contract import build_decision_transition_control_contract
from core.resolution.product_resolver import (
    build_closure_continuation_state_contract,
    build_decision_to_closure_continuation_handoff_contract,
    build_finalization_closure_record_contract,
    build_gate_outcome_operational_followup_contract,
    build_operational_continuity_gate_followup_state_contract,
    build_post_execution_decision_contract,
    build_product_execution_preparation_contract,
    build_product_execution_result_contract,
    build_request_to_product_resolution_contract,
    build_resolution_to_handoff_intent_contract,
    build_review_approval_gate_contract,
    resolve_product,
)
from core.classification.classifier import classify_request
from core.context.product_context import build_product_context
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


def _valid_source_state_ref() -> dict:
    """Source state ref that passes Slice C contract_id/state_scope/continuity_state validation."""
    return {
        "contract_id": "operational-continuity-gate-followup-state-req-1",
        "state_scope": "operational_continuity_gate_followup_state_only",
        "continuity_state": "approved_continuity_ready",
    }


def _minimal_oc_contract(continuity_state: str) -> dict:
    """Build minimal operational continuity contract for Slice D composite builder."""
    return {
        "contract_id": "operational-continuity-gate-followup-state-req-1",
        "state_scope": "operational_continuity_gate_followup_state_only",
        "request_id": "req-1",
        "run_id": "run-slice-d-1",
        "operational_continuity_state": {
            "continuity_state": continuity_state,
            "state_status": "continuity_ready" if continuity_state == "approved_continuity_ready" else "continuity_closed",
            "continuity_signal": "approved_continuation_available",
        },
    }


class TestSliceDContract(unittest.TestCase):
    """Cover Slice D decision/transition control — authority in core.decision_control."""

    def test_decision_classes_and_transition_classes_match_docs(self) -> None:
        self.assertIn("observational_decision", DECISION_CLASSES)
        self.assertIn("advisory_decision", DECISION_CLASSES)
        self.assertIn("conditional_binding_decision", DECISION_CLASSES)
        self.assertIn("blocking_decision", DECISION_CLASSES)
        self.assertIn("allow", DECISION_RESULTS)
        self.assertIn("block", DECISION_RESULTS)
        self.assertIn("defer", DECISION_RESULTS)
        self.assertIn("loop_back", DECISION_RESULTS)
        self.assertIn("allowed_transition", TRANSITION_CLASSES)
        self.assertIn("blocked_transition", TRANSITION_CLASSES)
        self.assertIn("deferred_transition", TRANSITION_CLASSES)
        self.assertIn("loop_back_transition", TRANSITION_CLASSES)

    def test_validate_decision_record_accepts_valid_record(self) -> None:
        record = {
            "record_id": "decision-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "atp_control_contract",
            "decision_authority": "conditional_binding_authority",
            "decision_class": "conditional_binding_decision",
            "rationale_summary": "Derived from continuity state.",
            "evidence_summary": "operational_continuity_contract",
            "requested_transition": "allowed_transition",
            "decision_result": "allow",
            "permission_block_result": "allow",
        }
        validate_decision_record(record)

    def test_validate_decision_record_rejects_missing_required_field(self) -> None:
        record = {
            "record_id": "decision-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "atp",
            "decision_authority": "conditional_binding",
            "decision_class": "conditional_binding_decision",
            "rationale_summary": "x",
            "evidence_summary": "y",
            "requested_transition": "allowed_transition",
            "decision_result": "invalid_result",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(record)
        self.assertIn("decision_result", str(ctx.exception))

    def test_validate_decision_record_rejects_invalid_decision_class(self) -> None:
        record = {
            "record_id": "decision-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "atp",
            "decision_authority": "conditional_binding",
            "decision_class": "invalid_class",
            "rationale_summary": "x",
            "evidence_summary": "y",
            "requested_transition": "allowed_transition",
            "decision_result": "allow",
            "permission_block_result": "allow",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(record)
        self.assertIn("decision_class", str(ctx.exception))

    def test_validate_transition_record_accepts_valid_record(self) -> None:
        record = {
            "record_id": "transition-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_record_ref": {
                "record_id": "decision-1",
                "decision_class": "conditional_binding_decision",
                "decision_result": "allow",
            },
            "transition_class": "allowed_transition",
            "permission_block_basis": "continuity_state_derived",
            "resulting_state_or_move": "approved_continuity_ready",
            "status_summary": "applied",
        }
        validate_transition_record(record)

    def test_validate_transition_record_rejects_missing_decision_record_ref(self) -> None:
        record = {
            "record_id": "transition-1",
            "source_state_ref": _valid_source_state_ref(),
            "transition_class": "allowed_transition",
            "permission_block_basis": "x",
            "resulting_state_or_move": "y",
            "status_summary": "ok",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_transition_record(record)
        self.assertIn("decision_record_ref", str(ctx.exception))

    def test_validate_transition_record_rejects_invalid_transition_class(self) -> None:
        record = {
            "record_id": "transition-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_record_ref": {
                "record_id": "decision-1",
                "decision_class": "conditional_binding_decision",
                "decision_result": "allow",
            },
            "transition_class": "invalid_transition",
            "permission_block_basis": "x",
            "resulting_state_or_move": "y",
            "status_summary": "ok",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_transition_record(record)
        self.assertIn("transition_class", str(ctx.exception))

    def test_build_decision_record_valid(self) -> None:
        oc = _minimal_oc_contract("approved_continuity_ready")
        rec = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="gate_authority",
            decision_authority="approval_gate",
            decision_class="conditional_binding_decision",
            rationale_summary="Continuity ready.",
            evidence_summary="Gate outcome approved.",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        self.assertEqual(rec["record_id"], "decision-req-1-run-1")
        self.assertEqual(rec["decision_class"], "conditional_binding_decision")
        self.assertEqual(rec["decision_result"], "allow")
        self.assertEqual(rec["source_state_ref"]["contract_id"], oc["contract_id"])
        validate_decision_record(rec)

    def test_build_decision_record_requires_slice_c_contract_id(self) -> None:
        with self.assertRaises(SliceDContractError) as ctx:
            build_decision_record(
                request_id="req-1",
                run_id="run-1",
                operational_continuity_state_contract={"state_scope": "x"},
                decision_actor="a",
                decision_authority="b",
                decision_class="observational_decision",
                rationale_summary="r",
                evidence_summary="e",
                requested_transition="deferred_transition",
                decision_result="defer",
            )
        self.assertIn("contract_id", str(ctx.exception))

    def test_slice_c_canonical_source_state_linkage(self) -> None:
        oc = _minimal_oc_contract("approved_continuity_ready")
        rec = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="a",
            decision_authority="b",
            decision_class="conditional_binding_decision",
            rationale_summary="r",
            evidence_summary="e",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        self.assertTrue(rec["source_state_ref"]["contract_id"].startswith("operational-continuity-gate-followup-state-"))
        self.assertEqual(rec["source_state_ref"]["state_scope"], "operational_continuity_gate_followup_state_only")
        self.assertEqual(rec["source_state_ref"]["continuity_state"], "approved_continuity_ready")

    def test_observational_advisory_cannot_allow(self) -> None:
        record = {
            "record_id": "dec-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "obs",
            "decision_authority": "observational",
            "decision_class": "observational_decision",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "allowed_transition",
            "decision_result": "allow",
            "permission_block_result": "allow",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(record)
        self.assertIn("cannot create binding allow", str(ctx.exception))

    def test_blocking_decision_must_block(self) -> None:
        record = {
            "record_id": "dec-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "b",
            "decision_authority": "blocking",
            "decision_class": "blocking_decision",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "blocked_transition",
            "decision_result": "allow",
            "permission_block_result": "allow",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(record)
        self.assertIn("blocking_decision must produce", str(ctx.exception))

    def test_conditional_binding_cannot_block(self) -> None:
        record = {
            "record_id": "dec-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "b",
            "decision_authority": "conditional",
            "decision_class": "conditional_binding_decision",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "blocked_transition",
            "decision_result": "block",
            "permission_block_result": "block",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(record)
        self.assertIn("cannot produce decision_result", str(ctx.exception))

    def test_traceability_chain_and_decision_result_transition_alignment(self) -> None:
        oc = _minimal_oc_contract("approved_continuity_ready")
        decision = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="a",
            decision_authority="b",
            decision_class="conditional_binding_decision",
            rationale_summary="r",
            evidence_summary="e",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        source_ref = decision["source_state_ref"]
        trans = build_transition_record(
            request_id="req-1",
            run_id="run-1",
            source_state_ref=source_ref,
            decision_record=decision,
            transition_class="allowed_transition",
            permission_block_basis="allow",
            resulting_state_or_move="next_state",
            status_summary="applied",
        )
        self.assertEqual(trans["source_state_ref"]["contract_id"], oc["contract_id"])
        self.assertEqual(trans["decision_record_ref"]["record_id"], decision["record_id"])
        self.assertEqual(trans["decision_record_ref"]["decision_result"], "allow")
        self.assertEqual(trans["transition_class"], "allowed_transition")
        self.assertEqual(trans["resulting_state_or_move"], "next_state")
        validate_decision_record(decision)
        validate_transition_record(trans)

    def test_build_decision_transition_control_contract_approved_yields_allow_allowed_transition(
        self,
    ) -> None:
        oc = _minimal_oc_contract("approved_continuity_ready")
        contract = build_decision_transition_control_contract(
            run_id="run-slice-d-1",
            normalized_request={"request_id": "req-1"},
            operational_continuity_gate_followup_state_contract=oc,
        )
        self.assertEqual(contract["contract_version"], "v1.0-slice-d")
        self.assertEqual(contract["decision_record"]["decision_class"], "conditional_binding_decision")
        self.assertEqual(contract["decision_record"]["decision_result"], "allow")
        self.assertEqual(contract["transition_record"]["transition_class"], "allowed_transition")
        self.assertIn("source_state", contract["traceability"]["chain"])
        self.assertEqual(
            contract["operational_continuity_gate_followup_state_ref"]["contract_id"],
            "operational-continuity-gate-followup-state-req-1",
        )

    def test_build_decision_transition_control_contract_rejected_yields_block_blocked_transition(
        self,
    ) -> None:
        oc = _minimal_oc_contract("rejected_continuity_closed")
        contract = build_decision_transition_control_contract(
            run_id="run-slice-d-1",
            normalized_request={"request_id": "req-1"},
            operational_continuity_gate_followup_state_contract=oc,
        )
        self.assertEqual(contract["decision_record"]["decision_class"], "blocking_decision")
        self.assertEqual(contract["decision_record"]["decision_result"], "block")
        self.assertEqual(contract["transition_record"]["transition_class"], "blocked_transition")

    def test_build_decision_transition_control_contract_held_yields_defer_deferred_transition(
        self,
    ) -> None:
        oc = _minimal_oc_contract("held_continuity_pending")
        contract = build_decision_transition_control_contract(
            run_id="run-slice-d-1",
            normalized_request={"request_id": "req-1"},
            operational_continuity_gate_followup_state_contract=oc,
        )
        self.assertEqual(contract["decision_record"]["decision_result"], "defer")
        self.assertEqual(contract["transition_record"]["transition_class"], "deferred_transition")

    def test_build_decision_transition_control_contract_requires_oc_contract(self) -> None:
        with self.assertRaises(SliceDContractError) as ctx:
            build_decision_transition_control_contract(
                run_id="run-1",
                normalized_request={"request_id": "req-1"},
                operational_continuity_gate_followup_state_contract={"contract_id": ""},
            )
        self.assertIn("contract_id", str(ctx.exception))

    def test_build_decision_transition_control_contract_integration_with_slice_c(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        resolution_contract = build_request_to_product_resolution_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-1",
        )
        handoff_contract = build_resolution_to_handoff_intent_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            classification=classification,
            resolution_contract=resolution_contract,
            manifest_id="task-manifest-req-1",
        )
        preparation_contract = build_product_execution_preparation_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            task_manifest={"manifest_id": "task-manifest-req-1", "required_capabilities": ["shell_execution"]},
            product_context=build_product_context(resolution),
            evidence_bundle={"bundle_id": "bundle-1", "selected_artifacts": []},
        )
        execution_result_contract = build_product_execution_result_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            execution_preparation_contract=preparation_contract,
            execution_result={
                "execution_id": "exec-1",
                "status": "succeeded",
                "exit_code": 0,
                "command": ["echo", "x"],
                "stdout": "",
                "stderr": "",
            },
            artifact_summary={"artifact_ids": []},
        )
        post_execution_contract = build_post_execution_decision_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            execution_preparation_contract=preparation_contract,
            execution_result_contract=execution_result_contract,
            review_decision={"decision_id": "r1", "review_status": "accept", "validation_status": "passed"},
            approval_result={"approval_id": "a1", "approval_status": "approved", "continue_recommended": False},
            close_decision="close",
        )
        decision_to_handoff = build_decision_to_closure_continuation_handoff_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            execution_preparation_contract=preparation_contract,
            execution_result_contract=execution_result_contract,
            post_execution_decision_contract=post_execution_contract,
        )
        closure_state = build_closure_continuation_state_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            execution_preparation_contract=preparation_contract,
            execution_result_contract=execution_result_contract,
            post_execution_decision_contract=post_execution_contract,
            decision_to_handoff_contract=decision_to_handoff,
        )
        finalization = build_finalization_closure_record_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            execution_result_contract=execution_result_contract,
            post_execution_decision_contract=post_execution_contract,
            decision_to_handoff_contract=decision_to_handoff,
            closure_continuation_state_contract=closure_state,
            finalization_summary={
                "finalization_id": "f1",
                "final_status": "completed",
                "validation_status": "passed",
                "review_status": "accept",
                "approval_status": "approved",
            },
        )
        gate = build_review_approval_gate_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            execution_result_contract=execution_result_contract,
            post_execution_decision_contract=post_execution_contract,
            decision_to_handoff_contract=decision_to_handoff,
            closure_continuation_state_contract=closure_state,
            finalization_closure_record_contract=finalization,
            review_decision={"decision_id": "r1", "review_status": "accept", "validation_status": "passed"},
            approval_result={"approval_id": "a1", "approval_status": "approved"},
        )
        followup = build_gate_outcome_operational_followup_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            finalization_closure_record_contract=finalization,
            review_approval_gate_contract=gate,
        )
        oc_contract = build_operational_continuity_gate_followup_state_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            finalization_closure_record_contract=finalization,
            review_approval_gate_contract=gate,
            gate_outcome_operational_followup_contract=followup,
        )
        slice_d_contract = build_decision_transition_control_contract(
            run_id="run-v1-0-slice-d-1",
            normalized_request=normalized,
            operational_continuity_gate_followup_state_contract=oc_contract,
        )
        self.assertEqual(slice_d_contract["operational_continuity_gate_followup_state_ref"]["contract_id"], oc_contract["contract_id"])
        self.assertEqual(slice_d_contract["operational_continuity_gate_followup_state_ref"]["continuity_state"], "approved_continuity_ready")
        self.assertEqual(slice_d_contract["decision_record"]["source_state_ref"]["contract_id"], oc_contract["contract_id"])
        self.assertEqual(slice_d_contract["transition_record"]["source_state_ref"]["contract_id"], oc_contract["contract_id"])
        self.assertEqual(slice_d_contract["transition_record"]["decision_record_ref"]["record_id"], slice_d_contract["decision_record"]["record_id"])


if __name__ == "__main__":
    unittest.main()
