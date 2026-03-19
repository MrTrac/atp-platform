"""Evidence and regression tests for ATP v1.3 Feature F-205 deployability readiness.

P1 scope is evidence only: capture the absence of a bounded deployability-readiness
surface before any runtime behavior is introduced.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature205DeployabilityReadinessP1GapCapture(unittest.TestCase):
    """Capture the current deployability-readiness projection gap."""

    def test_help_does_not_yet_advertise_deployability_check(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertNotIn("deployability-check", result.stdout)
        self.assertNotIn("Deployability readiness", result.stdout)

    def test_integration_contract_has_no_deployability_projection(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("deployability_readiness", payload)
        self.assertNotIn("deployability_readiness_projection", payload)
        self.assertNotIn("deployability_readiness", str(payload))

    def test_compose_chain_has_no_deployability_readiness_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", CANONICAL_REQUEST],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("deployability_readiness", payload)
        self.assertNotIn("deployability_readiness_projection", payload)
        self.assertNotIn("deployability_readiness", str(payload))

    def test_request_prompt_has_no_deployability_readiness_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", CANONICAL_REQUEST],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("deployability_readiness", payload)
        self.assertNotIn("deployability_readiness_projection", payload)
        self.assertNotIn("deployability_readiness", str(payload))

    def test_smoke_request_chain_still_passes_before_readiness_surface_exists(self) -> None:
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
