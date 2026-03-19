"""Evidence and regression tests for ATP v1.4 Feature F-301 operator review summary."""

from __future__ import annotations

import json
import subprocess
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature301OperatorReviewSummaryP1GapCapture(unittest.TestCase):
    """Capture the absence of a bounded dedicated operator review summary center."""

    def test_help_does_not_yet_expose_review_summary_command(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertNotIn("review-summary", result.stdout)
        self.assertNotIn("operator-review", result.stdout)

    def test_integration_contract_has_no_operator_review_summary_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("operator_review_summary", payload)
        self.assertNotIn("operator_review_summary", payload["integration_contract_projection"])

    def test_deployability_check_has_no_operator_review_summary_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("operator_review_summary", payload)
        self.assertNotIn("operator_review_summary", payload["deployability_readiness"])

    def test_compose_chain_has_no_dedicated_operator_review_summary_center(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", CANONICAL_REQUEST],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("operator_review_summary", payload)
        self.assertNotIn("operator_review_summary", str(payload))

    def test_smoke_request_chain_still_passes_before_review_summary_exists(self) -> None:
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
