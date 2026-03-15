"""Unit tests for ATP v1.0 Slice D decision/transition contract shape and validation."""

from __future__ import annotations

import unittest

from core.decision_control.slice_d_contract import (
    DECISION_CLASSES,
    DECISION_RESULTS,
    TRANSITION_CLASSES,
    SliceDContractError,
    build_decision_record,
    build_transition_record,
    validate_decision_record,
    validate_transition_record,
)


def _minimal_slice_c_contract(request_id: str = "req-1", run_id: str = "run-1") -> dict:
    """Minimal Slice C continuity state contract for use as source_state in Slice D."""
    return {
        "contract_id": f"operational-continuity-gate-followup-state-{request_id}",
        "contract_version": "v1.0-slice-c",
        "request_id": request_id,
        "run_id": run_id,
        "state_scope": "operational_continuity_gate_followup_state_only",
        "operational_continuity_state": {
            "state_stage": "post_gate_operational_continuity",
            "continuity_state": "approved_continuity_ready",
            "state_status": "continuity_ready",
            "continuity_signal": "continue",
            "close_or_continue": "continue",
        },
    }


def _valid_source_state_ref() -> dict:
    """Source state ref that passes Slice C contract_id/state_scope/continuity_state validation."""
    return {
        "contract_id": "operational-continuity-gate-followup-state-req-1",
        "state_scope": "operational_continuity_gate_followup_state_only",
        "continuity_state": "approved_continuity_ready",
    }


class TestSliceDDecisionRecord(unittest.TestCase):
    """Decision record shape and validation."""

    def test_build_decision_record_valid(self) -> None:
        oc = _minimal_slice_c_contract()
        rec = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="gate_authority",
            decision_authority="approval_gate",
            decision_class="conditional_binding_decision",
            rationale_summary="Continuity ready; allow next transition.",
            evidence_summary="Gate outcome approved.",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        self.assertEqual(rec["record_id"], "decision-req-1-run-1")
        self.assertEqual(rec["contract_version"], "v1.0-slice-d")
        self.assertEqual(rec["decision_class"], "conditional_binding_decision")
        self.assertEqual(rec["decision_result"], "allow")
        self.assertEqual(rec["permission_block_result"], "allow")
        self.assertIn("source_state_ref", rec)
        self.assertEqual(rec["source_state_ref"]["contract_id"], oc["contract_id"])
        self.assertEqual(rec["source_state_ref"]["continuity_state"], "approved_continuity_ready")
        validate_decision_record(rec)

    def test_validate_decision_record_accepts_built_record(self) -> None:
        oc = _minimal_slice_c_contract()
        rec = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="actor",
            decision_authority="authority",
            decision_class="advisory_decision",
            rationale_summary="Advisory only.",
            evidence_summary="Evidence present.",
            requested_transition="conditional_transition",
            decision_result="conditional",
        )
        validate_decision_record(rec)

    def test_validate_decision_record_rejects_missing_record_id(self) -> None:
        oc = _minimal_slice_c_contract()
        rec = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="a",
            decision_authority="b",
            decision_class="observational_decision",
            rationale_summary="r",
            evidence_summary="e",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        del rec["record_id"]
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(rec)
        self.assertIn("record_id", str(ctx.exception))

    def test_validate_decision_record_rejects_invalid_decision_class(self) -> None:
        rec = {
            "record_id": "dec-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "a",
            "decision_authority": "b",
            "decision_class": "invalid_class",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "allowed_transition",
            "decision_result": "allow",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(rec)
        self.assertIn("decision_class", str(ctx.exception))

    def test_validate_decision_record_rejects_invalid_decision_result(self) -> None:
        rec = {
            "record_id": "dec-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_actor": "a",
            "decision_authority": "b",
            "decision_class": "blocking_decision",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "blocked_transition",
            "decision_result": "invalid_result",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(rec)
        self.assertIn("decision_result", str(ctx.exception))

    def test_validate_decision_record_rejects_missing_source_state_ref(self) -> None:
        rec = {
            "record_id": "dec-1",
            "decision_actor": "a",
            "decision_authority": "b",
            "decision_class": "advisory_decision",
            "rationale_summary": "r",
            "evidence_summary": "e",
            "requested_transition": "deferred_transition",
            "decision_result": "defer",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_decision_record(rec)
        self.assertIn("source_state_ref", str(ctx.exception))

    def test_build_decision_record_rejects_invalid_decision_class(self) -> None:
        oc = _minimal_slice_c_contract()
        with self.assertRaises(SliceDContractError):
            build_decision_record(
                request_id="req-1",
                run_id="run-1",
                operational_continuity_state_contract=oc,
                decision_actor="a",
                decision_authority="b",
                decision_class="invalid",
                rationale_summary="r",
                evidence_summary="e",
                requested_transition="allow",
                decision_result="allow",
            )

    def test_build_decision_record_requires_slice_c_contract_id(self) -> None:
        bad_oc = {"state_scope": "x"}
        with self.assertRaises(SliceDContractError) as ctx:
            build_decision_record(
                request_id="req-1",
                run_id="run-1",
                operational_continuity_state_contract=bad_oc,
                decision_actor="a",
                decision_authority="b",
                decision_class="observational_decision",
                rationale_summary="r",
                evidence_summary="e",
                requested_transition="allowed_transition",
                decision_result="allow",
            )
        self.assertIn("contract_id", str(ctx.exception))


class TestSliceDTransitionRecord(unittest.TestCase):
    """Transition record shape and validation."""

    def test_build_transition_record_valid(self) -> None:
        oc = _minimal_slice_c_contract()
        decision = build_decision_record(
            request_id="req-1",
            run_id="run-1",
            operational_continuity_state_contract=oc,
            decision_actor="gate",
            decision_authority="approval",
            decision_class="conditional_binding_decision",
            rationale_summary="Allow.",
            evidence_summary="Evidence.",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        source_ref = {
            "contract_id": oc["contract_id"],
            "state_scope": oc["state_scope"],
            "continuity_state": oc["operational_continuity_state"]["continuity_state"],
        }
        trans = build_transition_record(
            request_id="req-1",
            run_id="run-1",
            source_state_ref=source_ref,
            decision_record=decision,
            transition_class="allowed_transition",
            permission_block_basis="decision_result_allow",
            resulting_state_or_move="next_operational_state",
            status_summary="transition_applied",
        )
        self.assertEqual(trans["record_id"], "transition-req-1-run-1")
        self.assertEqual(trans["transition_class"], "allowed_transition")
        self.assertEqual(trans["decision_record_ref"]["record_id"], decision["record_id"])
        self.assertEqual(trans["resulting_state_or_move"], "next_operational_state")
        validate_transition_record(trans)

    def test_validate_transition_record_rejects_missing_decision_record_ref(self) -> None:
        trans = {
            "record_id": "t-1",
            "source_state_ref": _valid_source_state_ref(),
            "transition_class": "blocked_transition",
            "permission_block_basis": "block",
            "resulting_state_or_move": "no_move",
            "status_summary": "blocked",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_transition_record(trans)
        self.assertIn("decision_record_ref", str(ctx.exception))

    def test_validate_transition_record_rejects_invalid_transition_class(self) -> None:
        trans = {
            "record_id": "t-1",
            "source_state_ref": _valid_source_state_ref(),
            "decision_record_ref": {
                "record_id": "dec-1",
                "decision_class": "conditional_binding_decision",
                "decision_result": "allow",
            },
            "transition_class": "invalid_transition",
            "permission_block_basis": "basis",
            "resulting_state_or_move": "state",
            "status_summary": "ok",
        }
        with self.assertRaises(SliceDContractError) as ctx:
            validate_transition_record(trans)
        self.assertIn("transition_class", str(ctx.exception))

    def test_build_transition_record_rejects_missing_decision_record_id(self) -> None:
        with self.assertRaises(SliceDContractError) as ctx:
            build_transition_record(
                request_id="req-1",
                run_id="run-1",
                source_state_ref={"contract_id": "oc-1"},
                decision_record={},
                transition_class="allowed_transition",
                permission_block_basis="basis",
                resulting_state_or_move="next",
                status_summary="ok",
            )
        self.assertIn("record_id", str(ctx.exception))


class TestSliceDTraceabilityLinkage(unittest.TestCase):
    """Traceability: source state -> decision -> transition -> resulting state."""

    def test_chain_linkage(self) -> None:
        oc = _minimal_slice_c_contract("req-2", "run-2")
        decision = build_decision_record(
            request_id="req-2",
            run_id="run-2",
            operational_continuity_state_contract=oc,
            decision_actor="authority",
            decision_authority="level_1",
            decision_class="conditional_binding_decision",
            rationale_summary="Rationale.",
            evidence_summary="Evidence.",
            requested_transition="allowed_transition",
            decision_result="allow",
        )
        source_ref = decision["source_state_ref"]
        trans = build_transition_record(
            request_id="req-2",
            run_id="run-2",
            source_state_ref=source_ref,
            decision_record=decision,
            transition_class="allowed_transition",
            permission_block_basis="allow",
            resulting_state_or_move="resulting_state",
            status_summary="applied",
        )
        self.assertEqual(trans["source_state_ref"]["contract_id"], oc["contract_id"])
        self.assertEqual(trans["decision_record_ref"]["record_id"], decision["record_id"])
        self.assertEqual(trans["resulting_state_or_move"], "resulting_state")
        validate_decision_record(decision)
        validate_transition_record(trans)


class TestSliceDEnums(unittest.TestCase):
    """Decision and transition class enums match contract."""

    def test_decision_classes_match_contract(self) -> None:
        expected = {
            "observational_decision",
            "advisory_decision",
            "conditional_binding_decision",
            "blocking_decision",
        }
        self.assertEqual(DECISION_CLASSES, expected)

    def test_decision_results_match_contract(self) -> None:
        expected = {"allow", "conditional", "defer", "block", "loop_back"}
        self.assertEqual(DECISION_RESULTS, expected)

    def test_transition_classes_match_contract(self) -> None:
        expected = {
            "allowed_transition",
            "conditional_transition",
            "deferred_transition",
            "blocked_transition",
            "loop_back_transition",
        }
        self.assertEqual(TRANSITION_CLASSES, expected)


if __name__ == "__main__":
    unittest.main()
