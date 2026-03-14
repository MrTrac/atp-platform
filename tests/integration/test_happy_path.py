"""Integration tests for ATP M8 happy path."""

from __future__ import annotations

import unittest
from pathlib import Path

from cli.run import preview_run


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_exec_echo.yaml"


class TestHappyPath(unittest.TestCase):
    """Cover the ATP v0 happy path through finalization."""

    def test_happy_path_closes_run_after_approval(self) -> None:
        preview = preview_run(str(FIXTURE_PATH), "run-happy-1")

        self.assertEqual(preview["execution"]["exit_code"], 0)
        self.assertEqual(preview["validation"]["validation_status"], "passed")
        self.assertEqual(preview["review"]["review_status"], "accept")
        self.assertEqual(preview["approval"]["approval_status"], "approved")
        self.assertEqual(preview["finalization"]["final_status"], "completed")
        self.assertEqual(preview["close_or_continue"], "close")


if __name__ == "__main__":
    unittest.main()
