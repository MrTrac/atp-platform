"""Evidence and regression tests for ATP v1.4 Feature F-302 handoff/planning consolidation."""

from __future__ import annotations

import json
import subprocess
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


class TestFeature302HandoffPlanningConsolidationP1GapCapture(unittest.TestCase):
    """Capture the bounded coherence gap between review-summary and supporting surfaces."""

    def test_review_summary_points_to_supporting_surfaces_but_not_their_roles(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "review-summary"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        focused = payload["operator_review_summary"]["operator_review_path"][
            "focused_supporting_surfaces"
        ]
        self.assertIn("./atp integration-contract", focused)
        self.assertIn("./atp deployability-check", focused)

    def test_integration_contract_has_no_review_handoff_alignment_guidance(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("review_handoff_alignment", payload["integration_contract_projection"])
        self.assertNotIn("review-summary", payload["operator_scan_summary"]["next_safe_bounded_action"])

    def test_deployability_check_has_no_review_handoff_alignment_guidance(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("review_handoff_alignment", payload["deployability_readiness"])
        self.assertNotIn("review-summary", payload["operator_scan_summary"]["next_safe_bounded_action"])

    def test_smoke_request_chain_still_passes_before_consolidation_exists(self) -> None:
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
