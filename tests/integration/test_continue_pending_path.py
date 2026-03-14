"""Integration tests for ATP continue-pending continuity behavior."""

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
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["materialized"])
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["persistence_state_path"].endswith("current-task-state.json"))
            self.assertTrue(preview["reference_index"]["exchange_current_task"]["active_pointer_path"].endswith("active-pointer.json"))
            self.assertEqual(preview["reference_index"]["exchange_current_task"]["supersede_trace_path"], "")
            self.assertTrue(preview["reference_index"]["continuation"]["recovery_contract_path"].endswith("continue-pending-recovery.json"))
            self.assertEqual(preview["reference_index"]["continuation"]["current_source"], "exchange_current_task")

            run_root = Path(preview["materialization"]["run_root"])
            exchange_root = Path(preview["materialization"]["exchange"]["exchange_root"])
            self.assertTrue((run_root / "manifests" / "request-to-product-resolution-contract.json").is_file())
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
