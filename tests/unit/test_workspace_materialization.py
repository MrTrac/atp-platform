"""Unit tests for ATP v0.4 Slice A-C plus earlier runtime materialization baseline."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import json

from adapters.filesystem.workspace_writer import (
    RUN_TREE_ZONES,
    materialize_run_outputs,
    materialize_run_tree,
    resolve_artifact_projection_root,
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
            "request_id": "req-1",
            "product": "ATP",
            "command": ["echo", "hello"],
            "exit_code": 0,
            "status": "succeeded",
            "stdout": "hello\n",
            "stderr": "",
        },
        "artifacts": {
            "items": [
                {
                    "artifact_id": "artifact-selected-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "selected",
                    "source_stage": "execution",
                    "source_ref": "artifact-filtered-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                },
                {
                    "artifact_id": "artifact-authoritative-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "authoritative",
                    "source_stage": "execution",
                    "source_ref": "artifact-selected-req-1",
                    "artifact_freshness": "current",
                    "authoritative": True,
                },
            ],
            "summary": {"artifact_ids": ["artifact-selected-req-1", "artifact-authoritative-req-1"]},
        },
        "validation_summary": {"validation_status": "passed"},
        "review_decision": {"review_status": "accept"},
        "approval_result": {"approval_status": "approved"},
        "close_or_continue": {"run_id": run_id, "decision": "close"},
        "decision_state": {"decision_status": "finalized"},
        "exchange_boundary_decision": {
            "decision_id": f"exchange-boundary-{run_id}",
            "run_id": run_id,
            "request_id": "req-1",
            "close_or_continue": "close",
            "boundary_mode": "run_local_handoff",
            "requires_exchange_boundary": False,
            "exchange_materialization_status": "deferred",
            "manifest_reference": "task-manifest-req-1",
            "evidence_bundle_id": "handoff-evidence-req-1",
            "reason_codes": ["closed_run_keeps_handoff_inside_current_run"],
        },
        "exchange_bundle": {
            "handoff_type": "exchange_bundle",
            "exchange_id": "exchange-req-1",
            "request_id": "req-1",
            "artifacts": ["artifact-authoritative-req-1"],
            "provider": "non_llm_execution",
            "adapter": "local_subprocess",
        },
        "handoff_outputs": {
            "inline_context": {"handoff_type": "inline_context", "summary": "done", "authoritative": True},
            "evidence_bundle": {"handoff_type": "evidence_bundle", "bundle_id": "handoff-evidence-req-1"},
            "manifest_reference": {
                "handoff_type": "manifest_reference",
                "manifest_reference": "task-manifest-req-1",
                "authoritative": True,
            },
        },
        "finalization_summary": {"final_status": "completed"},
    }


class TestWorkspaceMaterialization(unittest.TestCase):
    """Cover runtime root resolution plus v0.3-v0.4 traceability, persistence, recovery, and pointer semantics."""

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

    def test_materialize_run_tree_creates_only_approved_run_tree_zones(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            tree = materialize_run_tree("run-slice1-1", repo_root=repo_root)

            self.assertEqual(set(tree["run_root"].iterdir()), {tree[zone] for zone in RUN_TREE_ZONES})
            self.assertFalse((tree["run_root"] / "planning").exists())
            self.assertFalse((tree["run_root"] / "exchange").exists())

    def test_materialize_run_outputs_writes_only_under_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            summary = materialize_run_outputs("run-slice1-2", _sample_payloads("run-slice1-2"), repo_root=repo_root)

            run_root = Path(summary["run_root"])
            self.assertTrue(run_root.is_dir())
            self.assertEqual(set(Path(path).name for path in run_root.iterdir()), set(RUN_TREE_ZONES))
            self.assertTrue((run_root / "request" / "request.raw.json").is_file())
            self.assertTrue((run_root / "manifests" / "manifest-reference.json").is_file())
            self.assertTrue((run_root / "decisions" / "exchange-boundary-decision.json").is_file())
            self.assertTrue((run_root / "handoff" / "inline-context.json").is_file())
            self.assertTrue((run_root / "handoff" / "evidence-bundle.json").is_file())
            self.assertTrue((run_root / "handoff" / "manifest-reference.json").is_file())
            self.assertTrue((run_root / "logs" / "materialization.log").is_file())
            self.assertTrue((run_root / "logs" / "cleanup.log").is_file())
            self.assertTrue((run_root / "final" / "retention-summary.json").is_file())
            self.assertTrue((run_root / "final" / "continuation-state.json").is_file())
            self.assertTrue((run_root / "final" / "reference-index.json").is_file())
            self.assertFalse(summary["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(summary["exchange_boundary"]["exchange_materialization_status"], "not_required")
            self.assertFalse(summary["exchange"]["materialized"])
            self.assertFalse(summary["current_task_persistence"]["persisted"])
            self.assertFalse(summary["recovery_contract"]["recovery_ready"])
            self.assertFalse(summary["current_task_pointer"]["active_pointer_written"])
            self.assertFalse(summary["continuation"]["continuation_required"])
            self.assertFalse(summary["reference_index"]["exchange_current_task"]["materialized"])
            self.assertEqual(summary["reference_index"]["continuation"]["current_source"], "none")
            self.assertEqual(summary["authoritative_projection"]["projected_count"], 1)
            projection_root = Path(summary["authoritative_projection"]["items"][0]["projection_root"])
            self.assertTrue((projection_root / "artifact.json").is_file())
            self.assertTrue((projection_root / "projection-metadata.json").is_file())
            self.assertEqual(summary["retention"]["cleanup_mode"], "manual_review_only")
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            self.assertFalse((run_root / "exchange").exists())
            self.assertFalse((Path(summary["workspace_root"]) / "exchange").exists())
            self.assertFalse((repo_root / "atp-runs").exists())
            self.assertFalse((repo_root / "request").exists())
            self.assertFalse((repo_root / "atp-artifacts").exists())

    def test_authoritative_projection_keeps_traceability_to_run_and_source_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            summary = materialize_run_outputs("run-slice3-1", _sample_payloads("run-slice3-1"), repo_root=repo_root)

            projection_root = resolve_artifact_projection_root(
                "artifact-authoritative-req-1",
                repo_root=repo_root,
            )
            metadata = json.loads((projection_root / "projection-metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(summary["authoritative_projection"]["projected_count"], 1)
            self.assertEqual(metadata["run_id"], "run-slice3-1")
            self.assertEqual(metadata["source_stage"], "execution")
            self.assertEqual(metadata["projection_scope"], "authoritative")
            self.assertFalse((projection_root.parent / "artifact-selected-req-1").exists())

    def test_reference_index_and_current_exchange_pointer_remain_coherent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-sliceD-1")
            payloads["close_or_continue"]["decision"] = "continue_pending"
            payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]

            summary = materialize_run_outputs("run-sliceD-1", payloads, repo_root=repo_root)

            run_root = Path(summary["run_root"])
            exchange_root = Path(summary["exchange"]["exchange_root"])
            reference_index = json.loads((run_root / "final" / "reference-index.json").read_text(encoding="utf-8"))
            current_pointer = json.loads((exchange_root / "current.json").read_text(encoding="utf-8"))
            current_task_state = json.loads(
                (exchange_root / "current-task-state.json").read_text(encoding="utf-8")
            )
            recovery_contract = json.loads(
                (exchange_root / "continue-pending-recovery.json").read_text(encoding="utf-8")
            )
            active_pointer = json.loads(
                (exchange_root.parent / "active-pointer.json").read_text(encoding="utf-8")
            )

            self.assertEqual(reference_index["run_id"], "run-sliceD-1")
            self.assertTrue(reference_index["exchange_current_task"]["materialized"])
            self.assertEqual(
                reference_index["exchange_current_task"]["current_reference_path"],
                str(exchange_root / "current.json"),
            )
            self.assertEqual(current_pointer["reference_index_path"], str(run_root / "final" / "reference-index.json"))
            self.assertEqual(current_pointer["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(
                reference_index["exchange_current_task"]["persistence_state_path"],
                str(exchange_root / "current-task-state.json"),
            )
            self.assertTrue(summary["current_task_persistence"]["persisted"])
            self.assertEqual(summary["current_task_persistence"]["current_task_id"], "current-task-run-sliceD-1")
            self.assertEqual(current_task_state["current_reference_path"], str(exchange_root / "current.json"))
            self.assertEqual(current_task_state["reference_index_path"], str(run_root / "final" / "reference-index.json"))
            self.assertEqual(current_task_state["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(current_task_state["persistence_scope"], "workspace_exchange_current_task")
            self.assertTrue(summary["recovery_contract"]["recovery_ready"])
            self.assertEqual(
                summary["recovery_contract"]["recovery_contract_path"],
                str(exchange_root / "continue-pending-recovery.json"),
            )
            self.assertEqual(
                reference_index["continuation"]["recovery_contract_path"],
                str(exchange_root / "continue-pending-recovery.json"),
            )
            self.assertEqual(recovery_contract["current_task_persistence_state_path"], str(exchange_root / "current-task-state.json"))
            self.assertEqual(recovery_contract["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(recovery_contract["current_reference_path"], str(exchange_root / "current.json"))
            self.assertEqual(recovery_contract["recovery_scope"], "continue_pending_current_task")
            self.assertTrue(summary["current_task_pointer"]["active_pointer_written"])
            self.assertFalse(summary["current_task_pointer"]["superseded_previous"])
            self.assertEqual(
                reference_index["exchange_current_task"]["active_pointer_path"],
                str(exchange_root.parent / "active-pointer.json"),
            )
            self.assertEqual(reference_index["exchange_current_task"]["supersede_trace_path"], "")
            self.assertEqual(active_pointer["run_id"], "run-sliceD-1")
            self.assertEqual(active_pointer["current_task_persistence_state_path"], str(exchange_root / "current-task-state.json"))
            self.assertEqual(active_pointer["recovery_contract_path"], str(exchange_root / "continue-pending-recovery.json"))
            self.assertFalse(active_pointer["superseded_previous"])

    def test_active_pointer_supersede_trace_links_to_previous_current_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))

            first_payloads = _sample_payloads("run-sliceC-1")
            first_payloads["close_or_continue"]["decision"] = "continue_pending"
            first_payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            first_payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            first_payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            first_payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]
            first_summary = materialize_run_outputs("run-sliceC-1", first_payloads, repo_root=repo_root)

            second_payloads = _sample_payloads("run-sliceC-2")
            second_payloads["close_or_continue"]["decision"] = "continue_pending"
            second_payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            second_payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            second_payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            second_payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]
            second_summary = materialize_run_outputs("run-sliceC-2", second_payloads, repo_root=repo_root)

            second_exchange_root = Path(second_summary["exchange"]["exchange_root"])
            active_pointer = json.loads((second_exchange_root.parent / "active-pointer.json").read_text(encoding="utf-8"))
            supersede_trace = json.loads((second_exchange_root / "supersede-trace.json").read_text(encoding="utf-8"))

            self.assertTrue(second_summary["current_task_pointer"]["active_pointer_written"])
            self.assertTrue(second_summary["current_task_pointer"]["superseded_previous"])
            self.assertEqual(active_pointer["run_id"], "run-sliceC-2")
            self.assertTrue(active_pointer["superseded_previous"])
            self.assertEqual(active_pointer["supersede_trace_path"], str(second_exchange_root / "supersede-trace.json"))
            self.assertEqual(supersede_trace["previous_run_id"], "run-sliceC-1")
            self.assertEqual(
                supersede_trace["previous_current_task_state_path"],
                first_summary["current_task_persistence"]["persistence_state_path"],
            )
            self.assertEqual(
                supersede_trace["previous_recovery_contract_path"],
                first_summary["recovery_contract"]["recovery_contract_path"],
            )
            self.assertEqual(
                second_summary["reference_index"]["exchange_current_task"]["supersede_trace_path"],
                str(second_exchange_root / "supersede-trace.json"),
            )

    def test_retention_summary_marks_deprecated_artifacts_cleanup_eligible_after_close(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-slice4-1")
            payloads["artifacts"]["items"].append(
                {
                    "artifact_id": "artifact-deprecated-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "deprecated",
                    "source_stage": "execution",
                    "source_ref": "artifact-authoritative-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                }
            )
            payloads["close_or_continue"]["decision"] = "close_rejected"

            summary = materialize_run_outputs("run-slice4-1", payloads, repo_root=repo_root)

            self.assertEqual(summary["retention"]["close_or_continue"], "close_rejected")
            self.assertEqual(len(summary["retention"]["cleanup_eligible_artifacts"]), 1)
            self.assertEqual(
                summary["retention"]["cleanup_eligible_artifacts"][0]["artifact_id"],
                "artifact-deprecated-req-1",
            )
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            projection_root = Path(summary["authoritative_projection"]["items"][0]["projection_root"])
            self.assertTrue(projection_root.is_dir())

    def test_continue_pending_retains_deprecated_artifacts_without_cleanup_eligibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-slice4-2")
            payloads["artifacts"]["items"].append(
                {
                    "artifact_id": "artifact-deprecated-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "deprecated",
                    "source_stage": "execution",
                    "source_ref": "artifact-authoritative-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                }
            )
            payloads["close_or_continue"]["decision"] = "continue_pending"
            payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]

            summary = materialize_run_outputs("run-slice4-2", payloads, repo_root=repo_root)

            self.assertEqual(summary["retention"]["retention_mode"], "retain_for_continuation")
            self.assertEqual(summary["retention"]["cleanup_eligible_artifacts"], [])
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            self.assertTrue(summary["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(summary["exchange_boundary"]["exchange_materialization_status"], "materialized_current_task")
            self.assertTrue(summary["exchange"]["materialized"])
            self.assertTrue(summary["continuation"]["continuation_required"])
            self.assertEqual(summary["continuation"]["current_source"], "exchange_current_task")
            self.assertEqual(summary["continuation"]["exchange_boundary_mode"], "external_exchange_candidate")
            self.assertTrue(summary["reference_index"]["exchange_current_task"]["materialized"])
            self.assertEqual(
                summary["reference_index"]["continuation"]["current_source"],
                "exchange_current_task",
            )
            exchange_root = Path(summary["exchange"]["exchange_root"])
            self.assertTrue((exchange_root / "exchange-bundle.json").is_file())
            self.assertTrue((exchange_root / "exchange-metadata.json").is_file())
            self.assertTrue((exchange_root / "current.json").is_file())
            self.assertTrue((exchange_root / "current-task-state.json").is_file())
            self.assertTrue((exchange_root / "continue-pending-recovery.json").is_file())
            self.assertTrue((exchange_root.parent / "active-pointer.json").is_file())
            self.assertFalse((repo_root / "exchange").exists())


if __name__ == "__main__":
    unittest.main()
