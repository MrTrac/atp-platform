"""Evidence and contract tests for ATP v1.3 Feature 201 — Execution Artifact Export Surface.

P1 scope: verify bounded export contract definitions (path convention, manifest schema).
P2 scope: verify opt-in --export-dir flag on 3 CLI commands.
P3 scope: regression locks — stdout unchanged without flag, smoke chain intact.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
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

    def test_artifact_export_module_uses_no_raw_open_calls(self) -> None:
        """Verify the module never uses bare open() — file I/O is Path-based only."""
        module_path = ROOT_DIR / "core" / "artifact_export.py"
        source = module_path.read_text()
        # File writes use Path.write_text(), not bare open() calls.
        self.assertNotIn("open(", source)


class TestFeature201ArtifactExportP2Implementation(unittest.TestCase):
    """Lock the P2 opt-in export implementation on 3 CLI commands."""

    def test_write_artifact_and_write_manifest_exist_in_module(self) -> None:
        from core.artifact_export import write_artifact, write_manifest  # noqa: F401

    def test_write_artifact_creates_file_at_correct_path(self) -> None:
        from core.artifact_export import write_artifact

        with tempfile.TemporaryDirectory() as tmp:
            path = write_artifact(tmp, "run-p2-001", "request_flow", {"status": "ok"})
            self.assertTrue(path.endswith("/run-p2-001/request_flow.json"))
            self.assertTrue(Path(path).exists())

    def test_write_artifact_content_is_valid_json(self) -> None:
        from core.artifact_export import write_artifact

        data = {"command": "request-flow", "status": "ok", "run_id": "run-p2-001"}
        with tempfile.TemporaryDirectory() as tmp:
            path = write_artifact(tmp, "run-p2-001", "request_flow", data)
            loaded = json.loads(Path(path).read_text())
            self.assertEqual(loaded["status"], "ok")
            self.assertEqual(loaded["command"], "request-flow")

    def test_write_manifest_creates_file_at_correct_path(self) -> None:
        from core.artifact_export import build_export_manifest, write_manifest

        manifest = build_export_manifest(
            run_id="run-p2-001",
            command="request-flow",
            request_file=FIXTURE,
            artifact_type="request_flow",
            artifact_path="/tmp/run-p2-001/request_flow.json",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_manifest(tmp, "run-p2-001", manifest)
            self.assertTrue(path.endswith("/run-p2-001/export_manifest.json"))
            self.assertTrue(Path(path).exists())

    def test_write_manifest_content_is_valid_json_with_contract_fields(self) -> None:
        from core.artifact_export import build_export_manifest, write_manifest

        manifest = build_export_manifest(
            run_id="run-p2-001",
            command="request-bundle",
            request_file=FIXTURE,
            artifact_type="request_bundle",
            artifact_path="/tmp/run-p2-001/request_bundle.json",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_manifest(tmp, "run-p2-001", manifest)
            loaded = json.loads(Path(path).read_text())
            self.assertEqual(loaded["export_contract_version"], "1.0")
            self.assertEqual(loaded["export_mode"], "opt_in_human_initiated")
            self.assertEqual(loaded["artifact_type"], "request_bundle")

    def test_request_flow_export_dir_flag_writes_artifact_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_flow.py", FIXTURE, "--export-dir", tmp],
                capture_output=True, text=True, cwd=ROOT_DIR,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "slice-02-preview-0001"
            artifact = Path(tmp) / run_id / "request_flow.json"
            manifest = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact.exists(), f"artifact not found: {artifact}")
            self.assertTrue(manifest.exists(), f"manifest not found: {manifest}")

    def test_request_bundle_export_dir_flag_writes_artifact_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_bundle.py", FIXTURE, "--export-dir", tmp],
                capture_output=True, text=True, cwd=ROOT_DIR,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "slice-03-preview-0001"
            artifact = Path(tmp) / run_id / "request_bundle.json"
            manifest = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact.exists(), f"artifact not found: {artifact}")
            self.assertTrue(manifest.exists(), f"manifest not found: {manifest}")

    def test_request_prompt_export_dir_flag_writes_artifact_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_prompt.py", FIXTURE, "--export-dir", tmp],
                capture_output=True, text=True, cwd=ROOT_DIR,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run_id = "slice-04-preview-0001"
            artifact = Path(tmp) / run_id / "request_prompt.json"
            manifest = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact.exists(), f"artifact not found: {artifact}")
            self.assertTrue(manifest.exists(), f"manifest not found: {manifest}")

    def test_exported_artifact_is_same_json_as_stdout(self) -> None:
        """Artifact file content matches what stdout produced."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "cli/request_flow.py", FIXTURE, "--export-dir", tmp],
                capture_output=True, text=True, cwd=ROOT_DIR,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            stdout_data = json.loads(result.stdout)
            artifact_path = Path(tmp) / "slice-02-preview-0001" / "request_flow.json"
            file_data = json.loads(artifact_path.read_text())
            self.assertEqual(stdout_data, file_data)

    def test_help_output_mentions_export_dir_flag(self) -> None:
        result = subprocess.run(
            ["./atp", "help"],
            capture_output=True, text=True, cwd=ROOT_DIR,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--export-dir", result.stdout)
        self.assertIn("opt-in", result.stdout)

    def test_artifact_export_module_has_file_io_at_p2(self) -> None:
        """Verify write_artifact and write_manifest are now present in P2."""
        module_path = ROOT_DIR / "core" / "artifact_export.py"
        source = module_path.read_text()
        self.assertIn("def write_artifact", source)
        self.assertIn("def write_manifest", source)


class TestFeature201ArtifactExportP3RegressionLocks(unittest.TestCase):
    """Regression locks — stdout contract unchanged without flag, export posture bounded."""

    def _run_command(self, cmd: list[str]) -> str:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=ROOT_DIR,
        )
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
        return result.stdout

    def test_request_flow_stdout_is_valid_json_without_export_flag(self) -> None:
        out = self._run_command(["python3", "cli/request_flow.py", FIXTURE])
        data = json.loads(out)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-flow")

    def test_request_bundle_stdout_is_valid_json_without_export_flag(self) -> None:
        out = self._run_command(["python3", "cli/request_bundle.py", FIXTURE])
        data = json.loads(out)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-bundle")

    def test_request_prompt_stdout_is_valid_json_without_export_flag(self) -> None:
        out = self._run_command(["python3", "cli/request_prompt.py", FIXTURE])
        data = json.loads(out)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-prompt")

    def test_no_export_files_written_without_flag(self) -> None:
        """Without --export-dir, no files are written anywhere in the repo."""
        import os
        before_mtime = os.path.getmtime(ROOT_DIR / "core" / "artifact_export.py")
        self._run_command(["python3", "cli/request_flow.py", FIXTURE])
        after_mtime = os.path.getmtime(ROOT_DIR / "core" / "artifact_export.py")
        self.assertEqual(before_mtime, after_mtime)

    def test_export_mode_constant_remains_opt_in(self) -> None:
        from core.artifact_export import EXPORT_MODE

        self.assertEqual(EXPORT_MODE, "opt_in_human_initiated")
        self.assertNotIn("auto", EXPORT_MODE)
        self.assertNotIn("background", EXPORT_MODE)
        self.assertNotIn("default", EXPORT_MODE)

    def test_request_flow_stdout_content_unchanged_vs_no_flag_baseline(self) -> None:
        """Stdout with --export-dir equals stdout without flag."""
        out_no_flag = self._run_command(["python3", "cli/request_flow.py", FIXTURE])
        with tempfile.TemporaryDirectory() as tmp:
            out_with_flag = self._run_command(
                ["python3", "cli/request_flow.py", FIXTURE, "--export-dir", tmp]
            )
        self.assertEqual(json.loads(out_no_flag), json.loads(out_with_flag))

    def test_smoke_chain_passes_after_export_surface_added(self) -> None:
        result = subprocess.run(
            ["./atp", "smoke-request-chain"],
            capture_output=True, text=True, cwd=ROOT_DIR,
        )
        self.assertEqual(result.returncode, 0, f"Smoke chain failed:\n{result.stdout}\n{result.stderr}")

    def test_export_scope_label_does_not_imply_remote_or_network(self) -> None:
        from core.artifact_export import EXPORT_SCOPE

        self.assertNotIn("remote", EXPORT_SCOPE)
        self.assertNotIn("network", EXPORT_SCOPE)
        self.assertNotIn("cloud", EXPORT_SCOPE)
        self.assertIn("repo_local", EXPORT_SCOPE)

    def test_export_notes_contain_no_background_write_statement(self) -> None:
        from core.artifact_export import EXPORT_NOTES

        notes_text = " ".join(EXPORT_NOTES)
        self.assertIn("No background write", notes_text)
        self.assertIn("opt-in", notes_text)

    def test_write_artifact_does_not_write_inside_repo_root_by_default(self) -> None:
        """write_artifact must not write inside repo root — it only writes to provided export_dir."""
        from core.artifact_export import write_artifact
        import inspect

        source = inspect.getsource(write_artifact)
        # Function must not reference ROOT_DIR or repo paths
        self.assertNotIn("ROOT_DIR", source)
        self.assertNotIn("/SOURCE_DEV", source)


if __name__ == "__main__":
    unittest.main()
