"""Evidence and contract tests for ATP v1.2 Feature 04 control-plane command hardening."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


class TestFeature04ControlPlaneHardening(unittest.TestCase):
    """Capture one concrete control-plane command ambiguity before hardening it."""

    def test_root_help_currently_groups_control_plane_commands_too_generically(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Other commands:", result.stdout)
        self.assertIn("run             Run ATP control-plane execution surfaces.", result.stdout)

    def test_run_help_currently_lacks_repo_root_bounded_control_guidance(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT_DIR / "cli" / "run.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Preview the ATP M1-M8 run flow.", result.stdout)
        self.assertNotIn("./atp run", result.stdout)
        self.assertNotIn("control-plane preview only", result.stdout)


if __name__ == "__main__":
    unittest.main()
