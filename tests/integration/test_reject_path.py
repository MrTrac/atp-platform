"""Integration tests for ATP M8 reject path plus the v0.5-v0.6 contract chain."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_fail.yaml"


class TestRejectPath(unittest.TestCase):
    """Cover the ATP v0 reject path through finalization."""

    def test_reject_path_closes_as_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            preview = preview_run(
                str(FIXTURE_PATH),
                "run-reject-1",
                workspace_root=Path(temp_dir) / "SOURCE_DEV" / "workspace",
            )

            self.assertNotEqual(preview["execution"]["exit_code"], 0)
            self.assertEqual(preview["validation"]["validation_status"], "failed")
            self.assertEqual(preview["review"]["review_status"], "reject")
            self.assertEqual(preview["approval"]["approval_status"], "rejected")
            self.assertEqual(preview["finalization"]["final_status"], "rejected")
            self.assertEqual(preview["handoff"]["inline_context"]["final_status"], "rejected")
            self.assertEqual(
                preview["handoff"]["evidence_bundle"]["selected_artifacts"],
                [{"artifact_id": "artifact-selected-req-atp-m8-exec-fail-0001", "artifact_type": "execution_output"}],
            )
            self.assertFalse(preview["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(preview["exchange_boundary"]["boundary_mode"], "run_local_handoff")
            self.assertEqual(preview["exchange_boundary"]["exchange_materialization_status"], "not_required")
            self.assertEqual(preview["close_or_continue"], "close_rejected")
            self.assertEqual(preview["run"]["current_stage"], "CLOSED")
            self.assertEqual(preview["request_to_product_resolution"]["resolution_scope"], "request_to_product_only")
            self.assertEqual(preview["request_to_product_resolution"]["product_target"]["product"], "ATP")
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
                preview["product_execution_preparation"]["preparation_scope"],
                "product_execution_preparation_only",
            )
            self.assertEqual(
                preview["product_execution_preparation"]["resolution_to_handoff_intent_ref"]["contract_id"],
                preview["resolution_to_handoff_intent"]["contract_id"],
            )
            self.assertEqual(preview["product_execution_result"]["result_scope"], "product_execution_result_only")
            self.assertEqual(
                preview["product_execution_result"]["product_execution_preparation_ref"]["contract_id"],
                preview["product_execution_preparation"]["contract_id"],
            )
            self.assertEqual(preview["product_execution_result"]["execution_result"]["status"], "failed")
            self.assertEqual(preview["post_execution_decision"]["decision_scope"], "post_execution_decision_only")
            self.assertEqual(
                preview["post_execution_decision"]["product_execution_result_ref"]["contract_id"],
                preview["product_execution_result"]["contract_id"],
            )
            self.assertEqual(
                preview["post_execution_decision"]["post_execution_decision"]["bounded_outcome"],
                "close_rejected",
            )
            self.assertEqual(
                preview["post_execution_decision"]["post_execution_decision"]["review_followup_action"],
                "none",
            )
            run_root = Path(preview["materialization"]["run_root"])
            workspace_root = Path(preview["materialization"]["workspace_root"])
            self.assertTrue((run_root / "manifests" / "request-to-product-resolution-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "resolution-to-handoff-intent-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-preparation-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-result-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "post-execution-decision-contract.json").is_file())
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
