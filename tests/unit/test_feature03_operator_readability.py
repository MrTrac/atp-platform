"""Evidence and contract tests for ATP v1.2 Feature 03 readability layer."""

from __future__ import annotations

import json
import subprocess
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
REQUEST_A = "tests/fixtures/requests/sample_request_slice02.yaml"
REQUEST_B = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class TestFeature03OperatorReadability(unittest.TestCase):
    """Lock one bounded readability improvement for v1.2 expanded surfaces."""

    def test_multi_request_output_has_compact_operator_scan_summary(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow-multi", REQUEST_A, REQUEST_B],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        summary = payload["multi_request_summary"]
        self.assertIn("operator_scan_summary", summary)
        self.assertIn("request_ids", summary)
        self.assertIn("request_flows", summary)
        self.assertIn("session_summary", summary)
        self.assertEqual(
            summary["operator_scan_summary"],
            {
                "primary_focus": "request_flows",
                "session_id": "session-multi-2-5ee1c97dd7ad",
                "request_count": 2,
                "primary_request_id": "req-atp-v1-1-slice02-0001",
                "first_review_target": "request_flows[0].summary",
                "bounded_posture": "sequential_operator_controlled",
                "next_safe_bounded_action": "review prepared request_flows in input order",
            },
        )

    def test_execution_session_output_has_first_scan_summary(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(
            list(payload.keys())[:5],
            ["command", "status", "request_files", "operator_scan_summary", "session_summary"],
        )
        self.assertIn("artifact_continuity_anchors", payload)
        self.assertIn("integration_readiness_summary", payload)
        self.assertIn("session_summary", payload)
        self.assertEqual(
            payload["operator_scan_summary"],
            {
                "primary_focus": "session_summary",
                "session_id": "session-single-req-atp-v1-1-slice02-0001",
                "session_mode": "single_request",
                "request_count": 1,
                "primary_request_id": "req-atp-v1-1-slice02-0001",
                "first_review_target": "session_summary.request_ids",
                "bounded_posture": "repo_local_derived_only",
                "next_safe_bounded_action": "review the ordered request_ids, then continue with explicit request-chain commands from repo root",
            },
        )

    def test_single_request_request_chain_outputs_do_not_gain_extra_scan_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertNotIn("operator_scan_summary", payload)
        self.assertNotIn("operator_scan_summary", payload["review_summary"])

    def test_smoke_request_chain_still_passes_without_readability_drift(self) -> None:
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
