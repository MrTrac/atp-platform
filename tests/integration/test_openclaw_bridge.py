"""Integration tests for the OpenClaw → ATP bridge.

The bridge routes to the Anthropic cloud LLM (the sole/default provider on
macOS per ~/AI_OS/00_AUTHORITY/Global_Mac_No_Ollama_Rule.md). Live-call tests
are skipped (not failed) when ANTHROPIC_API_KEY is not set.
"""

from __future__ import annotations

import os
import unittest

from bridge.openclaw_bridge import bridge_request, BridgeError


ANTHROPIC_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))
SKIP_REASON = "ANTHROPIC_API_KEY not set — live Anthropic call skipped"


class TestBridgeHappyPath(unittest.TestCase):
    """1. Happy path: real request → ATP flow → success result."""

    @unittest.skipUnless(ANTHROPIC_AVAILABLE, SKIP_REASON)
    def test_full_bridge_request(self):
        result = bridge_request({
            "text": "What does ATIS stand for in aviation? Reply in one sentence.",
            "model": "anthropic/claude-haiku-4-5-20251001",
            "context": "You are an aviation expert.",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["selected_provider"], "anthropic")
        self.assertTrue(len(result["stdout"]) > 0, "Output must be non-empty")
        self.assertEqual(result["exit_code"], 0)

        # Bridge metadata
        self.assertEqual(result["bridge"]["source"], "openclaw")
        self.assertEqual(result["bridge"]["resolved_provider"], "anthropic")
        self.assertEqual(result["bridge"]["resolved_model"], "claude-haiku-4-5-20251001")


class TestBridgeMissingText(unittest.TestCase):
    """2. Missing text: request without prompt → clear error."""

    def test_empty_text_raises(self):
        with self.assertRaises(BridgeError) as ctx:
            bridge_request({"model": "anthropic/claude-haiku-4-5-20251001"})
        self.assertIn("text", str(ctx.exception))

    def test_blank_text_raises(self):
        with self.assertRaises(BridgeError) as ctx:
            bridge_request({"text": "   ", "model": "anthropic/claude-haiku-4-5-20251001"})
        self.assertIn("text", str(ctx.exception))

    def test_no_fields_raises(self):
        with self.assertRaises(BridgeError):
            bridge_request({})


class TestBridgeModelFallback(unittest.TestCase):
    """3. Model fallback: no/bare model spec → default anthropic provider."""

    @unittest.skipUnless(ANTHROPIC_AVAILABLE, SKIP_REASON)
    def test_default_model_when_omitted(self):
        result = bridge_request({
            "text": "Reply with exactly: OK",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["bridge"]["resolved_provider"], "anthropic")
        self.assertEqual(result["bridge"]["resolved_model"], "claude-haiku-4-5-20251001")
        self.assertTrue(len(result["stdout"]) > 0)

    @unittest.skipUnless(ANTHROPIC_AVAILABLE, SKIP_REASON)
    def test_model_without_provider_prefix(self):
        result = bridge_request({
            "text": "Reply with exactly: OK",
            "model": "claude-haiku-4-5-20251001",
        })

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["bridge"]["resolved_provider"], "anthropic")
        self.assertEqual(result["bridge"]["resolved_model"], "claude-haiku-4-5-20251001")


if __name__ == "__main__":
    unittest.main()
