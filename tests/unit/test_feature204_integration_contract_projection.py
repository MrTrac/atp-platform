"""Evidence and contract tests for ATP v1.3 Feature 204 integration-contract projection."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature204IntegrationContractProjection(unittest.TestCase):
    """Lock the bounded integration-contract projection surface."""

    def test_help_exposes_integration_contract_command(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("integration-contract", result.stdout)
        self.assertIn("./atp integration-contract", result.stdout)

    def test_integration_contract_command_returns_bounded_projection_json(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["command"], "integration-contract")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("operator_scan_summary", payload)
        projection = payload["integration_contract_projection"]
        self.assertEqual(projection["projection_mode"], "derived_static_projection")
        self.assertEqual(projection["integration_mode"], "not_activated")
        self.assertEqual(projection["invocation_surface"]["cli_entrypoint"], "./atp")
        self.assertEqual(projection["composition_projection"]["command"], "./atp compose-chain")
        self.assertEqual(
            projection["artifact_projection"]["terminal_handoff_artifact_type"],
            "one_shot_ai_ready_execution_prompt",
        )
        self.assertEqual(
            projection["continuity_projection"]["continuity_surfaces"],
            ["execution-session", "export_manifest", "compose-chain"],
        )
        self.assertIn("provider_abstraction_layer", projection["unsupported_features"])
        self.assertIn("open_network_endpoint", projection["blocked_actions"])

    def test_integration_contract_export_writes_projected_artifact_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [str(ROOT_DIR / "atp"), "integration-contract", "--export-dir", tmp],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "integration-contract-0001"
            artifact_path = Path(tmp) / run_id / "integration_contract.json"
            manifest_path = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact_path.exists())
            manifest = json.loads(manifest_path.read_text(), object_pairs_hook=OrderedDict)
            self.assertEqual(manifest["command"], "integration-contract")
            self.assertEqual(manifest["artifact_type"], "integration_contract")
            self.assertTrue(manifest["artifact_path"].endswith("/integration_contract.json"))
            self.assertNotIn("request_file", manifest)

    def test_projection_wording_stays_derived_and_not_activated(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "integration-contract"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        projection = payload["integration_contract_projection"]
        self.assertEqual(projection["integration_mode"], "not_activated")
        notes_text = " ".join(projection["notes"]).lower()
        self.assertIn("derived/static projection", notes_text)
        self.assertIn("does not create a live api", notes_text)
        self.assertNotIn("scheduler", notes_text)
        self.assertNotIn("daemon", notes_text)
        self.assertNotIn("background worker", notes_text)

    def test_projection_is_not_spread_to_compose_chain_or_request_prompt(self) -> None:
        compose_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        prompt_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(compose_result.returncode, 0)
        self.assertEqual(prompt_result.returncode, 0)
        compose_payload = json.loads(compose_result.stdout, object_pairs_hook=OrderedDict)
        prompt_payload = json.loads(prompt_result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("integration_contract_projection", compose_payload)
        self.assertNotIn("integration_contract_projection", prompt_payload)
        self.assertNotIn("integration_contract_projection", prompt_payload["review_summary"])

    def test_smoke_request_chain_still_passes_without_projection_drift(self) -> None:
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

    def test_integration_contract_module_has_no_network_or_subprocess_imports(self) -> None:
        module_path = ROOT_DIR / "core" / "integration_contract.py"
        source = module_path.read_text()
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import subprocess", source)


if __name__ == "__main__":
    unittest.main()
