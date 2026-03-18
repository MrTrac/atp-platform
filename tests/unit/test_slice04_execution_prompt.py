"""Unit tests for ATP v1.1 Slice 04 one-shot AI-ready execution prompts."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.intake.execution_prompt import (
    ExecutionPromptError,
    build_one_shot_ai_ready_execution_prompt,
    prepare_one_shot_ai_ready_execution_prompt,
)
from core.intake.loader import load_request
from core.intake.review_bundle import prepare_reviewable_single_ai_output_bundle


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"
ROOT_DIR = Path(__file__).resolve().parents[2]


class TestSlice04ExecutionPrompt(unittest.TestCase):
    """Cover the bounded Slice 04 AI-ready artifact continuation."""

    def test_valid_request_produces_ai_ready_artifact(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")

        prepared = prepare_one_shot_ai_ready_execution_prompt(
            raw_request, run_id="slice-04-test-0001"
        )

        self.assertEqual(prepared["artifact_status"], "ai_ready")
        artifact = prepared["one_shot_ai_ready_artifact"]
        self.assertEqual(
            artifact["artifact_type"], "one_shot_ai_ready_execution_prompt"
        )
        self.assertIn("Task summary:", artifact["prompt_text"])
        self.assertIn("Traceability:", artifact["prompt_text"])
        self.assertEqual(
            artifact["prompt_sections"]["traceability"]["request_traceability_seed"],
            "trace-slice02-0001",
        )

    def test_missing_reviewable_bundle_field_is_rejected_explicitly(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")
        reviewable_summary = prepare_reviewable_single_ai_output_bundle(
            raw_request, run_id="slice-04-test-0002"
        )
        reviewable_summary["reviewable_output_bundle"]["traceability"].pop("task_manifest_id")

        with self.assertRaisesRegex(
            ExecutionPromptError,
            "traceability.task_manifest_id is required",
        ):
            build_one_shot_ai_ready_execution_prompt(reviewable_summary)

    def test_cli_outputs_ai_ready_artifact_summary(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "cli" / "request_prompt.py"),
                str(FIXTURE_DIR / "sample_request_slice02.yaml"),
                "--run-id",
                "slice-04-test-0003",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["summary"]["one_shot_ai_ready_artifact"]["artifact_type"],
            "one_shot_ai_ready_execution_prompt",
        )

    def test_cli_rejects_out_of_scope_request(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "cli" / "request_prompt.py"),
                str(FIXTURE_DIR / "sample_request_tdf.yaml"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("Slice 02 supports ATP requests only", payload["error"])


if __name__ == "__main__":
    unittest.main()
