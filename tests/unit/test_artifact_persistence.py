"""Unit tests for ATP artifact persistence (tmpdir-isolated)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from adapters.filesystem.artifact_store import store_artifact
from adapters.filesystem.exchange_adapter import write_exchange_bundle
from bridge.run_persistence import get_run, list_runs, persist_bridge_run


class TestStoreArtifact(unittest.TestCase):

    def test_disabled_returns_stored_false(self) -> None:
        result = store_artifact({"artifact_id": "art-1", "artifact_type": "execution_output"})
        self.assertFalse(result["stored"])

    def test_enabled_writes_json_to_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            artifact = {
                "artifact_id": "art-test-1",
                "artifact_type": "execution_output",
                "payload_summary": {"status": "completed"},
            }
            result = store_artifact(artifact, workspace_root=ws)
            self.assertTrue(result["stored"])
            self.assertIn("path", result)

            written = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
            self.assertEqual(written["artifact_id"], "art-test-1")

    def test_creates_artifact_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            store_artifact({"artifact_id": "art-dir-test"}, workspace_root=ws)
            self.assertTrue((ws / "atp-artifacts" / "art-dir-test").is_dir())


class TestWriteExchangeBundle(unittest.TestCase):

    def test_disabled_returns_in_memory(self) -> None:
        result = write_exchange_bundle({"bundle_id": "b-1", "request_id": "r-1"})
        self.assertEqual(result["status"], "in_memory_only")

    def test_enabled_writes_bundle_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            bundle = {"bundle_id": "b-test-1", "request_id": "run-1", "data": "payload"}
            result = write_exchange_bundle(bundle, workspace_root=ws)
            self.assertEqual(result["status"], "persisted")
            self.assertIn("path", result)

            written = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
            self.assertEqual(written["bundle_id"], "b-test-1")


class TestRunPersistence(unittest.TestCase):

    def _persist_sample_run(self, ws: Path, run_id: str = "bridge-test-001") -> dict:
        return persist_bridge_run(
            request_id=run_id,
            normalized_request={"request_id": run_id, "payload": {"input_text": "test"}},
            routing_result={"selected_provider": "ollama", "selected_node": "local_mac", "selected_provider_model": "qwen3:14b"},
            raw_result={"status": "completed", "stdout": "hello", "exit_code": 0},
            normalized_output={"request_id": run_id, "status": "completed", "exit_code": 0},
            workspace_root=ws,
        )

    def test_disabled_returns_not_persisted(self) -> None:
        result = persist_bridge_run("r-1", {}, {}, {}, {})
        self.assertFalse(result["persisted"])

    def test_creates_run_directory_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            result = self._persist_sample_run(ws)
            self.assertTrue(result["persisted"])

            run_dir = ws / "atp-runs" / "bridge-test-001"
            self.assertTrue(run_dir.is_dir())
            self.assertTrue((run_dir / "request").is_dir())
            self.assertTrue((run_dir / "routing").is_dir())
            self.assertTrue((run_dir / "executor-outputs").is_dir())

    def test_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            result = self._persist_sample_run(ws)
            self.assertIn("request/request.normalized.json", result["files_written"])
            self.assertIn("routing/routing-result.json", result["files_written"])
            self.assertIn("executor-outputs/execution-result.json", result["files_written"])
            self.assertIn("run-summary.json", result["files_written"])

    def test_run_summary_has_correct_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            self._persist_sample_run(ws)
            summary_path = ws / "atp-runs" / "bridge-test-001" / "run-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["run_id"], "bridge-test-001")
            self.assertEqual(summary["provider"], "ollama")
            self.assertIn("timestamp", summary)


class TestListAndGetRuns(unittest.TestCase):

    def test_list_runs_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runs = list_runs(workspace_root=Path(tmpdir))
            self.assertEqual(runs, [])

    def test_list_runs_finds_persisted_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            persist_bridge_run("run-a", {}, {}, {}, {"status": "ok"}, workspace_root=ws)
            persist_bridge_run("run-b", {}, {}, {}, {"status": "ok"}, workspace_root=ws)
            runs = list_runs(workspace_root=ws)
            run_ids = [r["run_id"] for r in runs]
            self.assertIn("run-a", run_ids)
            self.assertIn("run-b", run_ids)

    def test_get_run_returns_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            persist_bridge_run("run-x", {}, {}, {}, {"status": "ok"}, workspace_root=ws)
            run_data = get_run("run-x", workspace_root=ws)
            self.assertIsNotNone(run_data)
            self.assertEqual(run_data["run_id"], "run-x")
            self.assertIn("zones", run_data)

    def test_get_run_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_data = get_run("nonexistent", workspace_root=Path(tmpdir))
            self.assertIsNone(run_data)


if __name__ == "__main__":
    unittest.main()
