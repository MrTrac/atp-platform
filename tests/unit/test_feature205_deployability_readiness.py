"""Evidence and regression tests for ATP v1.3 Feature F-205 deployability readiness.

P1 scope is evidence only: capture the absence of a bounded deployability-readiness
surface before any runtime behavior is introduced.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature205DeployabilityReadinessP1GapCapture(unittest.TestCase):
    """Capture the current deployability-readiness projection gap."""

    def test_request_bundle_has_no_deployability_readiness_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-bundle", CANONICAL_REQUEST],
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


class TestFeature205DeployabilityReadinessP2Surface(unittest.TestCase):
    """Lock the bounded deployability-readiness surface."""

    def test_help_exposes_deployability_check_command(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("deployability-check", result.stdout)
        self.assertIn("./atp deployability-check", result.stdout)
        self.assertIn("assessment_only_not_operationally_deployable", result.stdout)

    def test_deployability_check_returns_bounded_readiness_json(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["command"], "deployability-check")
        self.assertEqual(payload["status"], "ok")
        readiness = payload["deployability_readiness"]
        self.assertEqual(readiness["assessment_mode"], "derived_read_only_assessment")
        self.assertEqual(
            readiness["overall_readiness_signal"],
            "assessment_only_not_operationally_deployable",
        )
        self.assertEqual(
            readiness["entry_point_check"]["cli_entrypoint"],
            "./atp",
        )
        self.assertEqual(
            readiness["workspace_path_requirements"]["runtime_workspace_root"],
            "/Users/nguyenthanhthu/SOURCE_DEV/workspace",
        )
        self.assertIn("no_real_deployment_execution", readiness["blockers_by_design"])
        self.assertIn(
            "no_repo_dependency_manifest_detected",
            readiness["configuration_surface_gaps"],
        )

    def test_deployability_check_export_writes_artifact_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [str(ROOT_DIR / "atp"), "deployability-check", "--export-dir", tmp],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "deployability-check-0001"
            artifact_path = Path(tmp) / run_id / "deployability_readiness.json"
            manifest_path = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact_path.exists())
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(), object_pairs_hook=OrderedDict)
            self.assertEqual(manifest["command"], "deployability-check")
            self.assertEqual(manifest["artifact_type"], "deployability_readiness")
            self.assertNotIn("request_file", manifest)

    def test_deployability_check_wording_stays_descriptive_only(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "deployability-check"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        readiness = payload["deployability_readiness"]
        notes_text = " ".join(readiness["notes"]).lower()
        self.assertIn("descriptive only", notes_text)
        self.assertIn("does not deploy", notes_text)
        self.assertNotIn("activated", notes_text)
        self.assertNotIn("scheduler", notes_text)
        self.assertNotIn("daemon", notes_text)


class TestFeature205DeployabilityReadinessP3PostureLocks(unittest.TestCase):
    """Regression locks for truthful, bounded deployability posture."""

    def test_help_does_not_imply_deploy_engine_or_background_control(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        lowered = result.stdout.lower()
        self.assertNotIn("deploy engine", lowered)
        self.assertNotIn("installer engine", lowered)
        self.assertNotIn("background worker", lowered)
        self.assertNotIn("scheduler", lowered)

    def test_deployability_surface_is_not_spread_to_compose_chain_or_request_prompt(self) -> None:
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
        self.assertNotIn("deployability_readiness", compose_payload)
        self.assertNotIn("deployability_readiness", prompt_payload)
        self.assertNotIn("deployability_readiness", prompt_payload["review_summary"])

    def test_deployability_module_has_no_network_or_subprocess_imports(self) -> None:
        module_path = ROOT_DIR / "core" / "deployability_readiness.py"
        source = module_path.read_text()
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import subprocess", source)

    def test_smoke_request_chain_still_passes_without_deployability_drift(self) -> None:
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
