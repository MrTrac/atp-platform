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
        review_path = payload["operator_review_summary"]["operator_review_path"]
        focused = review_path["focused_supporting_surfaces"]
        self.assertIn("./atp integration-contract", focused)
        self.assertIn("./atp deployability-check", focused)
        self.assertNotIn("supporting_surface_roles", review_path)

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


class TestFeature302HandoffPlanningConsolidationP2Surface(unittest.TestCase):
    """Lock the narrow coherence refinement across relevant review/handoff surfaces."""

    def test_integration_contract_includes_review_handoff_alignment(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        alignment = payload["integration_contract_projection"]["review_handoff_alignment"]
        self.assertEqual(alignment["review_entrypoint"], "./atp review-summary")
        self.assertEqual(alignment["surface_role"], "integration_boundary_review_support")
        self.assertIn("handoff boundaries", alignment["operator_interpretation"])
        self.assertIn("review-summary", payload["operator_scan_summary"]["next_safe_bounded_action"])

    def test_deployability_check_includes_review_handoff_alignment(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        alignment = payload["deployability_readiness"]["review_handoff_alignment"]
        self.assertEqual(alignment["review_entrypoint"], "./atp review-summary")
        self.assertEqual(alignment["surface_role"], "deployability_boundary_review_support")
        self.assertIn("deployability limits and gaps", alignment["operator_interpretation"])
        self.assertIn("review-summary", payload["operator_scan_summary"]["next_safe_bounded_action"])

    def test_review_summary_remains_distinct_from_supporting_surfaces(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "review-summary"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        summary = payload["operator_review_summary"]
        self.assertNotIn("review_handoff_alignment", summary)
        self.assertNotIn("integration_contract_projection", summary)
        self.assertNotIn("deployability_readiness", summary)


if __name__ == "__main__":
    unittest.main()
