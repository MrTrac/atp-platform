"""Unit tests for ATP v1.1 Slice 09 repo-local invocation surface hardening."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


class TestSlice09InvocationSurface(unittest.TestCase):
    """Lock the bounded repo-root launcher contract."""

    def test_repo_root_launcher_delegates_to_canonical_cli_help(self) -> None:
        root_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
        )
        cli_result = subprocess.run(
            [str(ROOT_DIR / "cli" / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(root_result.returncode, 0)
        self.assertEqual(cli_result.returncode, 0)
        self.assertEqual(root_result.stdout, cli_result.stdout)

    def test_repo_root_launcher_supports_request_chain_command(self) -> None:
        result = subprocess.run(
            [
                str(ROOT_DIR / "atp"),
                "request-flow",
                "tests/fixtures/requests/sample_request_slice02.yaml",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('"command": "request-flow"', result.stdout)
        self.assertIn('"status": "ok"', result.stdout)
        self.assertIn('"review_summary"', result.stdout)


if __name__ == "__main__":
    unittest.main()
