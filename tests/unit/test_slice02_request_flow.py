"""Unit tests for ATP v1.1 Slice 02 thin request flow."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.intake.loader import load_request
from core.intake.request_flow import RequestFlowError, prepare_single_ai_request_flow


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"
ROOT_DIR = Path(__file__).resolve().parents[2]


class TestSlice02RequestFlow(unittest.TestCase):
    """Cover the first usable request intake to single-AI package flow."""

    def test_valid_request_is_normalized_into_single_ai_package(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")

        prepared = prepare_single_ai_request_flow(raw_request, run_id="slice-02-test-0001")

        self.assertEqual(prepared["flow_status"], "accepted")
        self.assertEqual(prepared["product"], "ATP")
        self.assertEqual(
            prepared["normalized_task"]["task_type"],
            "single_ai_execution_package_preparation",
        )
        self.assertEqual(
            prepared["single_ai_execution_package"]["package_type"],
            "single_ai_execution_package",
        )
        self.assertEqual(
            prepared["single_ai_execution_package"]["instructions"]["scope"],
            ["single_ai_package_flow", "atp_repo_only"],
        )

    def test_missing_traceability_seed_is_rejected_explicitly(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")
        raw_request["payload"].pop("request_traceability_seed")

        with self.assertRaisesRegex(RequestFlowError, "payload.request_traceability_seed is required"):
            prepare_single_ai_request_flow(raw_request, run_id="slice-02-test-0002")

    def test_out_of_scope_product_is_rejected_explicitly(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_tdf.yaml")

        with self.assertRaisesRegex(RequestFlowError, "Slice 02 supports ATP requests only"):
            prepare_single_ai_request_flow(raw_request, run_id="slice-02-test-0003")

    def test_cli_outputs_error_for_out_of_scope_request(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "cli" / "request_flow.py"),
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
