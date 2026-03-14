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
            self.assertTrue(preview["continuation"]["continuation_required"])
            self.assertEqual(preview["continuation"]["continuity_status"], "continuation_pending")
            self.assertEqual(preview["continuation"]["current_source"], "exchange_current_task")

            run_root = Path(preview["materialization"]["run_root"])
            exchange_root = Path(preview["materialization"]["exchange"]["exchange_root"])
            self.assertTrue((run_root / "final" / "continuation-state.json").is_file())
            self.assertTrue((exchange_root / "exchange-bundle.json").is_file())
            self.assertTrue((exchange_root / "exchange-metadata.json").is_file())


if __name__ == "__main__":
    unittest.main()
