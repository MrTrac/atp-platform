"""Unit tests for ATP v1.2 Feature 01 multi-request execution surface."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
REQUEST_A = "tests/fixtures/requests/sample_request_slice02.yaml"
REQUEST_B = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class TestFeature01MultiRequestSurface(unittest.TestCase):
    """Lock the bounded multi-request flow entry surface."""

    def test_root_help_mentions_multi_request_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("request-flow-multi  Build multiple Slice 02 request flows", result.stdout)
        self.assertIn(
            f"./atp request-flow-multi {REQUEST_A} {REQUEST_B}",
            result.stdout,
        )

    def test_request_flow_multi_runs_in_input_order(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow-multi", REQUEST_A, REQUEST_B],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["command"], "request-flow-multi")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["request_files"], [REQUEST_A, REQUEST_B])
        self.assertEqual(payload["run_id"], "multi-flow-preview-0001")
        self.assertEqual(
            list(payload.keys()),
            ["command", "status", "request_files", "run_id", "multi_request_summary"],
        )

        multi_request_summary = payload["multi_request_summary"]
        self.assertEqual(
            list(multi_request_summary.keys())[:8],
            [
                "multi_request_id",
                "processing_mode",
                "ordering_basis",
                "request_count",
                "accepted_request_count",
                "supported_flow",
                "notes",
                "request_ids",
            ],
        )
        self.assertEqual(multi_request_summary["processing_mode"], "sequential_operator_controlled")
        self.assertEqual(multi_request_summary["ordering_basis"], "input_order")
        self.assertEqual(multi_request_summary["request_count"], 2)
        self.assertEqual(multi_request_summary["accepted_request_count"], 2)
        self.assertEqual(
            multi_request_summary["request_ids"],
            ["req-atp-v1-1-slice02-0001", "req-atp-v1-1-slice02-0002"],
        )
        self.assertEqual(
            [item["request_file"] for item in multi_request_summary["request_flows"]],
            [REQUEST_A, REQUEST_B],
        )
        self.assertEqual(
            [item["run_id"] for item in multi_request_summary["request_flows"]],
            ["multi-flow-preview-0001-item-01", "multi-flow-preview-0001-item-02"],
        )
        self.assertEqual(
            [item["summary"]["request_id"] for item in multi_request_summary["request_flows"]],
            ["req-atp-v1-1-slice02-0001", "req-atp-v1-1-slice02-0002"],
        )

    def test_request_flow_multi_help_and_minimum_arity_guidance_are_bounded(self) -> None:
        help_result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "cli" / "request_flow_multi.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("Prepare multiple ATP Slice 02 request flows", help_result.stdout)
        self.assertIn(
            f"./atp request-flow-multi {REQUEST_A} {REQUEST_B}",
            help_result.stdout,
        )

        arity_result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "cli" / "request_flow_multi.py"), REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(arity_result.returncode, 2)
        self.assertIn("request_files must contain at least 2", arity_result.stderr)
        self.assertIn(
            f"Example: ./atp request-flow-multi {REQUEST_A} {REQUEST_B}",
            arity_result.stderr,
        )

    def test_request_flow_multi_reports_failing_request_context(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow-multi", REQUEST_A, "does/not/exist.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["command"], "request-flow-multi")
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error_stage"], "request_loading")
        self.assertEqual(payload["error_kind"], "request_file_not_found")
        self.assertEqual(payload["failed_request_file"], "does/not/exist.yaml")
        self.assertEqual(payload["failed_request_index"], 2)
        self.assertEqual(payload["processed_request_count"], 1)
        self.assertIn("./atp request-flow-multi", payload["next_step"])

    def test_single_request_flow_remains_unchanged_from_repo_root(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(
            list(payload.keys()),
            ["command", "status", "request_file", "run_id", "review_summary", "summary"],
        )
        self.assertEqual(payload["command"], "request-flow")
        self.assertEqual(payload["request_file"], REQUEST_A)
        self.assertEqual(payload["review_summary"]["result_status"], "accepted")
        self.assertNotIn("request_files", payload)
        self.assertNotIn("multi_request_summary", payload)

    def test_smoke_request_chain_still_passes_after_multi_request_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
