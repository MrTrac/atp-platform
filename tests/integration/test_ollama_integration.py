"""Integration test: ATP executor → Ollama adapter → live inference.

Requires a running Ollama instance at http://127.0.0.1:11434 with qwen3:14b.
Tests are skipped (not failed) when Ollama is unreachable.
"""

from __future__ import annotations

import json
import unittest
from urllib.error import URLError
from urllib.request import urlopen

from core.execution.executor import invoke_executor
from core.execution.output_normalizer import normalize_output


def _ollama_available() -> bool:
    """Check if Ollama is reachable."""
    try:
        with urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as resp:
            return resp.status == 200
    except (URLError, OSError):
        return False


OLLAMA_AVAILABLE = _ollama_available()
SKIP_REASON = "Ollama not reachable at http://127.0.0.1:11434"


class TestOllamaExecutorIntegration(unittest.TestCase):
    """End-to-end: ATP executor dispatches to Ollama and returns structured result."""

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_executor_ollama_happy_path(self):
        """Full path: executor → ollama adapter → live model → normalized result."""
        normalized_request = {
            "request_id": "integration-test-001",
            "product": "ATP",
            "payload": {
                "input_text": "In one sentence: what is AFTN in aviation?",
                "model": "qwen3:14b",
            },
        }
        routing_result = {
            "selected_provider": "ollama",
            "selected_node": "local_mac",
            "selected_provider_model": "qwen3:14b",
        }

        raw_result = invoke_executor(normalized_request, routing_result)

        # Verify raw result has the bridged shape
        self.assertEqual(raw_result["exit_code"], 0)
        self.assertEqual(raw_result["status"], "completed")
        self.assertTrue(len(raw_result["stdout"]) > 0, "Output should be non-empty")
        self.assertIn("ollama_manifest", raw_result)
        self.assertIsNotNone(raw_result["ollama_manifest"]["timestamp"])
        self.assertGreater(raw_result["ollama_manifest"]["response_time_ms"], 0)
        self.assertTrue(raw_result["ollama_manifest"]["completion_validated"])

        # Verify it normalizes cleanly through output_normalizer
        normalized = normalize_output(
            raw_result=raw_result,
            request_id="integration-test-001",
            product="ATP",
            routing_result=routing_result,
        )
        self.assertEqual(normalized["status"], "succeeded")
        self.assertEqual(normalized["selected_provider"], "ollama")
        self.assertTrue(len(normalized["stdout"]) > 0)

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_executor_ollama_with_context(self):
        """Verify system context is passed through to Ollama."""
        normalized_request = {
            "request_id": "integration-test-002",
            "product": "ATP",
            "payload": {
                "input_text": "What does NOTAM stand for?",
                "model": "qwen3:14b",
                "context": "You are an aviation expert. Reply in one sentence.",
            },
        }
        routing_result = {
            "selected_provider": "ollama",
            "selected_node": "local_mac",
            "selected_provider_model": "qwen3:14b",
        }

        raw_result = invoke_executor(normalized_request, routing_result)
        self.assertEqual(raw_result["exit_code"], 0)
        self.assertTrue(len(raw_result["stdout"]) > 0)

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_executor_ollama_manifest_complete(self):
        """Manifest fields must all have real values after a successful call."""
        normalized_request = {
            "request_id": "integration-test-003",
            "product": "ATP",
            "payload": {
                "input_text": "Reply with exactly: OK",
                "model": "qwen3:14b",
            },
        }
        routing_result = {
            "selected_provider": "ollama",
            "selected_node": "local_mac",
            "selected_provider_model": "qwen3:14b",
        }

        raw_result = invoke_executor(normalized_request, routing_result)
        manifest = raw_result["ollama_manifest"]

        self.assertIsInstance(manifest["timestamp"], str)
        self.assertGreater(len(manifest["timestamp"]), 0)
        self.assertIsInstance(manifest["response_time_ms"], int)
        self.assertGreaterEqual(manifest["response_time_ms"], 0)
        self.assertTrue(manifest["completion_validated"])


class TestOllamaExecutorContractValidation(unittest.TestCase):
    """Contract violations through executor path return structured errors, not exceptions."""

    def test_missing_model_returns_failed(self):
        """Missing model → exit_code 1, not an unhandled exception."""
        normalized_request = {
            "request_id": "contract-test-001",
            "product": "ATP",
            "payload": {"input_text": "Hello"},
        }
        routing_result = {
            "selected_provider": "ollama",
            "selected_node": "local_mac",
        }

        raw_result = invoke_executor(normalized_request, routing_result)
        self.assertEqual(raw_result["exit_code"], 1)
        self.assertEqual(raw_result["status"], "failed")
        self.assertIn("model", raw_result["stderr"])


if __name__ == "__main__":
    unittest.main()
