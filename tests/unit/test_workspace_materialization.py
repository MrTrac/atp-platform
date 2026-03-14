"""Unit tests for ATP v0.2 Slice 1 runtime materialization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from adapters.filesystem.workspace_writer import (
    SLICE1_RUN_ZONES,
    materialize_run_outputs,
    materialize_run_tree,
    resolve_workspace_root,
)


def _build_fake_repo_root(base_dir: Path) -> Path:
    repo_root = base_dir / "SOURCE_DEV" / "platforms" / "ATP"
    repo_root.mkdir(parents=True, exist_ok=True)
    return repo_root


def _sample_payloads(run_id: str) -> dict[str, object]:
    return {
        "raw_request": {"request_id": "req-1", "product": "ATP"},
        "normalized_request": {"request_id": "req-1", "product": "ATP"},
        "classification": {"request_type": "execute", "execution_intent": "run_command"},
        "resolution": {"product": "ATP", "repo_boundary": "SOURCE_DEV/platforms/ATP"},
        "task_manifest": {"manifest_id": "task-manifest-req-1", "request_id": "req-1"},
        "product_context": {"product": "ATP", "profile_ref": "profiles/ATP/profile.yaml"},
        "manifest_reference": {"handoff_type": "manifest_reference", "manifest_reference": "task-manifest-req-1"},
        "run_record": {"run_id": run_id, "request_id": "req-1", "current_stage": "CLOSED"},
        "prepared_route": {"route_id": "route-req-1", "candidate_providers": ["non_llm_execution"]},
        "routing_result": {"route_id": "route-req-1", "status": "selected"},
        "execution_result": {
            "execution_id": "execution-req-1",
            "command": ["echo", "hello"],
            "exit_code": 0,
            "status": "succeeded",
            "stdout": "hello\n",
            "stderr": "",
        },
        "artifacts": {"items": [], "summary": {"artifact_ids": []}},
        "validation_summary": {"validation_status": "passed"},
        "review_decision": {"review_status": "accept"},
        "approval_result": {"approval_status": "approved"},
        "close_or_continue": {"run_id": run_id, "decision": "close"},
        "decision_state": {"decision_status": "finalized"},
        "finalization_summary": {"final_status": "completed"},
    }


class TestWorkspaceMaterialization(unittest.TestCase):
    """Cover runtime root resolution and Slice 1 run tree creation."""

    def test_workspace_root_resolves_from_repo_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            self.assertEqual(resolve_workspace_root(repo_root), (repo_root.parents[1] / "workspace").resolve())

    def test_workspace_root_rejects_non_atp_repo_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_repo_root = Path(temp_dir) / "tmp" / "ATP"
            invalid_repo_root.mkdir(parents=True, exist_ok=True)

            with self.assertRaises(ValueError):
                resolve_workspace_root(invalid_repo_root)

    def test_materialize_run_tree_creates_only_slice1_zones(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            tree = materialize_run_tree("run-slice1-1", repo_root=repo_root)

            self.assertEqual(set(tree["run_root"].iterdir()), {tree[zone] for zone in SLICE1_RUN_ZONES})
            self.assertFalse((tree["run_root"] / "planning").exists())
            self.assertFalse((tree["run_root"] / "handoff").exists())

    def test_materialize_run_outputs_writes_only_under_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            summary = materialize_run_outputs("run-slice1-2", _sample_payloads("run-slice1-2"), repo_root=repo_root)

            run_root = Path(summary["run_root"])
            self.assertTrue(run_root.is_dir())
            self.assertEqual(set(Path(path).name for path in run_root.iterdir()), set(SLICE1_RUN_ZONES))
            self.assertTrue((run_root / "request" / "request.raw.json").is_file())
            self.assertTrue((run_root / "manifests" / "manifest-reference.json").is_file())
            self.assertTrue((run_root / "logs" / "materialization.log").is_file())
            self.assertFalse((repo_root / "atp-runs").exists())
            self.assertFalse((repo_root / "request").exists())


if __name__ == "__main__":
    unittest.main()
