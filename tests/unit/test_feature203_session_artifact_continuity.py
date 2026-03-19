"""Evidence and contract tests for ATP v1.3 Feature 203 session-artifact continuity."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature203SessionArtifactContinuity(unittest.TestCase):
    """Capture current continuity gaps before adding anchors."""

    def test_execution_session_currently_lacks_artifact_continuity_anchors(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertIn("session_summary", payload)
        self.assertNotIn("artifact_continuity_anchors", payload["session_summary"])

    def test_export_manifest_currently_lacks_session_linkage_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_flow.py", FIXTURE, "--export-dir", tmp],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = Path(tmp) / "slice-02-preview-0001" / "export_manifest.json"
            manifest = json.loads(manifest_path.read_text(), object_pairs_hook=OrderedDict)
            self.assertNotIn("session_id", manifest)
            self.assertNotIn("artifact_continuity_anchors", manifest)

    def test_compose_chain_currently_lacks_compact_session_artifact_continuity_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertIn("stages_executed", payload)
        self.assertNotIn("artifact_continuity_anchors", payload)


if __name__ == "__main__":
    unittest.main()
