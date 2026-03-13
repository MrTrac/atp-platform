"""Unit tests for ATP M4 artifact, evidence, and state seed models."""

from __future__ import annotations

import unittest

from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.handoff.evidence_bundle import build_evidence_bundle
from core.handoff.inline_context import build_inline_context
from core.handoff.manifest_reference import build_manifest_reference
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state, build_transition_record


class TestArtifactModel(unittest.TestCase):
    """Cover shallow artifact and transition contracts."""

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

    def test_state_transition_helper_returns_expected_structure(self) -> None:
        run_record = build_run_record(run_id="run-1", request_id="req-1")
        updated = advance_run_state(run_record, RunState.CONTEXT_PACKAGED, "context packaged")
        transition = build_transition_record(
            "run-1",
            RunState.RESOLVED,
            RunState.CONTEXT_PACKAGED,
            RunState.CONTEXT_PACKAGED,
        )

        self.assertEqual(updated["state"], RunState.CONTEXT_PACKAGED)
        self.assertEqual(updated["latest_transition"]["detail"], "context packaged")
        self.assertEqual(
            set(transition.keys()),
            {"run_id", "from_state", "to_state", "stage", "detail", "recorded_at"},
        )


if __name__ == "__main__":
    unittest.main()
