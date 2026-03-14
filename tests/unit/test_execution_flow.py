"""Unit tests for ATP M6 execution flow."""

from __future__ import annotations

import unittest
from pathlib import Path

from adapters.subprocess.local_exec_adapter import execute_local
from core.execution.executor import ExecutionError, invoke_executor
from core.execution.output_normalizer import normalize_output
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


class TestExecutionFlow(unittest.TestCase):
    """Cover the supported local non-LLM execution path."""

    def test_local_non_llm_route_maps_to_local_exec_adapter(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_exec_echo.yaml"))
        raw_result = invoke_executor(
            normalized,
            {"selected_provider": "non_llm_execution", "selected_node": "local_mac"},
        )

        self.assertEqual(raw_result["exit_code"], 0)
        self.assertIn("hello", raw_result["stdout"])

    def test_local_exec_adapter_returns_exit_stdout_stderr_structure(self) -> None:
        result = execute_local({"payload": {"command_argv": ["echo", "hello"]}})

        self.assertEqual(set(result.keys()), {"command", "exit_code", "stdout", "stderr", "status", "notes"})
        self.assertEqual(result["exit_code"], 0)

    def test_output_normalizer_returns_stable_required_keys(self) -> None:
        normalized = normalize_output(
            raw_result={"command": ["echo", "hello"], "exit_code": 0, "stdout": "hello\n", "stderr": "", "notes": []},
            request_id="req-1",
            product="ATP",
            routing_result={"selected_provider": "non_llm_execution", "selected_node": "local_mac"},
        )

        self.assertEqual(
            set(normalized.keys()),
            {
                "execution_id",
                "request_id",
                "product",
                "selected_provider",
                "selected_node",
                "command",
                "exit_code",
                "stdout",
                "stderr",
                "status",
                "notes",
            },
        )

    def test_unsupported_route_returns_clear_error(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_exec_echo.yaml"))

        with self.assertRaisesRegex(ExecutionError, "Unsupported execution route"):
            invoke_executor(normalized, {"selected_provider": "", "selected_node": ""})


if __name__ == "__main__":
    unittest.main()
