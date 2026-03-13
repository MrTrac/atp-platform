"""Unit tests for ATP M1-M2 artifact and state seed models."""

from __future__ import annotations

import unittest

from core.handoff.evidence_bundle import build_evidence_bundle
from core.handoff.inline_context import build_inline_context
from core.handoff.manifest_reference import build_manifest_reference
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state, build_transition_record


class TestArtifactModel(unittest.TestCase):
    """Cover shallow artifact and transition contracts."""

    def test_inline_context_and_manifest_reference_keep_locked_names(self) -> None:
        inline_context = build_inline_context("seed summary", authoritative=True)
        manifest_reference = build_manifest_reference("artifact-1", "manifests/request.yaml")

        self.assertEqual(inline_context["handoff_type"], "inline_context")
        self.assertTrue(inline_context["authoritative"])
        self.assertEqual(manifest_reference["handoff_type"], "manifest_reference")
        self.assertTrue(manifest_reference["authoritative"])

    def test_evidence_bundle_is_authoritative_by_default(self) -> None:
        bundle = build_evidence_bundle([{"artifact_id": "artifact-1"}])

        self.assertEqual(bundle["handoff_type"], "evidence_bundle")
        self.assertTrue(bundle["authoritative"])

    def test_state_transition_helper_returns_expected_structure(self) -> None:
        run_record = build_run_record(run_id="run-1", request_id="req-1")
        updated = advance_run_state(run_record, RunState.NORMALIZED, "normalized request")
        transition = build_transition_record("run-1", RunState.NORMALIZED, RunState.CLASSIFIED, RunState.CLASSIFIED)

        self.assertEqual(updated["state"], RunState.NORMALIZED)
        self.assertEqual(updated["latest_transition"]["detail"], "normalized request")
        self.assertEqual(
            set(transition.keys()),
            {"run_id", "from_state", "to_state", "stage", "detail", "recorded_at"},
        )


if __name__ == "__main__":
    unittest.main()
