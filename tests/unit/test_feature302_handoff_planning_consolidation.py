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


class TestFeature302HandoffPlanningConsolidationP3PostureLocks(unittest.TestCase):
    """Regression locks for truthful, non-centralizing consolidation posture."""

    def test_touched_surfaces_do_not_imply_workflow_or_planning_controller(self) -> None:
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

        self.assertEqual(integration_result.returncode, 0)
        self.assertEqual(deployability_result.returncode, 0)
        lowered = (integration_result.stdout + deployability_result.stdout).lower()
        self.assertNotIn("workflow engine", lowered)
        self.assertIn("does not create a planning controller", lowered)
        self.assertNotIn("acts as a planning controller", lowered)
        self.assertNotIn("handoff manager", lowered)
        self.assertNotIn("state machine", lowered)
        self.assertNotIn("control center", lowered)

    def test_consolidation_guidance_is_not_spread_to_compose_chain_or_request_prompt(self) -> None:
        compose_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        prompt_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(compose_result.returncode, 0)
        self.assertEqual(prompt_result.returncode, 0)
        compose_payload = json.loads(compose_result.stdout, object_pairs_hook=OrderedDict)
        prompt_payload = json.loads(prompt_result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("review_handoff_alignment", compose_payload)
        self.assertNotIn("review_handoff_alignment", prompt_payload)
        self.assertNotIn("review_handoff_alignment", prompt_payload["review_summary"])

    def test_consolidation_does_not_create_central_registry_semantics(self) -> None:
        review_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "review-summary"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(review_result.returncode, 0)
        lowered = review_result.stdout.lower()
        self.assertIn("does not report live state", lowered)
        self.assertIn("or create a registry/catalog", lowered)
        self.assertNotIn("single source of truth", lowered)
        self.assertNotIn("global coordination", lowered)
        self.assertNotIn("surface catalog", lowered)

    def test_smoke_request_chain_still_passes_without_consolidation_drift(self) -> None:
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
