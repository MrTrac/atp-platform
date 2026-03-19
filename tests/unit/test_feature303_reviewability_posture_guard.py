"""Evidence and regression tests for ATP v1.4 Feature F-303 reviewability posture guard."""

from __future__ import annotations

import json
import subprocess
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature303ReviewabilityPostureGuardP1GapCapture(unittest.TestCase):
    """Capture the bounded need for a dedicated line-level posture guard after F-301/F-302."""

    def test_help_exposes_the_v14_reviewability_surface_set(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("review-summary", result.stdout)
        self.assertIn("integration-contract", result.stdout)
        self.assertIn("deployability-check", result.stdout)

    def test_review_and_supporting_surfaces_now_cross_reference_each_other(self) -> None:
        review_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "review-summary"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        integration_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        deployability_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(review_result.returncode, 0)
        self.assertEqual(integration_result.returncode, 0)
        self.assertEqual(deployability_result.returncode, 0)
        review_payload = json.loads(review_result.stdout, object_pairs_hook=OrderedDict)
        integration_payload = json.loads(integration_result.stdout, object_pairs_hook=OrderedDict)
        deployability_payload = json.loads(deployability_result.stdout, object_pairs_hook=OrderedDict)
        focused = review_payload["operator_review_summary"]["operator_review_path"][
            "focused_supporting_surfaces"
        ]
        self.assertIn("./atp integration-contract", focused)
        self.assertIn("./atp deployability-check", focused)
        self.assertIn("review-summary", integration_payload["operator_scan_summary"]["next_safe_bounded_action"])
        self.assertIn("review-summary", deployability_payload["operator_scan_summary"]["next_safe_bounded_action"])

    def test_smoke_request_chain_still_passes_before_guard_layer_is_added(self) -> None:
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
