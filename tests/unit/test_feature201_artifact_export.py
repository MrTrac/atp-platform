"""Evidence and contract tests for ATP v1.3 Feature 201 — Execution Artifact Export Surface.

P1 scope: verify bounded export contract definitions (path convention, manifest schema).
P2 scope: verify opt-in --export-dir flag on 3 CLI commands.
P3 scope: regression locks — stdout unchanged without flag, smoke chain intact.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature201ArtifactExportP1Contract(unittest.TestCase):
    """Lock the bounded artifact export contract definitions."""

    def test_export_contract_version_is_defined(self) -> None:
        from core.artifact_export import EXPORT_CONTRACT_VERSION

        self.assertEqual(EXPORT_CONTRACT_VERSION, "1.0")

    def test_export_scope_is_bounded(self) -> None:
        from core.artifact_export import EXPORT_SCOPE

        self.assertEqual(EXPORT_SCOPE, "bounded_repo_local_artifact")

    def test_export_mode_is_opt_in(self) -> None:
        from core.artifact_export import EXPORT_MODE

        self.assertEqual(EXPORT_MODE, "opt_in_human_initiated")
        self.assertNotIn("automatic", EXPORT_MODE)
        self.assertNotIn("background", EXPORT_MODE)

    def test_supported_artifact_types_covers_three_cli_commands(self) -> None:
        from core.artifact_export import SUPPORTED_ARTIFACT_TYPES

        self.assertIn("request_flow", SUPPORTED_ARTIFACT_TYPES)
        self.assertIn("request_bundle", SUPPORTED_ARTIFACT_TYPES)
        self.assertIn("request_prompt", SUPPORTED_ARTIFACT_TYPES)
        self.assertEqual(len(SUPPORTED_ARTIFACT_TYPES), 3)

    def test_manifest_filename_is_deterministic(self) -> None:
        from core.artifact_export import MANIFEST_FILENAME

        self.assertEqual(MANIFEST_FILENAME, "export_manifest.json")

    def test_build_export_path_follows_convention(self) -> None:
        from core.artifact_export import build_export_path

        path = build_export_path("/tmp/atp-export", "my-run-001", "request_flow")
        self.assertEqual(path, "/tmp/atp-export/my-run-001/request_flow.json")

    def test_build_export_path_all_three_types(self) -> None:
        from core.artifact_export import build_export_path

        for artifact_type in ("request_flow", "request_bundle", "request_prompt"):
            path = build_export_path("/export", "run-id", artifact_type)
            self.assertTrue(path.endswith(f"/{artifact_type}.json"))

    def test_build_export_path_rejects_invalid_artifact_type(self) -> None:
        from core.artifact_export import build_export_path

        with self.assertRaises(ValueError):
            build_export_path("/tmp", "run-id", "invalid_type")

    def test_build_export_path_rejects_empty_export_dir(self) -> None:
        from core.artifact_export import build_export_path

        with self.assertRaises(ValueError):
            build_export_path("", "run-id", "request_flow")

    def test_build_manifest_path_follows_convention(self) -> None:
        from core.artifact_export import build_manifest_path

        path = build_manifest_path("/tmp/atp-export", "my-run-001")
        self.assertEqual(path, "/tmp/atp-export/my-run-001/export_manifest.json")

    def test_build_export_manifest_returns_bounded_dict(self) -> None:
        from core.artifact_export import build_export_manifest

        manifest = dict(
            build_export_manifest(
                run_id="run-001",
                command="request-flow",
                request_file=FIXTURE,
                artifact_type="request_flow",
                artifact_path="/tmp/atp-export/run-001/request_flow.json",
            )
        )
        self.assertEqual(manifest["export_contract_version"], "1.0")
        self.assertEqual(manifest["export_scope"], "bounded_repo_local_artifact")
        self.assertEqual(manifest["export_mode"], "opt_in_human_initiated")
        self.assertEqual(manifest["run_id"], "run-001")
        self.assertEqual(manifest["command"], "request-flow")
        self.assertEqual(manifest["artifact_type"], "request_flow")
        self.assertIn("notes", manifest)
        self.assertIsInstance(manifest["notes"], list)

    def test_build_export_manifest_notes_confirm_opt_in_posture(self) -> None:
        from core.artifact_export import build_export_manifest

        manifest = dict(
            build_export_manifest(
                run_id="run-001",
                command="request-flow",
                request_file=FIXTURE,
                artifact_type="request_flow",
                artifact_path="/tmp/atp-export/run-001/request_flow.json",
            )
        )
        notes_text = " ".join(manifest["notes"])
        self.assertIn("opt-in", notes_text)
        self.assertIn("Stdout remains the canonical primary output", notes_text)
        self.assertNotIn("background", notes_text.replace("No background", "").lower())

    def test_artifact_export_module_has_no_file_io_at_p1(self) -> None:
        """Verify the module contains no file write operations at P1 (contract-only stage)."""
        module_path = ROOT_DIR / "core" / "artifact_export.py"
        source = module_path.read_text()
        # write_artifact and write_manifest are P2 additions — not present in P1
        self.assertNotIn("def write_artifact", source)
        self.assertNotIn("def write_manifest", source)
        # No open() calls in P1
        self.assertNotIn("open(", source)


if __name__ == "__main__":
    unittest.main()
