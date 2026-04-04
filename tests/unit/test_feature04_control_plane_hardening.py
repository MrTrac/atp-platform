"""Evidence and contract tests for ATP v1.2 Feature 04 control-plane command hardening."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


class TestFeature04ControlPlaneHardening(unittest.TestCase):
    """Lock one bounded control-plane command hardening improvement."""

    def test_root_help_distinguishes_control_plane_preparation_commands(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Bounded control-plane preparation commands:", result.stdout)
        self.assertIn(
            "run             Preview one bounded ATP v0 control-plane run surface from an explicit request file.",
            result.stdout,
        )
        self.assertIn(
            "control-plane -> preview/read-only surfaces only; no background execution or autonomous progression",
            result.stdout,
        )

    def test_run_help_has_repo_root_bounded_control_guidance(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT_DIR / "cli" / "run.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Preview one bounded ATP v0 control-plane run surface from an explicit request file only.",
            result.stdout,
        )
        self.assertIn(f"./atp run tests/fixtures/requests/sample_request_slice02.yaml", result.stdout)
        self.assertIn("repo-local preview surface only", result.stdout)

    def test_validate_help_has_repo_root_bounded_control_guidance(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT_DIR / "cli" / "validate.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Preview bounded ATP v0 validation readiness from an explicit request file only.",
            result.stdout,
        )
        self.assertIn(f"./atp validate tests/fixtures/requests/sample_request_slice02.yaml", result.stdout)

    def test_inspect_help_is_explicitly_read_only(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT_DIR / "cli" / "inspect.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Inspect bounded ATP preview summaries or read-only current-task state only.", result.stdout)
        self.assertIn("This command is read-only.", result.stdout)

    def test_root_help_does_not_imply_automation_or_background_control(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("auto-execute  -> disabled", result.stdout)
        self.assertIn(
            "control-plane -> preview/read-only surfaces only; no background execution or autonomous progression",
            result.stdout,
        )
        self.assertNotIn("scheduler", result.stdout.lower())
        self.assertNotIn("daemon", result.stdout.lower())

    def test_smoke_request_chain_still_passes_after_control_plane_hardening(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
