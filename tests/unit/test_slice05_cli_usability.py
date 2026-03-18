"""Unit tests for ATP v1.1 Slice 05 CLI usability hardening."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestSlice05CliUsability(unittest.TestCase):
    """Lock the bounded operator usability/help contract for the current CLI chain."""

    def test_root_help_lists_command_descriptions_and_examples(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "cli" / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("ATP v1.1 execution CLI", result.stdout)
        self.assertIn("request-flow    Build the Slice 02 normalized request flow", result.stdout)
        self.assertIn("request-bundle  Build the Slice 03 reviewable output bundle", result.stdout)
        self.assertIn("request-prompt  Build the Slice 04 one-shot AI-ready prompt artifact", result.stdout)
        self.assertIn(
            f"./cli/atp request-flow {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn("Canonical bounded-chain fixture policy:", result.stdout)
        self.assertIn(CANONICAL_SAMPLE_REQUEST, result.stdout)
        self.assertIn(
            "Use this same fixture for help examples, repo-root smoke verification, and bounded happy-path checks.",
            result.stdout,
        )
        self.assertIn("Canonical verification contract from repo root:", result.stdout)
        self.assertIn("verify-smoke  -> ./atp smoke-request-chain", result.stdout)
        self.assertIn(
            f"verify-flow   -> ./atp request-flow {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn(
            f"verify-bundle -> ./atp request-bundle {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn(
            f"verify-prompt -> ./atp request-prompt {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn(
            "Expected bounded result: all commands exit cleanly on the canonical fixture without changing execution scope.",
            result.stdout,
        )
        self.assertIn("Execution control boundaries:", result.stdout)
        self.assertIn(
            "control-mode  -> repo-local, human-gated, bounded single-AI execution only",
            result.stdout,
        )
        self.assertIn("auto-execute  -> disabled", result.stdout)
        self.assertIn(
            "release-gates -> merge main / push main / tag release remain unauthorized here",
            result.stdout,
        )
        self.assertIn("Canonical bounded operator path from repo root:", result.stdout)
        self.assertIn("verify  -> ./atp smoke-request-chain", result.stdout)
        self.assertIn(
            f"review  -> ./atp request-bundle {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn(
            f"handoff -> ./atp request-prompt {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )

    def test_request_flow_help_includes_description_and_example(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "cli" / "request_flow.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Prepare the ATP Slice 02 thin request flow", result.stdout)
        self.assertIn(
            f"./cli/atp request-flow {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn("Canonical repo-root sample", result.stdout)

    def test_request_bundle_help_includes_description_and_example(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "cli" / "request_bundle.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Prepare the ATP Slice 03 reviewable bundle", result.stdout)
        self.assertIn(
            f"./cli/atp request-bundle {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn("Canonical repo-root sample", result.stdout)

    def test_request_prompt_help_includes_description_and_example(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "cli" / "request_prompt.py"), "-h"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Prepare the ATP Slice 04 one-shot AI-ready prompt artifact", result.stdout)
        self.assertIn(
            f"./cli/atp request-prompt {CANONICAL_SAMPLE_REQUEST}",
            result.stdout,
        )
        self.assertIn("Canonical repo-root sample", result.stdout)

    def test_missing_request_file_guidance_is_actionable(self) -> None:
        commands = [
            ("request_flow.py", "./cli/atp request-flow"),
            ("request_bundle.py", "./cli/atp request-bundle"),
            ("request_prompt.py", "./cli/atp request-prompt"),
        ]

        for script_name, command_name in commands:
            with self.subTest(script_name=script_name):
                result = subprocess.run(
                    [sys.executable, str(ROOT_DIR / "cli" / script_name)],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertIn("the following arguments are required: request_file", result.stderr)
                self.assertIn(
                    "Next step: run the command from repo root with the canonical sample request.",
                    result.stderr,
                )
                self.assertIn(
                    f"Example: {command_name} {CANONICAL_SAMPLE_REQUEST}",
                    result.stderr,
                )


if __name__ == "__main__":
    unittest.main()
