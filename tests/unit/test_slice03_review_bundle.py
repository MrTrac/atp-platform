"""Unit tests for ATP v1.1 Slice 03 reviewable output bundles."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.intake.loader import load_request
from core.intake.request_flow import prepare_single_ai_request_flow
from core.intake.review_bundle import (
    ReviewBundleError,
    build_reviewable_single_ai_output_bundle,
    prepare_reviewable_single_ai_output_bundle,
)


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"
ROOT_DIR = Path(__file__).resolve().parents[2]


class TestSlice03ReviewBundle(unittest.TestCase):
    """Cover the bounded Slice 03 reviewable bundle continuation."""

    def test_valid_request_produces_reviewable_bundle(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")

        prepared = prepare_reviewable_single_ai_output_bundle(raw_request, run_id="slice-03-test-0001")

        self.assertEqual(prepared["bundle_status"], "reviewable")
        bundle = prepared["reviewable_output_bundle"]
        self.assertEqual(bundle["bundle_type"], "reviewable_single_ai_output_bundle")
        self.assertEqual(
            bundle["review_surface"]["human_readable_sections"],
            [
                "request_identity",
                "normalized_task_summary",
                "scope_and_constraints",
                "single_ai_package_payload",
                "traceability",
            ],
        )
        self.assertEqual(
            bundle["traceability"]["request_traceability_seed"],
            "trace-slice02-0001",
        )

    def test_missing_upstream_package_field_is_rejected_explicitly(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")
        prepared_flow = prepare_single_ai_request_flow(raw_request, run_id="slice-03-test-0002")
        prepared_flow["single_ai_execution_package"].pop("package_id")

        with self.assertRaisesRegex(
            ReviewBundleError,
            "prepared_flow.single_ai_execution_package.package_id is required",
        ):
            build_reviewable_single_ai_output_bundle(prepared_flow)

    def test_cli_outputs_reviewable_bundle_summary(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "cli" / "request_bundle.py"),
                str(FIXTURE_DIR / "sample_request_slice02.yaml"),
                "--run-id",
                "slice-03-test-0003",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["summary"]["reviewable_output_bundle"]["bundle_type"],
            "reviewable_single_ai_output_bundle",
        )

    def test_cli_rejects_out_of_scope_request(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "cli" / "request_bundle.py"),
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
