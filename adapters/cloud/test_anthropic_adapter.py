"""Tests for ATP Anthropic cloud adapter.

All tests mock the API — no real Anthropic calls.
"""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch, MagicMock

from adapters.cloud.anthropic_adapter import execute_anthropic


# --- Fixtures ---

MOCK_ANTHROPIC_RESPONSE = json.dumps({
    "id": "msg_mock",
    "type": "message",
    "role": "assistant",
    "content": [{"type": "text", "text": "AFTN is the Aeronautical Fixed Telecommunication Network."}],
    "model": "claude-sonnet-4-20250514",
    "usage": {"input_tokens": 25, "output_tokens": 15},
}).encode("utf-8")

MOCK_EMPTY_RESPONSE = json.dumps({
    "id": "msg_mock",
    "type": "message",
    "role": "assistant",
    "content": [{"type": "text", "text": ""}],
    "model": "claude-sonnet-4-20250514",
    "usage": {"input_tokens": 10, "output_tokens": 0},
}).encode("utf-8")

REQUIRED_TOP_KEYS = {
    "status", "route_type", "provider", "model",
    "output", "manifest", "escalation_triggered", "error",
}
REQUIRED_MANIFEST_KEYS = {
    "timestamp", "response_time_ms", "token_count", "completion_validated",
}


def _mock_urlopen(raw_bytes):
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw_bytes
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestMissingApiKey(unittest.TestCase):
    """1. Missing ANTHROPIC_API_KEY → status=failed, clear error."""

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_returns_failed(self):
        # Ensure key is not set
        os.environ.pop("ANTHROPIC_API_KEY", None)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Hello",
        })
        self.assertEqual(result["status"], "failed")
        self.assertIn("ANTHROPIC_API_KEY", result["error"])
        self.assertEqual(result["provider"], "anthropic")
        self.assertEqual(result["route_type"], "cloud")


class TestInputContractValidation(unittest.TestCase):
    """2. Missing model or prompt → clear error."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_missing_model(self):
        result = execute_anthropic({"prompt": "Hello"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("model", result["error"])

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_missing_prompt_and_messages(self):
        result = execute_anthropic({"model": "claude-sonnet-4-20250514"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("prompt", result["error"])


class TestOutputStructure(unittest.TestCase):
    """3. Mock response → all fields present."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_output_structure_complete(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_ANTHROPIC_RESPONSE)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })

        self.assertEqual(set(result.keys()), REQUIRED_TOP_KEYS)
        self.assertEqual(set(result["manifest"].keys()), REQUIRED_MANIFEST_KEYS)
        self.assertEqual(result["status"], "success")
        self.assertIn("AFTN", result["output"])
        self.assertIsNone(result["error"])

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_token_count_from_usage(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_ANTHROPIC_RESPONSE)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })
        self.assertEqual(result["manifest"]["token_count"], 40)  # 25 + 15


class TestRouteType(unittest.TestCase):
    """4. route_type is always "cloud"."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_route_type_is_cloud(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_ANTHROPIC_RESPONSE)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })
        self.assertEqual(result["route_type"], "cloud")

    def test_route_type_cloud_on_error(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })
        self.assertEqual(result["route_type"], "cloud")


class TestEscalationTriggered(unittest.TestCase):
    """5. escalation_triggered is always True for cloud adapter."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_escalation_triggered_true(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_ANTHROPIC_RESPONSE)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })
        self.assertTrue(result["escalation_triggered"])

    def test_escalation_triggered_true_on_error(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        result = execute_anthropic({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Test",
        })
        self.assertTrue(result["escalation_triggered"])


if __name__ == "__main__":
    unittest.main()
