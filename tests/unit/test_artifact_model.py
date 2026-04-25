"""Unit tests for ATP M4-M7 artifact, routing, validation, and state seed models."""

from __future__ import annotations

import unittest
from pathlib import Path

from adapters.filesystem.artifact_store import (
    create_filtered_artifact,
    create_raw_artifact,
    mark_authoritative,
    mark_deprecated,
    mark_selected,
)
from adapters.filesystem.workspace_writer import (
    RUN_TREE_ZONES,
    repo_local_serialization_path,
    resolve_run_root,
    workspace_path,
)
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.handoff.evidence_bundle import build_evidence_bundle
from core.handoff.inline_context import build_inline_context
from core.handoff.manifest_reference import build_manifest_reference
from core.routing.routing_result import build_routing_result
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state, build_transition_record


class TestArtifactModel(unittest.TestCase):
    """Cover shallow artifact and transition contracts."""

    def test_execution_output_transforms_into_raw_artifact_structure(self) -> None:
        raw_artifact = create_raw_artifact(
            {
                "execution_id": "execution-req-1",
                "request_id": "req-1",
                "product": "ATP",
                "command": ["echo", "hello"],
                "exit_code": 0,
                "stdout": "hello\n",
                "stderr": "",
                "status": "succeeded",
            }
        )

        self.assertEqual(raw_artifact["artifact_state"], "raw")
        self.assertEqual(raw_artifact["artifact_type"], "execution_output")

    def test_filtered_selected_and_authoritative_flags_apply_as_expected(self) -> None:
        raw_artifact = create_raw_artifact(
            {
                "execution_id": "execution-req-1",
                "request_id": "req-1",
                "product": "ATP",
                "command": ["echo", "hello"],
                "exit_code": 0,
                "stdout": "hello\n",
                "stderr": "",
                "status": "succeeded",
            }
        )
        filtered = create_filtered_artifact(raw_artifact)
        selected = mark_selected(filtered)
        authoritative = mark_authoritative(selected)
        deprecated = mark_deprecated(authoritative)

        self.assertEqual(filtered["artifact_state"], "filtered")
        self.assertEqual(selected["artifact_state"], "selected")
        self.assertEqual(authoritative["artifact_state"], "authoritative")
        self.assertTrue(authoritative["authoritative"])
        self.assertEqual(deprecated["artifact_state"], "deprecated")

    def test_inline_context_and_manifest_reference_keep_locked_names(self) -> None:
        inline_context = build_inline_context("seed summary", authoritative=True)
        manifest_reference = build_manifest_reference("artifact-1", "task-manifest-req-1")

        self.assertEqual(inline_context["handoff_type"], "inline_context")
        self.assertTrue(inline_context["authoritative"])
        self.assertEqual(manifest_reference["handoff_type"], "manifest_reference")
        self.assertTrue(manifest_reference["authoritative"])

    def test_evidence_selector_returns_expected_core_artifact_set(self) -> None:
        selection = select_evidence(
            [
                {"artifact_id": "raw-1", "artifact_type": "request_raw"},
                {"artifact_id": "norm-1", "artifact_type": "request_normalized", "authoritative": True},
                {"artifact_id": "manifest-1", "artifact_type": "task_manifest", "authoritative": True},
                {"artifact_id": "future-1", "artifact_type": "execution_output"},
            ]
        )

        self.assertEqual(
            [artifact["artifact_type"] for artifact in selection["selected_artifacts"]],
            ["request_raw", "request_normalized", "task_manifest"],
        )
        self.assertEqual(len(selection["authoritative_refs"]), 2)

    def test_evidence_bundle_materializer_returns_stable_structure(self) -> None:
        selection = {
            "selected_artifacts": [{"artifact_id": "manifest-1", "artifact_type": "task_manifest"}],
            "authoritative_refs": [{"artifact_id": "manifest-1", "manifest_reference": "task-manifest-req-1"}],
        }
        bundle = materialize_bundle("req-1", "ATP", selection, "task-manifest-req-1")
        handoff_bundle = build_evidence_bundle(selection["selected_artifacts"])

        self.assertEqual(bundle["bundle_id"], "evidence-bundle-req-1")
        self.assertEqual(bundle["manifest_reference"], "task-manifest-req-1")
        self.assertEqual(handoff_bundle["handoff_type"], "evidence_bundle")

    def test_routing_result_builder_returns_stable_structure(self) -> None:
        routing_result = build_routing_result(
            request_id="req-1",
            product="ATP",
            required_capabilities=["shell_execution"],
            candidate_providers=["non_llm_execution"],
            candidate_nodes=["local_mac"],
            selected_provider="non_llm_execution",
            selected_node="local_mac",
            reason_codes=["capability_supported"],
            cost_summary={"policy_mode": "local_first"},
            execution_path="local_subprocess",
        )

        self.assertEqual(routing_result["route_id"], "route-req-1")
        self.assertEqual(routing_result["execution_path"], "local_subprocess")
        self.assertEqual(routing_result["status"], "selected")

    def test_artifact_schema_keys_remain_stable(self) -> None:
        artifact = create_raw_artifact(
            {
                "execution_id": "execution-req-1",
                "request_id": "req-1",
                "product": "ATP",
                "command": ["echo", "hello"],
                "exit_code": 0,
                "stdout": "hello\n",
                "stderr": "",
                "status": "succeeded",
            }
        )

        self.assertEqual(
            set(artifact.keys()),
            {
                "artifact_id",
                "request_id",
                "product",
                "artifact_type",
                "artifact_state",
                "source_stage",
                "source_ref",
                "authoritative",
                "artifact_freshness",
                "payload_summary",
                "notes",
            },
        )

    def test_state_transition_helper_returns_expected_structure(self) -> None:
        run_record = build_run_record(run_id="run-1", request_id="req-1")
        updated = advance_run_state(run_record, RunState.REVIEWED, "review decision created")
        transition = build_transition_record("run-1", RunState.VALIDATED, RunState.REVIEWED, RunState.REVIEWED)

        self.assertEqual(updated["state"], RunState.REVIEWED)
        self.assertEqual(updated["latest_transition"]["detail"], "review decision created")
        self.assertEqual(
            set(transition.keys()),
            {"run_id", "from_state", "to_state", "stage", "detail", "recorded_at"},
        )

    def test_workspace_path_helpers_preserve_repo_vs_runtime_boundary(self) -> None:
        self.assertEqual(workspace_path("run-1", "logs"), "SOURCE_DEV/workspace/ATP/runs/run-1/logs")
        self.assertIn("handoff", RUN_TREE_ZONES)
        self.assertEqual(
            resolve_run_root("run-1", workspace_root=Path("/tmp") / "SOURCE_DEV" / "workspace"),
            (Path("/tmp") / "SOURCE_DEV" / "workspace" / "ATP" / "runs" / "run-1").resolve(),
        )
        self.assertEqual(
            repo_local_serialization_path("run-1", "exchange"),
            Path("tests") / "fixtures" / "outputs" / "exchange" / "run-1",
        )


if __name__ == "__main__":
    unittest.main()
