"""Integration tests for ATP M8 happy path."""

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
            run_root = Path(preview["materialization"]["run_root"])
            workspace_root = Path(preview["materialization"]["workspace_root"])
            self.assertTrue(run_root.is_dir())
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
