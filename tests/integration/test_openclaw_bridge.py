"""Integration tests for the OpenClaw → ATP bridge.

Requires a running Ollama instance at http://127.0.0.1:11434 with qwen3:14b.
Tests are skipped (not failed) when Ollama is unreachable.
"""

from __future__ import annotations

import unittest
from urllib.error import URLError
from urllib.request import urlopen

from bridge.openclaw_bridge import bridge_request, BridgeError


def _ollama_available() -> bool:
    try:
        with urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as resp:
            return resp.status == 200
    except (URLError, OSError):
        return False


OLLAMA_AVAILABLE = _ollama_available()
SKIP_REASON = "Ollama not reachable at http://127.0.0.1:11434"


class TestBridgeHappyPath(unittest.TestCase):
    """1. Happy path: real request → ATP flow → success result."""

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_full_bridge_request(self):
        result = bridge_request({
            "text": "What does ATIS stand for in aviation? Reply in one sentence.",
            "model": "ollama/qwen3:14b",
            "context": "You are an aviation expert.",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["selected_provider"], "ollama")
        self.assertTrue(len(result["stdout"]) > 0, "Output must be non-empty")
        self.assertEqual(result["exit_code"], 0)

        # Bridge metadata
        self.assertEqual(result["bridge"]["source"], "openclaw")
        self.assertEqual(result["bridge"]["resolved_provider"], "ollama")
        self.assertEqual(result["bridge"]["resolved_model"], "qwen3:14b")

        # Ollama manifest
        self.assertIn("ollama_manifest", result)
        self.assertTrue(result["ollama_manifest"]["completion_validated"])
        self.assertGreater(result["ollama_manifest"]["response_time_ms"], 0)
        self.assertIsInstance(result["ollama_manifest"]["timestamp"], str)


class TestBridgeMissingText(unittest.TestCase):
    """2. Missing text: request without prompt → clear error."""

    def test_empty_text_raises(self):
        with self.assertRaises(BridgeError) as ctx:
            bridge_request({"model": "ollama/qwen3:14b"})
        self.assertIn("text", str(ctx.exception))

    def test_blank_text_raises(self):
        with self.assertRaises(BridgeError) as ctx:
            bridge_request({"text": "   ", "model": "ollama/qwen3:14b"})
        self.assertIn("text", str(ctx.exception))

    def test_no_fields_raises(self):
        with self.assertRaises(BridgeError):
            bridge_request({})


class TestBridgeModelFallback(unittest.TestCase):
    """3. Model fallback: no model specified → default qwen3:14b is used."""

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_default_model_when_omitted(self):
        result = bridge_request({
            "text": "Reply with exactly: OK",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["bridge"]["resolved_provider"], "ollama")
        self.assertEqual(result["bridge"]["resolved_model"], "qwen3:14b")
        self.assertTrue(len(result["stdout"]) > 0)

    @unittest.skipUnless(OLLAMA_AVAILABLE, SKIP_REASON)
    def test_model_without_provider_prefix(self):
        result = bridge_request({
            "text": "Reply with exactly: OK",
            "model": "qwen3:14b",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["bridge"]["resolved_provider"], "ollama")
        self.assertEqual(result["bridge"]["resolved_model"], "qwen3:14b")


if __name__ == "__main__":
    unittest.main()
