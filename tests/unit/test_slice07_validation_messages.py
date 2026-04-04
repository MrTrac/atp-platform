"""Unit tests for ATP v1.1 Slice 07 validation-message hardening."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

from core.intake.loader import load_request


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT_DIR / "tests" / "fixtures" / "requests"
CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


def _run_cli(script_name: str, request_file: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT_DIR / "cli" / script_name), request_file],
        check=False,
        capture_output=True,
        text=True,
    )


def _load_payload(stdout: str) -> OrderedDict[str, object]:
    return json.loads(stdout, object_pairs_hook=OrderedDict)


class TestSlice07ValidationMessages(unittest.TestCase):
    """Lock the bounded invalid-input contract for request-chain CLIs."""

    def test_missing_request_file_includes_stage_kind_and_next_step(self) -> None:
        result = _run_cli("request_flow.py", "does/not/exist.yaml")

        self.assertEqual(result.returncode, 1)
        payload = _load_payload(result.stdout)
        self.assertEqual(
            list(payload.keys()),
            [
                "command",
                "status",
                "request_file",
                "run_id",
                "error_stage",
                "error_kind",
                "error",
                "next_step",
                "validation_evidence_summary",
            ],
        )
        self.assertEqual(payload["error_stage"], "request_loading")
        self.assertEqual(payload["error_kind"], "request_file_not_found")
        self.assertIn("./atp request-flow", payload["next_step"])
        self.assertEqual(
            payload["validation_evidence_summary"],
            {
                "failed_command": "request-flow",
                "failed_stage": "request_loading",
                "failed_kind": "request_file_not_found",
                "bounded_scope_preserved": True,
                "canonical_recheck_command": "./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml",
            },
        )

    def test_invalid_yaml_is_classified_clearly_for_all_request_chain_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_yaml_path = Path(temp_dir) / "invalid_request.yaml"
            invalid_yaml_path.write_text("request_id: broken\n  - invalid\n", encoding="utf-8")

            for script_name, command_name in [
                ("request_flow.py", "request-flow"),
                ("request_bundle.py", "request-bundle"),
                ("request_prompt.py", "request-prompt"),
            ]:
                with self.subTest(script_name=script_name):
                    result = _run_cli(script_name, str(invalid_yaml_path))

                    self.assertEqual(result.returncode, 1)
                    payload = _load_payload(result.stdout)
                    self.assertEqual(payload["command"], command_name)
                    self.assertEqual(payload["error_stage"], "request_loading")
                    self.assertEqual(payload["error_kind"], "invalid_yaml")
                    self.assertIn("Unsupported YAML structure", payload["error"])
                    self.assertIn(CANONICAL_SAMPLE_REQUEST, payload["next_step"])
                    self.assertEqual(
                        payload["validation_evidence_summary"],
                        {
                            "failed_command": command_name,
                            "failed_stage": "request_loading",
                            "failed_kind": "invalid_yaml",
                            "bounded_scope_preserved": True,
                            "canonical_recheck_command": f"./atp {command_name} {CANONICAL_SAMPLE_REQUEST}",
                        },
                    )

    def test_missing_required_field_is_classified_as_request_flow_validation(self) -> None:
        raw_request = load_request(FIXTURE_DIR / "sample_request_slice02.yaml")
        raw_request["payload"].pop("request_traceability_seed")

        with tempfile.TemporaryDirectory() as temp_dir:
            request_path = Path(temp_dir) / "missing_required.json"
            request_path.write_text(json.dumps(raw_request), encoding="utf-8")

            for script_name, command_name in [
                ("request_flow.py", "request-flow"),
                ("request_bundle.py", "request-bundle"),
                ("request_prompt.py", "request-prompt"),
            ]:
                with self.subTest(script_name=script_name):
                    result = _run_cli(script_name, str(request_path))

                    self.assertEqual(result.returncode, 1)
                    payload = _load_payload(result.stdout)
                    self.assertEqual(payload["command"], command_name)
                    self.assertEqual(payload["error_stage"], "request_flow_preparation")
                    self.assertEqual(payload["error_kind"], "missing_required_field")
                    self.assertIn("payload.request_traceability_seed is required.", payload["error"])
                    self.assertIn(CANONICAL_SAMPLE_REQUEST, payload["next_step"])
                    self.assertEqual(
                        payload["validation_evidence_summary"],
                        {
                            "failed_command": command_name,
                            "failed_stage": "request_flow_preparation",
                            "failed_kind": "missing_required_field",
                            "bounded_scope_preserved": True,
                            "canonical_recheck_command": f"./atp {command_name} {CANONICAL_SAMPLE_REQUEST}",
                        },
                    )

    def test_unsupported_request_shape_is_classified_consistently(self) -> None:
        unsupported_request = str(FIXTURE_DIR / "sample_request_tdf.yaml")

        for script_name, command_name in [
            ("request_flow.py", "request-flow"),
            ("request_bundle.py", "request-bundle"),
            ("request_prompt.py", "request-prompt"),
        ]:
            with self.subTest(script_name=script_name):
                result = _run_cli(script_name, unsupported_request)

                self.assertEqual(result.returncode, 1)
                payload = _load_payload(result.stdout)
                self.assertEqual(payload["command"], command_name)
                self.assertEqual(payload["error_stage"], "request_flow_preparation")
                self.assertEqual(payload["error_kind"], "unsupported_request_shape")
                self.assertIn("Slice 02 supports ATP requests only.", payload["error"])
                self.assertIn(command_name, payload["next_step"])
                self.assertEqual(
                    payload["validation_evidence_summary"],
                    {
                        "failed_command": command_name,
                        "failed_stage": "request_flow_preparation",
                        "failed_kind": "unsupported_request_shape",
                        "bounded_scope_preserved": True,
                        "canonical_recheck_command": f"./atp {command_name} {CANONICAL_SAMPLE_REQUEST}",
                    },
                )


if __name__ == "__main__":
    unittest.main()
