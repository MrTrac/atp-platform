"""Unit tests for ATP v1.1 Slice 10 smoke-verification hardening."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestSlice10SmokeVerification(unittest.TestCase):
    """Lock the bounded repo-root smoke verification contract."""

    def test_help_includes_smoke_request_chain_guidance(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke-request-chain", result.stdout)
        self.assertIn("./atp smoke-request-chain", result.stdout)
        self.assertIn(CANONICAL_FIXTURE, result.stdout)
        self.assertIn("Canonical bounded-chain fixture policy:", result.stdout)

    def test_smoke_request_chain_runs_all_three_steps(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("ATP v1.1 canonical smoke verification", result.stdout)
        self.assertIn(
            f"Canonical fixture policy: {CANONICAL_FIXTURE} is the bounded help/example/smoke fixture",
            result.stdout,
        )
        self.assertIn(
            "Canonical verification contract: smoke + request-flow + request-bundle + request-prompt must all succeed on this fixture with bounded scope unchanged.",
            result.stdout,
        )
        self.assertIn("[1/3] request-flow", result.stdout)
        self.assertIn("[2/3] request-bundle", result.stdout)
        self.assertIn("[3/3] request-prompt", result.stdout)
        self.assertIn('"command": "request-flow"', result.stdout)
        self.assertIn('"command": "request-bundle"', result.stdout)
        self.assertIn('"command": "request-prompt"', result.stdout)
        self.assertIn('"request_file": "tests/fixtures/requests/sample_request_slice02.yaml"', result.stdout)
        self.assertIn("ATP smoke verification result", result.stdout)
        self.assertIn("canonical_fixture_confirmed: true", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)
        self.assertIn(
            "bounded_surfaces_exercised: request-flow,request-bundle,request-prompt",
            result.stdout,
        )
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("verification_scope: repo_local_bounded_single_ai_chain", result.stdout)
        self.assertIn(
            "verification_confidence: canonical_fixture_and_request_chain_confirmed",
            result.stdout,
        )
        self.assertIn(
            "control_boundary: repo_local_human_gated_manual_single_ai_only",
            result.stdout,
        )
        self.assertIn("release_gates_opened: false", result.stdout)
        self.assertIn(
            "operator_surface_confirmed: ./atp repo-root launcher remains canonical for bounded followthrough",
            result.stdout,
        )
        self.assertIn(
            f"verification_recheck_command: ./atp smoke-request-chain {CANONICAL_FIXTURE}",
            result.stdout,
        )
        self.assertIn(
            f"next_operator_path: review -> ./atp request-bundle {CANONICAL_FIXTURE} ; handoff -> ./atp request-prompt {CANONICAL_FIXTURE}",
            result.stdout,
        )

    def test_smoke_request_chain_reports_missing_fixture_clearly(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain", "does/not/exist.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ATP smoke-request-chain error: request file not found", result.stderr)
        self.assertIn(CANONICAL_FIXTURE, result.stderr)


if __name__ == "__main__":
    unittest.main()
