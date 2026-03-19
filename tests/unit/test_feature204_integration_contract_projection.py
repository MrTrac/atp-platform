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
    """Capture the missing bounded integration-contract projection surface before implementation."""

    def test_help_does_not_yet_expose_integration_contract_command(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertNotIn("integration-contract", result.stdout)

    def test_compose_chain_does_not_yet_expose_integration_contract_projection(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("integration_contract_projection", payload)

    def test_request_prompt_export_manifest_does_not_yet_project_integration_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_prompt.py", FIXTURE, "--export-dir", tmp],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = Path(tmp) / "slice-04-preview-0001" / "export_manifest.json"
            manifest = json.loads(manifest_path.read_text(), object_pairs_hook=OrderedDict)
            self.assertNotIn("integration_contract_projection", manifest)


if __name__ == "__main__":
    unittest.main()
