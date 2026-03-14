"""Integration tests for ATP M8 reject path."""

from __future__ import annotations

import unittest
from pathlib import Path

from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_fail.yaml"


class TestRejectPath(unittest.TestCase):
    """Cover the ATP v0 reject path through finalization."""

    def test_reject_path_closes_as_rejected(self) -> None:
        preview = preview_run(str(FIXTURE_PATH), "run-reject-1")

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
        self.assertEqual(preview["close_or_continue"], "close_rejected")
        self.assertEqual(preview["run"]["current_stage"], "CLOSED")


if __name__ == "__main__":
    unittest.main()
