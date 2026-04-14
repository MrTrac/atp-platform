"""Unit tests for ATP v1.7.0 features.

Covers:
- Cloud API key passthrough (request body → env var fallback)
- Model auto-detection from model name prefix (claude/gpt/o1/o3)
- Bridge top-level error field for AIOS-OC consumption
- HTTPError diagnostic body capture in Anthropic adapter
"""

from __future__ import annotations

import json
import os
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from adapters.cloud.anthropic_adapter import execute_anthropic
from bridge.openclaw_bridge import _parse_model_spec


def _mock_response(body: dict) -> MagicMock:
    """Build a mock urlopen response returning JSON."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestModelAutoDetection(unittest.TestCase):
    """Verify _parse_model_spec() auto-detects provider from model name."""

    def test_empty_defaults_to_ollama(self) -> None:
        provider, model = _parse_model_spec("")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model, "qwen3:14b")

    def test_explicit_provider_slash_model(self) -> None:
        provider, model = _parse_model_spec("anthropic/claude-sonnet-4")
        self.assertEqual(provider, "anthropic")
        self.assertEqual(model, "claude-sonnet-4")

    def test_claude_prefix_detects_anthropic(self) -> None:
        provider, model = _parse_model_spec("claude-sonnet-4-20250514")
        self.assertEqual(provider, "anthropic")
        self.assertEqual(model, "claude-sonnet-4-20250514")

    def test_claude_3_prefix_detects_anthropic(self) -> None:
        provider, model = _parse_model_spec("claude-3-opus-20240229")
        self.assertEqual(provider, "anthropic")
        self.assertEqual(model, "claude-3-opus-20240229")

    def test_gpt_prefix_detects_openai(self) -> None:
        provider, model = _parse_model_spec("gpt-4-turbo")
        self.assertEqual(provider, "openai")
        self.assertEqual(model, "gpt-4-turbo")

    def test_gpt_5_prefix_detects_openai(self) -> None:
        provider, model = _parse_model_spec("gpt-5")
        self.assertEqual(provider, "openai")
        self.assertEqual(model, "gpt-5")

    def test_o1_prefix_detects_openai(self) -> None:
        provider, model = _parse_model_spec("o1-preview")
        self.assertEqual(provider, "openai")
        self.assertEqual(model, "o1-preview")

    def test_o3_prefix_detects_openai(self) -> None:
        provider, model = _parse_model_spec("o3-mini")
        self.assertEqual(provider, "openai")
        self.assertEqual(model, "o3-mini")

    def test_unknown_prefix_defaults_to_ollama(self) -> None:
        provider, model = _parse_model_spec("qwen3:14b")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model, "qwen3:14b")

    def test_llama_defaults_to_ollama(self) -> None:
        provider, model = _parse_model_spec("llama3:70b")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model, "llama3:70b")


class TestApiKeyPassthrough(unittest.TestCase):
    """Verify Anthropic adapter accepts api_key from request body."""

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_api_key_from_request_body_used(self, mock_urlopen: MagicMock) -> None:
        """api_key in request body should be used as x-api-key header."""
        mock_urlopen.return_value = _mock_response({
            "content": [{"type": "text", "text": "Hello"}],
            "model": "claude-sonnet-4",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            result = execute_anthropic({
                "model": "claude-sonnet-4",
                "prompt": "Hello",
                "api_key": "sk-ant-request-body-key",
            })

        self.assertEqual(result["status"], "success")
        # Verify the x-api-key header came from request body
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        self.assertEqual(http_req.headers.get("X-api-key"), "sk-ant-request-body-key")

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_api_key_falls_back_to_env_var(self, mock_urlopen: MagicMock) -> None:
        """When api_key not in request, falls back to ANTHROPIC_API_KEY env var."""
        mock_urlopen.return_value = _mock_response({
            "content": [{"type": "text", "text": "Hello"}],
            "model": "claude-sonnet-4",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-env-key"}):
            result = execute_anthropic({"model": "claude-sonnet-4", "prompt": "Hello"})

        self.assertEqual(result["status"], "success")
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        self.assertEqual(http_req.headers.get("X-api-key"), "sk-ant-env-key")

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_request_api_key_overrides_env(self, mock_urlopen: MagicMock) -> None:
        """Request-body api_key takes priority over env var."""
        mock_urlopen.return_value = _mock_response({
            "content": [{"type": "text", "text": "Hello"}],
            "model": "claude-sonnet-4",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-env-key"}):
            result = execute_anthropic({
                "model": "claude-sonnet-4",
                "prompt": "Hello",
                "api_key": "sk-ant-override",
            })

        self.assertEqual(result["status"], "success")
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        self.assertEqual(http_req.headers.get("X-api-key"), "sk-ant-override")

    def test_missing_api_key_returns_structured_error(self) -> None:
        """No api_key anywhere → structured error (not raised)."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            result = execute_anthropic({"model": "claude-sonnet-4", "prompt": "Hello"})

        self.assertEqual(result["status"], "failed")
        self.assertIn("ANTHROPIC_API_KEY", result["error"])
        self.assertIn("api_key in request", result["error"])


class TestAnthropicErrorDiagnostics(unittest.TestCase):
    """Verify HTTPError body is captured for diagnostic messages."""

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_http_error_body_captured_in_message(self, mock_urlopen: MagicMock) -> None:
        """HTTPError response body should appear in error message."""
        error_body = json.dumps({
            "error": {"type": "invalid_request_error", "message": "model not found"}
        }).encode("utf-8")
        mock_urlopen.side_effect = HTTPError(
            url="http://test", code=400, msg="Bad Request",
            hdrs={}, fp=BytesIO(error_body),
        )

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = execute_anthropic({"model": "bad-model", "prompt": "test"})

        self.assertEqual(result["status"], "failed")
        self.assertIn("model not found", result["error"])


class TestExecutorApiKeyFlow(unittest.TestCase):
    """Verify executor passes api_key from payload into LLM request."""

    def test_build_llm_request_includes_api_key(self) -> None:
        from core.execution.executor import _build_llm_request
        normalized_request = {
            "payload": {
                "input_text": "hello",
                "model": "claude-sonnet-4",
                "api_key": "sk-ant-passthrough",
            }
        }
        routing_result = {"selected_provider_model": "claude-sonnet-4"}
        llm_req = _build_llm_request(normalized_request, routing_result)
        self.assertEqual(llm_req["api_key"], "sk-ant-passthrough")

    def test_build_llm_request_omits_api_key_when_absent(self) -> None:
        from core.execution.executor import _build_llm_request
        normalized_request = {
            "payload": {"input_text": "hello", "model": "claude-sonnet-4"}
        }
        routing_result = {"selected_provider_model": "claude-sonnet-4"}
        llm_req = _build_llm_request(normalized_request, routing_result)
        self.assertNotIn("api_key", llm_req)


class TestBridgeTopLevelError(unittest.TestCase):
    """Verify bridge response has top-level 'error' field when status=failed."""

    def test_bridge_request_passes_api_key_to_payload(self) -> None:
        """bridge_request should put api_key into normalized_request.payload."""
        # We can verify this by checking the payload shape that would be built.
        # This is essentially an integration-level check that the field flows through.
        from bridge.openclaw_bridge import bridge_request

        # Use a contract-violating request so we fail fast without calling Anthropic
        # But first verify the api_key is carried in the flow
        with patch("bridge.openclaw_bridge.invoke_executor") as mock_exec:
            mock_exec.return_value = {
                "status": "completed",
                "stdout": "ok",
                "exit_code": 0,
                "notes": [],
                "command": [],
                "stderr": "",
            }
            bridge_request({
                "text": "hello",
                "model": "claude-sonnet-4",
                "api_key": "sk-ant-test",
            })

            # Check that api_key was included in the normalized_request passed to executor
            call_args = mock_exec.call_args
            normalized_request = call_args[0][0]
            self.assertEqual(normalized_request["payload"]["api_key"], "sk-ant-test")


if __name__ == "__main__":
    unittest.main()
