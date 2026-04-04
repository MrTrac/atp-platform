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


class TestFeature301OperatorReviewSummaryP2Surface(unittest.TestCase):
    """Lock the bounded dedicated operator review summary surface."""

    def test_help_exposes_review_summary_command(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("review-summary", result.stdout)
        self.assertIn("./atp review-summary", result.stdout)

    def test_review_summary_returns_bounded_review_json(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "review-summary"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["command"], "review-summary")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("operator_scan_summary", payload)
        summary = payload["operator_review_summary"]
        self.assertEqual(summary["review_mode"], "derived_static_review_summary")
        self.assertEqual(
            summary["entrypoint_surface"]["review_command"],
            "./atp review-summary",
        )
        self.assertEqual(
            summary["bounded_capabilities"]["can_project"],
            ["integration_contract_projection"],
        )
        self.assertEqual(
            summary["bounded_capabilities"]["can_assess"],
            ["deployability_readiness"],
        )
        self.assertIn("persistent_registry_or_history", summary["unsupported_capabilities"])
        self.assertIn("start_scheduler_or_daemon", summary["blocked_actions"])

    def test_review_summary_export_writes_artifact_and_manifest(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [str(ROOT_DIR / "atp"), "review-summary", "--export-dir", tmp],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "review-summary-0001"
            artifact_path = Path(tmp) / run_id / "operator_review_summary.json"
            manifest_path = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact_path.exists())
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(), object_pairs_hook=OrderedDict)
            self.assertEqual(manifest["command"], "review-summary")
            self.assertEqual(manifest["artifact_type"], "operator_review_summary")
            self.assertNotIn("request_file", manifest)

    def test_review_summary_wording_stays_review_oriented(self) -> None:
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
        notes_text = " ".join(summary["notes"]).lower()
        self.assertIn("descriptive only", notes_text)
        self.assertIn("does not report live state", notes_text)
        self.assertNotIn("dashboard", notes_text)
        self.assertNotIn("control center", notes_text)


class TestFeature301OperatorReviewSummaryP3PostureLocks(unittest.TestCase):
    """Regression locks for truthful, bounded operator review posture."""

    def test_help_does_not_imply_dashboard_or_control_plane(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        lowered = result.stdout.lower()
        self.assertNotIn("dashboard", lowered)
        self.assertNotIn("control center", lowered)
        self.assertNotIn("live status", lowered)
        self.assertNotIn("status board", lowered)

    def test_review_summary_is_not_spread_to_compose_chain_or_request_prompt(self) -> None:
        compose_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", CANONICAL_REQUEST],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        prompt_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", CANONICAL_REQUEST],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(compose_result.returncode, 0)
        self.assertEqual(prompt_result.returncode, 0)
        compose_payload = json.loads(compose_result.stdout, object_pairs_hook=OrderedDict)
        prompt_payload = json.loads(prompt_result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("operator_review_summary", compose_payload)
        self.assertNotIn("operator_review_summary", prompt_payload)
        self.assertNotIn("operator_review_summary", prompt_payload["review_summary"])

    def test_review_summary_module_has_no_network_or_subprocess_imports(self) -> None:
        module_path = ROOT_DIR / "core" / "operator_review_summary.py"
        source = module_path.read_text()
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import subprocess", source)

    def test_smoke_request_chain_still_passes_without_review_summary_drift(self) -> None:
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
