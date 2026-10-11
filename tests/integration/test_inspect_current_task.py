"""Integration tests for ATP v0.4 Slice D read-only current-task inspect surface."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cli.inspect_task import main as inspect_main
from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_echo.yaml"


class TestInspectCurrentTask(unittest.TestCase):
    """Cover the narrow read-only inspect surface for current-task state."""

    def test_inspect_current_task_reads_materialized_slice_a_b_c_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir) / "SOURCE_DEV" / "workspace"
            with patch(
                "cli.run.validate_artifacts",
                return_value={
                    "request_id": "req-atp-m7-exec-echo-0001",
                    "validation_status": "incomplete",
                    "artifact_ids": ["artifact-authoritative-req-atp-m7-exec-echo-0001"],
                },
            ):
                preview_run(
                    str(FIXTURE_PATH),
                    "run-inspect-1",
                    workspace_root=workspace_root,
                )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = inspect_main(
                    [
                        "--workspace-root",
                        str(workspace_root),
                        "--run-id",
                        "run-inspect-1",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            summary = payload["summary"]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(summary["inspect_mode"], "current_task")
            self.assertEqual(summary["run_id"], "run-inspect-1")
            self.assertEqual(summary["close_or_continue"], "continue_pending")
            self.assertEqual(summary["active_pointer"]["run_id"], "run-inspect-1")
            self.assertFalse(summary["active_pointer"]["superseded_previous"])
            self.assertTrue(summary["recovery_contract"]["recovery_ready"])
            self.assertEqual(summary["recovery_contract"]["recovery_scope"], "continue_pending_current_task")
            self.assertFalse(summary["supersede_trace"]["present"])
            self.assertTrue(summary["current_task_persistence_state_path"].endswith("current-task-state.json"))

    def test_inspect_current_task_surfaces_supersede_trace_for_latest_active_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir) / "SOURCE_DEV" / "workspace"
            with patch(
                "cli.run.validate_artifacts",
                return_value={
                    "request_id": "req-atp-m7-exec-echo-0001",
                    "validation_status": "incomplete",
                    "artifact_ids": ["artifact-authoritative-req-atp-m7-exec-echo-0001"],
                },
            ):
                preview_run(
                    str(FIXTURE_PATH),
                    "run-inspect-prev",
                    workspace_root=workspace_root,
                )
                preview_run(
                    str(FIXTURE_PATH),
                    "run-inspect-next",
                    workspace_root=workspace_root,
                )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = inspect_main(
                    [
                        "--workspace-root",
                        str(workspace_root),
                        "--run-id",
                        "run-inspect-next",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            summary = payload["summary"]
            self.assertEqual(summary["active_pointer"]["run_id"], "run-inspect-next")
            self.assertTrue(summary["active_pointer"]["superseded_previous"])
            self.assertTrue(summary["supersede_trace"]["present"])
            self.assertEqual(summary["supersede_trace"]["previous_run_id"], "run-inspect-prev")
            self.assertEqual(summary["supersede_trace"]["previous_current_task_id"], "current-task-run-inspect-prev")



    def test_inspect_reads_both_the_current_layout_and_the_pre_2_0_4_layout(self) -> None:
        """Runs written by the current writer live under _shared/exchange; runs persisted before 2.0.4 live under exchange/. inspect must find both."""
        import shutil

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir) / "SOURCE_DEV" / "workspace"
            with patch(
                "cli.run.validate_artifacts",
                return_value={
                    "request_id": "req-atp-m7-exec-echo-0001",
                    "validation_status": "incomplete",
                    "artifact_ids": ["artifact-authoritative-req-atp-m7-exec-echo-0001"],
                },
            ):
                preview_run(str(FIXTURE_PATH), "run-inspect-layout", workspace_root=workspace_root)

            def run_inspect() -> tuple[int, dict]:
                out = io.StringIO()
                with redirect_stdout(out):
                    code = inspect_main(["--workspace-root", str(workspace_root), "--run-id", "run-inspect-layout"])
                return code, json.loads(out.getvalue())

            self.assertTrue((workspace_root / "_shared" / "exchange" / "current-task" / "run-inspect-layout").is_dir(), "writer layout changed")
            code, payload = run_inspect()
            self.assertEqual(code, 0)
            self.assertIn("_shared/exchange/current-task", payload["summary"]["exchange_root"])

            legacy = workspace_root / "exchange"
            shutil.move(str(workspace_root / "_shared" / "exchange"), str(legacy))
            code, payload = run_inspect()
            self.assertEqual(code, 0)
            self.assertNotIn("_shared", payload["summary"]["exchange_root"])

            shutil.rmtree(legacy)
            code, payload = run_inspect()
            self.assertEqual(code, 1)
            self.assertIn("_shared/exchange/current-task/run-inspect-layout", payload["error"])
            self.assertIn("exchange/current-task/run-inspect-layout", payload["error"])


if __name__ == "__main__":
    unittest.main()
