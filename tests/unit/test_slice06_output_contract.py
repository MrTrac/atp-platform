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
                "quick_status",
                "primary_artifact",
                "primary_review_target",
                "handoff_target",
                "next_bounded_action",
                "review_sections",
            ],
        )
        self.assertEqual(payload["review_summary"]["result_status"], "accepted")
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
