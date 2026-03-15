"""Integration tests for ATP continue-pending continuity plus the v0.5-v1.0 contract chain."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_echo.yaml"


class TestContinuePendingPath(unittest.TestCase):
    """Cover minimal continue_pending operational continuity."""

    def test_continue_pending_materializes_exchange_and_continuation_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "cli.run.validate_artifacts",
                return_value={
                    "request_id": "req-atp-m7-exec-echo-0001",
                    "validation_status": "incomplete",
                    "artifact_ids": ["artifact-authoritative-req-atp-m7-exec-echo-0001"],
                },
            ):
                preview = preview_run(
                    str(FIXTURE_PATH),
                    "run-continue-1",
                    workspace_root=Path(temp_dir) / "SOURCE_DEV" / "workspace",
                )

            self.assertEqual(preview["approval"]["approval_status"], "needs_attention")
            self.assertEqual(preview["close_or_continue"], "continue_pending")
            self.assertTrue(preview["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(preview["exchange_boundary"]["exchange_materialization_status"], "materialized_current_task")
            self.assertTrue(preview["materialization"]["exchange"]["materialized"])
            self.assertTrue(preview["current_task_persistence"]["persisted"])
            self.assertEqual(preview["current_task_persistence"]["persistence_scope"], "workspace_exchange_current_task")
            self.assertTrue(preview["recovery_contract"]["recovery_ready"])
            self.assertEqual(preview["recovery_contract"]["recovery_scope"], "continue_pending_current_task")
            self.assertTrue(preview["current_task_pointer"]["active_pointer_written"])
            self.assertFalse(preview["current_task_pointer"]["superseded_previous"])
            self.assertTrue(preview["continuation"]["continuation_required"])
            self.assertEqual(preview["continuation"]["continuity_status"], "continuation_pending")
            self.assertEqual(preview["continuation"]["current_source"], "exchange_current_task")
            self.assertEqual(preview["request_to_product_resolution"]["resolution_scope"], "request_to_product_only")
            self.assertEqual(preview["request_to_product_resolution"]["product_target"]["product"], "ATP")
            self.assertEqual(preview["request_to_product_resolution"]["capability_target"]["capability"], "shell_execution")
            self.assertEqual(preview["request_to_product_resolution"]["capability_target"]["source"], "classification.capability")
            self.assertEqual(
                preview["request_to_product_resolution"]["resolution_rationale"]["product_source"],
                "normalized_request.product",
            )
            self.assertEqual(preview["resolution_to_handoff_intent"]["handoff_scope"], "resolution_to_handoff_only")
            self.assertEqual(
                preview["resolution_to_handoff_intent"]["request_to_product_resolution_ref"]["contract_id"],
                preview["request_to_product_resolution"]["contract_id"],
            )
            self.assertEqual(
                preview["resolution_to_handoff_intent"]["handoff_intent"]["intent"],
                "prepare_structured_product_handoff",
            )
            self.assertEqual(
                preview["resolution_to_handoff_intent"]["handoff_intent"]["target_capability"],
                "shell_execution",
            )
            self.assertEqual(
                preview["product_execution_preparation"]["preparation_scope"],
                "product_execution_preparation_only",
            )
            self.assertEqual(
                preview["product_execution_preparation"]["request_to_product_resolution_ref"]["contract_id"],
                preview["request_to_product_resolution"]["contract_id"],
            )
            self.assertEqual(
                preview["product_execution_preparation"]["resolution_to_handoff_intent_ref"]["contract_id"],
                preview["resolution_to_handoff_intent"]["contract_id"],
            )
            self.assertEqual(
                preview["product_execution_preparation"]["execution_preparation"]["preparation_mode"],
                "pre_routing_pre_provider",
            )
            self.assertEqual(preview["product_execution_result"]["result_scope"], "product_execution_result_only")
            self.assertEqual(
                preview["product_execution_result"]["request_to_product_resolution_ref"]["contract_id"],
                preview["request_to_product_resolution"]["contract_id"],
            )
            self.assertEqual(
                preview["product_execution_result"]["resolution_to_handoff_intent_ref"]["contract_id"],
                preview["resolution_to_handoff_intent"]["contract_id"],
            )
            self.assertEqual(
                preview["product_execution_result"]["product_execution_preparation_ref"]["contract_id"],
                preview["product_execution_preparation"]["contract_id"],
            )
            self.assertEqual(preview["product_execution_result"]["execution_result"]["status"], "succeeded")
            self.assertEqual(preview["post_execution_decision"]["decision_scope"], "post_execution_decision_only")
            self.assertEqual(
                preview["post_execution_decision"]["product_execution_result_ref"]["contract_id"],
                preview["product_execution_result"]["contract_id"],
            )
            self.assertEqual(
                preview["post_execution_decision"]["post_execution_decision"]["bounded_outcome"],
                "continue_pending",
            )
            self.assertEqual(
                preview["post_execution_decision"]["post_execution_decision"]["review_followup_action"],
                "escalate_review",
            )
            self.assertEqual(
                preview["decision_to_closure_continuation_handoff"]["handoff_scope"],
                "decision_to_closure_continuation_only",
            )
            self.assertEqual(
                preview["decision_to_closure_continuation_handoff"]["post_execution_decision_ref"]["contract_id"],
                preview["post_execution_decision"]["contract_id"],
            )
            self.assertEqual(
                preview["decision_to_closure_continuation_handoff"]["closure_or_continuation_handoff"][
                    "bounded_next_path"
                ],
                "continue_pending",
            )
            self.assertEqual(
                preview["decision_to_closure_continuation_handoff"]["closure_or_continuation_handoff"][
                    "review_escalation_mode"
                ],
                "escalate_review",
            )
            self.assertEqual(
                preview["closure_continuation_state"]["state_scope"],
                "closure_continuation_state_only",
            )
            self.assertEqual(
                preview["closure_continuation_state"]["decision_to_closure_continuation_handoff_ref"]["contract_id"],
                preview["decision_to_closure_continuation_handoff"]["contract_id"],
            )
            self.assertEqual(
                preview["closure_continuation_state"]["closure_or_continuation_state"]["bounded_path"],
                "continue_pending",
            )
            self.assertEqual(
                preview["closure_continuation_state"]["closure_or_continuation_state"]["state_status"],
                "continuation_pending",
            )
            self.assertTrue(
                preview["closure_continuation_state"]["closure_or_continuation_state"]["continuation_required"]
            )
            self.assertEqual(
                preview["finalization_closure_record"]["record_scope"],
                "finalization_closure_record_only",
            )
            self.assertEqual(
                preview["finalization_closure_record"]["closure_continuation_state_ref"]["contract_id"],
                preview["closure_continuation_state"]["contract_id"],
            )
            self.assertEqual(
                preview["finalization_closure_record"]["finalization_or_closure_record"]["bounded_path"],
                "continue_pending",
            )
            self.assertEqual(
                preview["finalization_closure_record"]["finalization_or_closure_record"]["record_status"],
                "continuation_record_finalized",
            )
            self.assertEqual(
                preview["finalization_closure_record"]["finalization_or_closure_record"]["final_status"],
                "attention_required",
            )
            self.assertEqual(
                preview["review_approval_gate"]["gate_scope"],
                "review_approval_gate_only",
            )
            self.assertEqual(
                preview["review_approval_gate"]["finalization_closure_record_ref"]["contract_id"],
                preview["finalization_closure_record"]["contract_id"],
            )
            self.assertEqual(
                preview["review_approval_gate"]["review_or_approval_gate"]["gate_decision"],
                "hold",
            )
            self.assertEqual(
                preview["gate_outcome_operational_followup"]["followup_scope"],
                "gate_outcome_operational_followup_only",
            )
            self.assertEqual(
                preview["gate_outcome_operational_followup"]["review_approval_gate_ref"]["contract_id"],
                preview["review_approval_gate"]["contract_id"],
            )
            self.assertEqual(
                preview["gate_outcome_operational_followup"]["gate_outcome_or_operational_followup"][
                    "bounded_followup"
                ],
                "held_operational_followup",
            )
            self.assertEqual(
                preview["operational_continuity_gate_followup_state"]["state_scope"],
                "operational_continuity_gate_followup_state_only",
            )
            self.assertEqual(
                preview["operational_continuity_gate_followup_state"]["gate_outcome_operational_followup_ref"][
                    "contract_id"
                ],
                preview["gate_outcome_operational_followup"]["contract_id"],
            )
            self.assertEqual(
                preview["operational_continuity_gate_followup_state"]["operational_continuity_state"][
                    "continuity_state"
                ],
                "held_continuity_pending",
            )
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["materialized"])
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["persistence_state_path"].endswith("current-task-state.json"))
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["active_pointer_path"].endswith("active-pointer.json"))
            self.assertEqual(preview["reference_index"]["exchange_current_task"]["supersede_trace_path"], "")
            self.assertTrue(preview["reference_index"]["continuation"]["recovery_contract_path"].endswith("continue-pending-recovery.json"))
            self.assertEqual(preview["reference_index"]["continuation"]["current_source"], "exchange_current_task")

            run_root = Path(preview["materialization"]["run_root"])
            exchange_root = Path(preview["materialization"]["exchange"]["exchange_root"])
            self.assertTrue((run_root / "manifests" / "request-to-product-resolution-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "resolution-to-handoff-intent-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-preparation-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-result-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "post-execution-decision-contract.json").is_file())
            self.assertTrue(
                (run_root / "manifests" / "decision-to-closure-continuation-handoff-contract.json").is_file()
            )
            self.assertTrue((run_root / "manifests" / "closure-continuation-state-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "finalization-closure-record-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "review-approval-gate-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "gate-outcome-operational-followup-contract.json").is_file())
            self.assertTrue(
                (run_root / "manifests" / "operational-continuity-gate-followup-state-contract.json").is_file()
            )
            self.assertTrue((run_root / "final" / "continuation-state.json").is_file())
            self.assertTrue((run_root / "final" / "reference-index.json").is_file())
            self.assertTrue((exchange_root / "exchange-bundle.json").is_file())
            self.assertTrue((exchange_root / "exchange-metadata.json").is_file())
            self.assertTrue((exchange_root / "current.json").is_file())
            self.assertTrue((exchange_root / "current-task-state.json").is_file())
            self.assertTrue((exchange_root / "continue-pending-recovery.json").is_file())
            self.assertTrue((exchange_root.parent / "active-pointer.json").is_file())


if __name__ == "__main__":
    unittest.main()
