"""Unit tests for ATP v1.2 Feature 01 multi-request execution surface."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
REQUEST_A = "tests/fixtures/requests/sample_request_slice02.yaml"
REQUEST_B = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class TestFeature01MultiRequestSurface(unittest.TestCase):
    """Lock the bounded multi-request flow entry surface."""

    def test_request_flow_multi_runs_in_input_order(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow-multi", REQUEST_A, REQUEST_B],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "request-flow-multi")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["request_files"], [REQUEST_A, REQUEST_B])
        self.assertEqual(payload["run_id"], "multi-flow-preview-0001")

        multi_request_summary = payload["multi_request_summary"]
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


if __name__ == "__main__":
    unittest.main()
