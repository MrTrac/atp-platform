"""Integration tests for ATP M8 happy path plus the v0.5-v0.6 foundational contract chain."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_echo.yaml"


class TestHappyPath(unittest.TestCase):
    """Cover the ATP v0 happy path through finalization."""

    def test_happy_path_closes_run_after_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            preview = preview_run(
                str(FIXTURE_PATH),
                "run-happy-1",
                workspace_root=Path(temp_dir) / "SOURCE_DEV" / "workspace",
            )

            self.assertEqual(preview["execution"]["exit_code"], 0)
            self.assertEqual(preview["validation"]["validation_status"], "passed")
            self.assertEqual(preview["review"]["review_status"], "accept")
            self.assertEqual(preview["approval"]["approval_status"], "approved")
            self.assertEqual(preview["finalization"]["final_status"], "completed")
            self.assertEqual(preview["handoff"]["inline_context"]["final_status"], "completed")
            self.assertEqual(
                preview["handoff"]["evidence_bundle"]["selected_artifacts"],
                [{"artifact_id": "artifact-selected-req-atp-m7-exec-echo-0001", "artifact_type": "execution_output"}],
            )
            self.assertFalse(preview["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(preview["exchange_boundary"]["boundary_mode"], "run_local_handoff")
            self.assertEqual(preview["exchange_boundary"]["exchange_materialization_status"], "not_required")
            self.assertEqual(preview["close_or_continue"], "close")
            self.assertEqual(preview["run"]["current_stage"], "CLOSED")
            self.assertEqual(preview["request_to_product_resolution"]["resolution_scope"], "request_to_product_only")
            self.assertEqual(preview["request_to_product_resolution"]["product_target"]["product"], "ATP")
            self.assertEqual(preview["request_to_product_resolution"]["capability_target"]["capability"], "shell_execution")
            self.assertEqual(preview["request_to_product_resolution"]["capability_target"]["source"], "classification.capability")
            self.assertEqual(preview["resolution_to_handoff_intent"]["handoff_scope"], "resolution_to_handoff_only")
            self.assertEqual(
                preview["resolution_to_handoff_intent"]["request_to_product_resolution_ref"]["contract_id"],
                preview["request_to_product_resolution"]["contract_id"],
            )
            self.assertEqual(
                preview["resolution_to_handoff_intent"]["handoff_intent"]["intent"],
                "prepare_structured_product_handoff",
            )
            self.assertEqual(preview["resolution_to_handoff_intent"]["handoff_intent"]["target_product"], "ATP")
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
            self.assertEqual(
                preview["product_execution_preparation"]["execution_preparation"]["target_product"],
                "ATP",
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
            self.assertEqual(preview["post_execution_decision"]["post_execution_decision"]["bounded_outcome"], "close")
            self.assertEqual(
                preview["post_execution_decision"]["post_execution_decision"]["review_followup_action"],
                "none",
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
                "close",
            )
            self.assertEqual(
                preview["decision_to_closure_continuation_handoff"]["closure_or_continuation_handoff"][
                    "review_escalation_mode"
                ],
                "none",
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
                "close",
            )
            self.assertEqual(
                preview["closure_continuation_state"]["closure_or_continuation_state"]["state_status"],
                "closed",
            )
            run_root = Path(preview["materialization"]["run_root"])
            workspace_root = Path(preview["materialization"]["workspace_root"])
            self.assertTrue(run_root.is_dir())
            self.assertTrue((run_root / "manifests" / "request-to-product-resolution-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "resolution-to-handoff-intent-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-preparation-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-result-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "post-execution-decision-contract.json").is_file())
            self.assertTrue(
                (run_root / "manifests" / "decision-to-closure-continuation-handoff-contract.json").is_file()
            )
            self.assertTrue((run_root / "manifests" / "closure-continuation-state-contract.json").is_file())
            self.assertTrue((run_root / "decisions" / "exchange-boundary-decision.json").is_file())
            self.assertTrue((run_root / "handoff" / "inline-context.json").is_file())
            self.assertTrue((run_root / "handoff" / "evidence-bundle.json").is_file())
            self.assertTrue((run_root / "handoff" / "manifest-reference.json").is_file())
            projection = preview["materialization"]["authoritative_projection"]
            self.assertEqual(projection["projected_count"], 1)
            projection_root = Path(projection["items"][0]["projection_root"])
            self.assertTrue((projection_root / "artifact.json").is_file())
            self.assertTrue((projection_root / "projection-metadata.json").is_file())
            self.assertEqual(preview["materialization"]["retention"]["cleanup_mode"], "manual_review_only")
            self.assertEqual(preview["materialization"]["retention"]["cleanup_actions"], [])
            self.assertTrue((run_root / "final" / "retention-summary.json").is_file())
            self.assertTrue((run_root / "logs" / "cleanup.log").is_file())
            self.assertTrue((run_root / "final" / "reference-index.json").is_file())
            self.assertFalse((run_root / "exchange").exists())
            self.assertFalse((workspace_root / "exchange").exists())
            self.assertFalse(preview["reference_index"]["exchange_current_task"]["materialized"])


if __name__ == "__main__":
    unittest.main()
