"""Unit tests for ATP v1.1 Slice 06 output-contract hardening."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE_FILE = "tests/fixtures/requests/sample_request_slice02.yaml"


def _run_cli(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT_DIR / "cli" / command), str(ROOT_DIR / FIXTURE_FILE)],
        check=False,
        capture_output=True,
        text=True,
    )


def _load_ordered_json(stdout: str) -> OrderedDict[str, object]:
    return json.loads(stdout, object_pairs_hook=OrderedDict)


class TestSlice06OutputContract(unittest.TestCase):
    """Lock deterministic operator-facing output shape for the request chain."""

    def test_request_flow_output_has_hardened_top_level_shape(self) -> None:
        result = _run_cli("request_flow.py")

        self.assertEqual(result.returncode, 0)
        payload = _load_ordered_json(result.stdout)
        self.assertEqual(
            list(payload.keys()),
            ["command", "status", "request_file", "run_id", "review_summary", "summary"],
        )
        self.assertEqual(payload["command"], "request-flow")
        self.assertEqual(
            list(payload["review_summary"].keys()),
            [
                "command",
                "request_file",
                "run_id",
                "product",
                "request_id",
                "flow_id",
                "supported_flow",
                "result_status",
                "completion_signal",
                "quick_status",
                "readiness_checklist",
                "confidence_summary",
                "chain_trace_summary",
                "review_evidence_summary",
                "primary_artifact",
                "primary_review_target",
                "handoff_target",
                "next_bounded_action",
                "review_first",
                "handoff_surface",
                "review_sections",
            ],
        )
        self.assertEqual(payload["review_summary"]["result_status"], "accepted")
        self.assertEqual(
            payload["review_summary"]["completion_signal"],
            {
                "state": "complete_for_current_step",
                "review_complete_candidate": False,
                "handoff_complete_candidate": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["quick_status"],
            {
                "command": "request-flow",
                "result_status": "accepted",
                "primary_artifact_type": "single_ai_execution_package",
                "ready_for_review": True,
                "ready_for_handoff": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["readiness_checklist"],
            {
                "ready_for_review": True,
                "ready_for_next_bounded_step": True,
                "ready_for_handoff": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["confidence_summary"],
            {
                "confidence_state": "low_ambiguity_for_bounded_progression",
                "confidence_basis": [
                    "completion_signal_complete_for_current_step",
                    "readiness_checklist_ready_for_next_bounded_step",
                    "primary_artifact_identified",
                ],
                "next_safe_bounded_action": "./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml",
            },
        )
        self.assertEqual(
            payload["review_summary"]["chain_trace_summary"],
            {
                "current_stage": "single_ai_execution_package",
                "current_artifact_id": "single-ai-package-req-atp-v1-1-slice02-0001",
                "current_artifact_type": "single_ai_execution_package",
                "request_traceability_seed": "trace-slice02-0001",
                "upstream_evidence": {
                    "request_id": "req-atp-v1-1-slice02-0001",
                    "flow_id": "slice-02-request-flow-req-atp-v1-1-slice02-0001",
                    "task_id": "single-ai-task-req-atp-v1-1-slice02-0001",
                    "task_manifest_id": "task-manifest-req-atp-v1-1-slice02-0001",
                    "preparation_contract_id": "product-execution-preparation-req-atp-v1-1-slice02-0001",
                },
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_evidence_summary"],
            {
                "evidence_status": "bounded_preparation_evidence_present",
                "evidence_needed": [
                    "validation_summary",
                    "single_ai_execution_package.traceability",
                    "task_manifest.input_artifacts",
                ],
                "evidence_present": [
                    "validation_summary",
                    "single_ai_execution_package",
                    "single_ai_execution_package.traceability",
                    "task_manifest",
                ],
            },
        )
        self.assertEqual(
            payload["review_summary"]["primary_review_target"],
            {
                "section": "single_ai_execution_package",
                "focus": "bounded_execution_package_surface",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_target"],
            {
                "target_type": "next_bounded_cli_step",
                "command": "request-bundle",
                "artifact_section": "single_ai_execution_package",
            },
        )
        self.assertEqual(
            payload["review_summary"]["next_bounded_action"],
            {
                "action_type": "run_cli_command",
                "command": "./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml",
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_first"],
            {
                "section": "validation_summary",
                "then_check": "single_ai_execution_package",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_surface"],
            {
                "section": "single_ai_execution_package",
                "mode": "prepare_reviewable_bundle",
                "next_command": "request-bundle",
            },
        )
        summary = payload["summary"]
        self.assertEqual(
            list(summary.keys())[:8],
            [
                "product",
                "request_id",
                "flow_id",
                "flow_status",
                "supported_flow",
                "notes",
                "validation_summary",
                "normalized_task",
            ],
        )

    def test_request_bundle_output_has_review_friendly_section_order(self) -> None:
        result = _run_cli("request_bundle.py")

        self.assertEqual(result.returncode, 0)
        payload = _load_ordered_json(result.stdout)
        self.assertEqual(
            list(payload.keys()),
            ["command", "status", "request_file", "run_id", "review_summary", "summary"],
        )
        self.assertEqual(payload["command"], "request-bundle")
        self.assertEqual(payload["review_summary"]["result_status"], "reviewable")
        self.assertEqual(
            payload["review_summary"]["completion_signal"],
            {
                "state": "review_complete_candidate",
                "review_complete_candidate": True,
                "handoff_complete_candidate": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["quick_status"],
            {
                "command": "request-bundle",
                "result_status": "reviewable",
                "primary_artifact_type": "reviewable_single_ai_output_bundle",
                "ready_for_review": True,
                "ready_for_handoff": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["readiness_checklist"],
            {
                "ready_for_review": True,
                "ready_for_next_bounded_step": True,
                "ready_for_handoff": False,
            },
        )
        self.assertEqual(
            payload["review_summary"]["confidence_summary"],
            {
                "confidence_state": "low_ambiguity_for_review_then_progression",
                "confidence_basis": [
                    "completion_signal_review_complete_candidate",
                    "readiness_checklist_ready_for_next_bounded_step",
                    "review_surface_present",
                ],
                "next_safe_bounded_action": "./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml",
            },
        )
        self.assertEqual(
            payload["review_summary"]["chain_trace_summary"],
            {
                "current_stage": "reviewable_single_ai_bundle",
                "current_artifact_id": "reviewable-output-bundle-req-atp-v1-1-slice02-0001",
                "current_artifact_type": "reviewable_single_ai_output_bundle",
                "request_traceability_seed": "trace-slice02-0001",
                "upstream_evidence": {
                    "request_id": "req-atp-v1-1-slice02-0001",
                    "flow_id": "slice-02-request-flow-req-atp-v1-1-slice02-0001",
                    "normalized_task_id": "single-ai-task-req-atp-v1-1-slice02-0001",
                    "package_id": "single-ai-package-req-atp-v1-1-slice02-0001",
                    "task_manifest_id": "task-manifest-req-atp-v1-1-slice02-0001",
                    "preparation_contract_id": "product-execution-preparation-req-atp-v1-1-slice02-0001",
                },
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_evidence_summary"],
            {
                "evidence_status": "bounded_review_evidence_present",
                "evidence_needed": [
                    "reviewable_output_bundle.review_surface",
                    "reviewable_output_bundle.traceability",
                    "reviewable_output_bundle.single_ai_package_payload.traceability",
                ],
                "evidence_present": [
                    "reviewable_output_bundle",
                    "reviewable_output_bundle.review_surface",
                    "reviewable_output_bundle.traceability",
                ],
            },
        )
        self.assertEqual(
            payload["review_summary"]["primary_review_target"],
            {
                "section": "reviewable_output_bundle",
                "focus": "human_reviewable_bundle_surface",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_target"],
            {
                "target_type": "next_bounded_cli_step",
                "command": "request-prompt",
                "artifact_section": "reviewable_output_bundle",
            },
        )
        self.assertEqual(
            payload["review_summary"]["next_bounded_action"],
            {
                "action_type": "run_cli_command",
                "command": "./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml",
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_first"],
            {
                "section": "reviewable_output_bundle",
                "then_check": "reviewable_output_bundle.review_surface",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_surface"],
            {
                "section": "reviewable_output_bundle",
                "mode": "prepare_request_prompt",
                "next_command": "request-prompt",
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_sections"],
            ["reviewable_output_bundle"],
        )
        summary = payload["summary"]
        self.assertEqual(
            list(summary.keys()),
            [
                "product",
                "request_id",
                "flow_id",
                "bundle_status",
                "supported_flow",
                "notes",
                "reviewable_output_bundle",
            ],
        )
        bundle = summary["reviewable_output_bundle"]
        self.assertEqual(
            list(bundle.keys()),
            [
                "bundle_id",
                "bundle_type",
                "bundle_version",
                "request_identity",
                "normalized_task_summary",
                "scope_and_constraints",
                "single_ai_package_payload",
                "review_surface",
                "traceability",
            ],
        )

    def test_request_prompt_output_has_review_friendly_section_order(self) -> None:
        result = _run_cli("request_prompt.py")

        self.assertEqual(result.returncode, 0)
        payload = _load_ordered_json(result.stdout)
        self.assertEqual(
            list(payload.keys()),
            ["command", "status", "request_file", "run_id", "review_summary", "summary"],
        )
        self.assertEqual(payload["command"], "request-prompt")
        self.assertEqual(payload["review_summary"]["result_status"], "ai_ready")
        self.assertEqual(
            payload["review_summary"]["completion_signal"],
            {
                "state": "handoff_complete_candidate",
                "review_complete_candidate": True,
                "handoff_complete_candidate": True,
            },
        )
        self.assertEqual(
            payload["review_summary"]["quick_status"],
            {
                "command": "request-prompt",
                "result_status": "ai_ready",
                "primary_artifact_type": "one_shot_ai_ready_execution_prompt",
                "ready_for_review": True,
                "ready_for_handoff": True,
            },
        )
        self.assertEqual(
            payload["review_summary"]["readiness_checklist"],
            {
                "ready_for_review": True,
                "ready_for_next_bounded_step": False,
                "ready_for_handoff": True,
            },
        )
        self.assertEqual(
            payload["review_summary"]["confidence_summary"],
            {
                "confidence_state": "low_ambiguity_for_manual_handoff",
                "confidence_basis": [
                    "completion_signal_handoff_complete_candidate",
                    "readiness_checklist_ready_for_handoff",
                    "handoff_surface_prompt_text_present",
                ],
                "next_safe_bounded_action": "handoff one_shot_ai_ready_artifact.prompt_text to one AI manually",
            },
        )
        self.assertEqual(
            payload["review_summary"]["chain_trace_summary"],
            {
                "current_stage": "one_shot_ai_ready_prompt",
                "current_artifact_id": "one-shot-ai-prompt-req-atp-v1-1-slice02-0001",
                "current_artifact_type": "one_shot_ai_ready_execution_prompt",
                "request_traceability_seed": "trace-slice02-0001",
                "upstream_evidence": {
                    "request_id": "req-atp-v1-1-slice02-0001",
                    "flow_id": "slice-02-request-flow-req-atp-v1-1-slice02-0001",
                    "normalized_task_id": "single-ai-task-req-atp-v1-1-slice02-0001",
                    "package_id": "single-ai-package-req-atp-v1-1-slice02-0001",
                    "bundle_id": "reviewable-output-bundle-req-atp-v1-1-slice02-0001",
                    "task_manifest_id": "task-manifest-req-atp-v1-1-slice02-0001",
                    "preparation_contract_id": "product-execution-preparation-req-atp-v1-1-slice02-0001",
                },
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_evidence_summary"],
            {
                "evidence_status": "bounded_handoff_evidence_present",
                "evidence_needed": [
                    "one_shot_ai_ready_artifact.prompt_text",
                    "one_shot_ai_ready_artifact.prompt_sections.traceability",
                    "reviewable_output_bundle.traceability",
                ],
                "evidence_present": [
                    "one_shot_ai_ready_artifact",
                    "one_shot_ai_ready_artifact.prompt_text",
                    "reviewable_output_bundle",
                    "reviewable_output_bundle.traceability",
                ],
            },
        )
        self.assertEqual(
            payload["review_summary"]["primary_review_target"],
            {
                "section": "one_shot_ai_ready_artifact",
                "focus": "manual_single_ai_handoff_surface",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_target"],
            {
                "target_type": "manual_single_ai_handoff",
                "artifact_section": "one_shot_ai_ready_artifact",
                "usage_mode": "manual_single_ai_handoff",
            },
        )
        self.assertEqual(
            payload["review_summary"]["next_bounded_action"],
            {
                "action_type": "handoff_to_one_ai",
                "target_section": "one_shot_ai_ready_artifact",
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_first"],
            {
                "section": "one_shot_ai_ready_artifact",
                "then_check": "one_shot_ai_ready_artifact.prompt_text",
            },
        )
        self.assertEqual(
            payload["review_summary"]["handoff_surface"],
            {
                "section": "one_shot_ai_ready_artifact",
                "artifact_field": "prompt_text",
                "mode": "manual_single_ai_handoff",
            },
        )
        self.assertEqual(
            payload["review_summary"]["review_sections"],
            ["reviewable_output_bundle", "one_shot_ai_ready_artifact"],
        )
        summary = payload["summary"]
        self.assertEqual(
            list(summary.keys()),
            [
                "product",
                "request_id",
                "flow_id",
                "artifact_status",
                "supported_flow",
                "notes",
                "reviewable_output_bundle",
                "one_shot_ai_ready_artifact",
            ],
        )
        artifact = summary["one_shot_ai_ready_artifact"]
        self.assertEqual(
            list(artifact.keys()),
            [
                "artifact_id",
                "artifact_type",
                "artifact_version",
                "product",
                "request_id",
                "flow_id",
                "supported_flow",
                "usage_mode",
                "handoff_notes",
                "prompt_sections",
                "prompt_text",
            ],
        )

    def test_repeated_runs_keep_identical_output_shape(self) -> None:
        first = _run_cli("request_prompt.py")
        second = _run_cli("request_prompt.py")

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()
