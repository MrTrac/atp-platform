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
    """Lock the bounded session-artifact continuity surface."""

    def test_execution_session_exposes_empty_artifact_continuity_anchors_when_no_artifacts_exist(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(
            payload["artifact_continuity_anchors"],
            OrderedDict(
                [
                    ("continuity_mode", "derived_session_to_artifact"),
                    ("continuity_scope", "bounded_repo_local_within_invocation"),
                    ("session_id", "session-single-req-atp-v1-1-slice02-0001"),
                    (
                        "request_group_anchor",
                        OrderedDict(
                            [
                                ("primary_request_id", "req-atp-v1-1-slice02-0001"),
                                ("request_count", 1),
                            ]
                        ),
                    ),
                    ("anchors", []),
                    (
                        "operator_interpretation",
                        "These anchors link this session to locally produced artifacts in this bounded invocation only.",
                    ),
                ]
            ),
        )

    def test_export_manifest_includes_session_linkage_fields(self) -> None:
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
            self.assertEqual(manifest["session_id"], "session-single-req-atp-v1-1-slice02-0001")
            anchors = manifest["artifact_continuity_anchors"]["anchors"]
            self.assertEqual(len(anchors), 1)
            self.assertEqual(anchors[0]["artifact_id"], "single-ai-package-req-atp-v1-1-slice02-0001")
            self.assertEqual(anchors[0]["artifact_type"], "single_ai_execution_package")
            self.assertTrue(
                anchors[0]["export_path"].endswith("/slice-02-preview-0001/request_flow.json")
            )

    def test_compose_chain_exposes_compact_session_artifact_continuity_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "compose-chain", FIXTURE],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        anchors = payload["artifact_continuity_anchors"]
        self.assertEqual(anchors["session_id"], "session-single-req-atp-v1-1-slice02-0001")
        self.assertEqual(len(anchors["anchors"]), 3)
        self.assertEqual(
            [anchor["artifact_type"] for anchor in anchors["anchors"]],
            [
                "single_ai_execution_package",
                "reviewable_single_ai_output_bundle",
                "one_shot_ai_ready_execution_prompt",
            ],
        )


if __name__ == "__main__":
    unittest.main()
