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
    """Capture and then lock one bounded readability improvement for v1.2 surfaces."""

    def test_multi_request_output_currently_requires_deep_scan_for_primary_path(self) -> None:
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
        self.assertIn("request_ids", summary)
        self.assertIn("request_flows", summary)
        self.assertIn("session_summary", summary)
        self.assertNotIn("operator_scan_summary", summary)

    def test_execution_session_output_currently_lacks_first_scan_summary(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", REQUEST_A],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertIn("session_summary", payload)
        self.assertNotIn("operator_scan_summary", payload)


if __name__ == "__main__":
    unittest.main()
