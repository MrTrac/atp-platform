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
            list(payload.keys()),
            ["command", "status", "request_files", "session_summary"],
        )
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


if __name__ == "__main__":
    unittest.main()
