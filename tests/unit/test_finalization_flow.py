"""Unit tests for ATP M8 approval, handoff, and finalization flow."""

from __future__ import annotations

import unittest

from core.approvals.approval_gate import require_approval
from core.finalization.close_or_continue import close_or_continue
from core.finalization.finalize import derive_final_status, finalize_run
from core.handoff.continuation_state import build_continuation_state
from core.handoff.exchange_boundary import build_exchange_boundary_decision
from core.handoff.inline_context import build_inline_context
from core.handoff.manifest_reference import build_manifest_reference


class TestFinalizationFlow(unittest.TestCase):
    """Cover minimal ATP v0 finalization rules."""

    def test_inline_context_returns_stable_essential_fields(self) -> None:
        inline_context = build_inline_context(
            summary="ATP run completed",
            request_id="req-1",
            product="ATP",
            final_status="completed",
            review_status="accept",
            authoritative=True,
        )

        self.assertEqual(inline_context["handoff_type"], "inline_context")
        self.assertEqual(inline_context["request_id"], "req-1")

    def test_manifest_reference_structure_is_stable(self) -> None:
        manifest_reference = build_manifest_reference("artifact-1", "task-manifest-req-1", "ATP")

        self.assertEqual(manifest_reference["handoff_type"], "manifest_reference")
        self.assertEqual(manifest_reference["product"], "ATP")

    def test_close_or_continue_logic_follows_minimal_rules(self) -> None:
        self.assertEqual(close_or_continue({"approval_status": "approved"}), "close")
        self.assertEqual(close_or_continue({"approval_status": "needs_attention"}), "continue_pending")
        self.assertEqual(close_or_continue({"approval_status": "rejected"}), "close_rejected")

    def test_exchange_boundary_decision_marks_only_continue_pending_as_external_candidate(self) -> None:
        continue_decision = build_exchange_boundary_decision(
            run_id="run-1",
            request_id="req-1",
            close_decision="continue_pending",
            handoff_outputs={
                "evidence_bundle": {"bundle_id": "handoff-evidence-req-1"},
                "manifest_reference": {"manifest_reference": "task-manifest-req-1"},
            },
        )
        close_decision = build_exchange_boundary_decision(
            run_id="run-2",
            request_id="req-2",
            close_decision="close",
            handoff_outputs={
                "evidence_bundle": {"bundle_id": "handoff-evidence-req-2"},
                "manifest_reference": {"manifest_reference": "task-manifest-req-2"},
            },
        )

        self.assertTrue(continue_decision["requires_exchange_boundary"])
        self.assertEqual(continue_decision["boundary_mode"], "external_exchange_candidate")
        self.assertEqual(continue_decision["exchange_materialization_status"], "deferred")
        self.assertFalse(close_decision["requires_exchange_boundary"])
        self.assertEqual(close_decision["boundary_mode"], "run_local_handoff")

    def test_continuation_state_uses_exchange_current_task_for_continue_pending(self) -> None:
        state = build_continuation_state(
            run_id="run-1",
            request_id="req-1",
            close_decision="continue_pending",
            exchange_boundary_decision={
                "decision_id": "exchange-boundary-run-1",
                "boundary_mode": "external_exchange_candidate",
                "exchange_materialization_status": "materialized_current_task",
            },
            exchange_summary={
                "materialized": True,
                "exchange_root": "/tmp/SOURCE_DEV/workspace/exchange/current-task/run-1",
            },
            handoff_outputs={
                "evidence_bundle": {
                    "bundle_id": "handoff-evidence-req-1",
                    "selected_artifacts": [{"artifact_id": "artifact-selected-req-1", "artifact_type": "execution_output"}],
                    "authoritative_refs": [{"artifact_id": "artifact-authoritative-req-1", "artifact_type": "execution_output"}],
                },
                "manifest_reference": {"manifest_reference": "task-manifest-req-1"},
                "exchange_bundle": {"exchange_id": "exchange-req-1"},
            },
        )

        self.assertTrue(state["continuation_required"])
        self.assertEqual(state["continuity_status"], "continuation_pending")
        self.assertEqual(state["current_source"], "exchange_current_task")
        self.assertEqual(state["continuity_refs"]["exchange_bundle_id"], "exchange-req-1")

    def test_continuation_state_for_closed_run_does_not_require_current_exchange_reference(self) -> None:
        state = build_continuation_state(
            run_id="run-2",
            request_id="req-2",
            close_decision="close",
            exchange_boundary_decision={
                "decision_id": "exchange-boundary-run-2",
                "boundary_mode": "run_local_handoff",
                "exchange_materialization_status": "not_required",
            },
            exchange_summary={
                "materialized": False,
                "exchange_root": "",
            },
            handoff_outputs={
                "evidence_bundle": {"bundle_id": "handoff-evidence-req-2"},
                "manifest_reference": {"manifest_reference": "task-manifest-req-2"},
                "exchange_bundle": {"exchange_id": "exchange-req-2"},
            },
        )

        self.assertFalse(state["continuation_required"])
        self.assertEqual(state["current_source"], "none")
        self.assertEqual(state["continuity_refs"]["exchange_root"], "")

    def test_derive_final_status_keeps_finalization_vocabulary_stable(self) -> None:
        self.assertEqual(derive_final_status({"approval_status": "approved"}), "completed")
        self.assertEqual(derive_final_status({"approval_status": "rejected"}), "rejected")
        self.assertEqual(derive_final_status({"approval_status": "needs_attention"}), "attention_required")

    def test_finalization_closes_approved_run(self) -> None:
        approval = require_approval(
            {"request_id": "req-1", "validation_status": "passed"},
            {"request_id": "req-1", "review_status": "accept"},
            {"artifact_ids": ["artifact-1"], "authoritative_artifacts": [{"artifact_id": "artifact-1", "artifact_type": "execution_output"}]},
        )
        finalization = finalize_run(
            execution_result={"request_id": "req-1", "selected_provider": "non_llm_execution", "selected_node": "local_mac"},
            artifact_summary={"authoritative_artifacts": [{"artifact_id": "artifact-1", "artifact_type": "execution_output"}]},
            validation_summary={"validation_status": "passed"},
            review_decision={"review_status": "accept"},
            approval_result=approval,
            handoff_outputs={
                "inline_context": {"handoff_type": "inline_context"},
                "evidence_bundle": {"bundle_id": "bundle-1"},
                "exchange_bundle": {"exchange_id": "exchange-1"},
                "manifest_reference": {"manifest_reference": "task-manifest-req-1"},
            },
        )

        self.assertEqual(finalization["final_status"], "completed")
        self.assertEqual(finalization["approval_status"], "approved")


if __name__ == "__main__":
    unittest.main()
