"""Unit tests for ATP v1.2 Feature 02 execution session tracking."""

from __future__ import annotations

import json
import subprocess
import unittest
from collections import OrderedDict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
REQUEST_A = "tests/fixtures/requests/sample_request_slice02.yaml"
REQUEST_B = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class TestFeature02ExecutionSessionTracking(unittest.TestCase):
    """Lock the bounded repo-local execution session identity surface."""

    def test_root_help_mentions_execution_session_surface(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("execution-session  Inspect one bounded repo-local execution session", result.stdout)
        self.assertIn(f"./atp execution-session {REQUEST_A}", result.stdout)

    def test_execution_session_supports_single_request_identity(self) -> None:
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
        self.assertEqual(payload["command"], "execution-session")
        self.assertEqual(payload["request_files"], [REQUEST_A])
        self.assertEqual(
            payload["session_summary"]["session_id"],
            "session-single-req-atp-v1-1-slice02-0001",
        )
        self.assertEqual(payload["session_summary"]["session_mode"], "single_request")
        self.assertEqual(payload["session_summary"]["persistence_mode"], "derived_in_memory_only")

    def test_execution_session_supports_multi_request_identity(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", REQUEST_A, REQUEST_B],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertEqual(payload["request_files"], [REQUEST_A, REQUEST_B])
        self.assertEqual(payload["session_summary"]["session_mode"], "multi_request")
        self.assertEqual(payload["session_summary"]["request_count"], 2)
        self.assertEqual(
            payload["session_summary"]["request_ids"],
            ["req-atp-v1-1-slice02-0001", "req-atp-v1-1-slice02-0002"],
        )
        self.assertTrue(payload["session_summary"]["session_id"].startswith("session-multi-2-"))

    def test_single_request_outputs_share_same_session_id(self) -> None:
        flow_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        bundle_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-bundle", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        prompt_result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(flow_result.returncode, 0)
        self.assertEqual(bundle_result.returncode, 0)
        self.assertEqual(prompt_result.returncode, 0)

        flow_payload = json.loads(flow_result.stdout, object_pairs_hook=OrderedDict)
        bundle_payload = json.loads(bundle_result.stdout, object_pairs_hook=OrderedDict)
        prompt_payload = json.loads(prompt_result.stdout, object_pairs_hook=OrderedDict)

        session_id = flow_payload["review_summary"]["session_summary"]["session_id"]
        self.assertEqual(session_id, bundle_payload["review_summary"]["session_summary"]["session_id"])
        self.assertEqual(session_id, prompt_payload["review_summary"]["session_summary"]["session_id"])
        self.assertEqual(session_id, "session-single-req-atp-v1-1-slice02-0001")

    def test_multi_request_summary_includes_session_continuity(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow-multi", REQUEST_A, REQUEST_B],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        session_summary = payload["multi_request_summary"]["session_summary"]
        self.assertEqual(session_summary["session_mode"], "multi_request")
        self.assertEqual(session_summary["request_count"], 2)
        self.assertTrue(session_summary["session_id"].startswith("session-multi-2-"))

    def test_execution_session_explicitly_rules_out_runtime_state_subsystems(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        session_summary = payload["session_summary"]
        self.assertEqual(session_summary["session_scope"], "repo_local_operator_controlled")
        self.assertEqual(session_summary["persistence_mode"], "derived_in_memory_only")
        self.assertIn(
            "No background writer, daemon, service, or database is used.",
            session_summary["notes"],
        )

    def test_smoke_request_chain_still_passes_with_session_tracking_present(self) -> None:
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
