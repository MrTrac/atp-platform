"""Unit tests for ATP v1.8.0 cloud foundations.

Covers:
- OpenAI adapter: API key passthrough, payload building, success/error paths
- Retry/backoff: 429, 502, 503, 504, network errors, Retry-After header
- Per-model cost table: lookup by model, fallback to provider defaults
- Per-model timeout: get_timeout_for_model override
- Executor dispatch: openai handler in EXECUTOR_MAP
"""

from __future__ import annotations

import json
import os
import time
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from adapters.cloud.openai_adapter import execute_openai
from core.execution.executor import EXECUTOR_MAP
from core.pricing import calculate_cost, get_model_price, list_priced_models
from core.retry import _calculate_delay, _is_retryable, _retry_after_seconds, with_retry


def _mock_response(body: dict) -> MagicMock:
    """Build a mock urlopen response returning JSON."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestPricingTable(unittest.TestCase):
    """Per-model cost table lookup."""

    def test_known_model_uses_table(self) -> None:
        cost = calculate_cost("claude-sonnet-4-20250514", 1000, 500)
        # Sonnet 4: $3 in + $15 out per MTok
        expected = (1000 * 3 + 500 * 15) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_opus_pricing_higher(self) -> None:
        cost = calculate_cost("claude-opus-4-20250514", 1000, 1000)
        # Opus: $15/$75
        expected = (1000 * 15 + 1000 * 75) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_haiku_pricing_lower(self) -> None:
        cost = calculate_cost("claude-3-5-haiku-20241022", 1000, 1000)
        # Haiku: $0.80/$4
        expected = (1000 * 0.80 + 1000 * 4) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_openai_gpt4o_pricing(self) -> None:
        cost = calculate_cost("gpt-4o", 1000, 1000)
        # gpt-4o: $2.50/$10
        expected = (1000 * 2.5 + 1000 * 10) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_o1_pricing(self) -> None:
        cost = calculate_cost("o1", 1000, 1000)
        # o1: $15/$60
        expected = (1000 * 15 + 1000 * 60) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_unknown_model_falls_back_to_provider_default(self) -> None:
        cost = calculate_cost("claude-future-model", 1000, 1000, provider="anthropic")
        # default anthropic: $3/$15
        expected = (1000 * 3 + 1000 * 15) / 1_000_000
        self.assertAlmostEqual(cost, round(expected, 6))

    def test_unknown_model_no_provider_returns_zero(self) -> None:
        cost = calculate_cost("totally-unknown", 1000, 1000)
        self.assertEqual(cost, 0.0)

    def test_ollama_default_zero(self) -> None:
        cost = calculate_cost("any-ollama-model", 1000, 1000, provider="ollama")
        self.assertEqual(cost, 0.0)

    def test_get_model_price_known(self) -> None:
        price = get_model_price("claude-sonnet-4-20250514")
        self.assertIsNotNone(price)
        self.assertEqual(price.provider, "anthropic")
        self.assertEqual(price.input_per_mtok, 3.00)

    def test_get_model_price_unknown(self) -> None:
        self.assertIsNone(get_model_price("nonexistent-model-xyz"))

    def test_list_priced_models_includes_both_providers(self) -> None:
        models = list_priced_models()
        self.assertTrue(any(m.startswith("claude") for m in models))
        self.assertTrue(any(m.startswith("gpt") for m in models))
        self.assertIn("o1", models)


class TestRetryLogic(unittest.TestCase):
    """Retry + exponential backoff for transient errors."""

    def test_is_retryable_429(self) -> None:
        exc = HTTPError("http://x", 429, "Too Many", {}, BytesIO(b""))
        self.assertTrue(_is_retryable(exc))

    def test_is_retryable_502_503_504(self) -> None:
        for code in (502, 503, 504):
            exc = HTTPError("http://x", code, "msg", {}, BytesIO(b""))
            self.assertTrue(_is_retryable(exc), f"{code} should be retryable")

    def test_is_retryable_400_not_retried(self) -> None:
        exc = HTTPError("http://x", 400, "Bad Request", {}, BytesIO(b""))
        self.assertFalse(_is_retryable(exc))

    def test_is_retryable_network_error(self) -> None:
        self.assertTrue(_is_retryable(URLError("connection refused")))

    def test_is_retryable_value_error_not_retried(self) -> None:
        self.assertFalse(_is_retryable(ValueError("bad input")))

    def test_retry_after_header_parsed(self) -> None:
        class MockHeaders:
            def get(self, k, default=None):
                return "5" if k == "Retry-After" else default
        exc = HTTPError("http://x", 429, "Too Many", MockHeaders(), BytesIO(b""))
        self.assertEqual(_retry_after_seconds(exc), 5.0)

    def test_calculate_delay_uses_retry_after(self) -> None:
        delay = _calculate_delay(0, 1.0, 30.0, retry_after=10.0)
        self.assertEqual(delay, 10.0)

    def test_calculate_delay_caps_at_max(self) -> None:
        delay = _calculate_delay(10, 1.0, 30.0, retry_after=None)
        self.assertLessEqual(delay, 30.0)

    def test_with_retry_succeeds_first_attempt(self) -> None:
        calls = []
        def fn():
            calls.append(1)
            return "ok"
        result = with_retry(fn, sleep_fn=lambda _: None)
        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 1)

    def test_with_retry_succeeds_after_retry(self) -> None:
        calls = []
        def fn():
            calls.append(1)
            if len(calls) < 2:
                raise URLError("transient")
            return "ok"
        result = with_retry(fn, sleep_fn=lambda _: None)
        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 2)

    def test_with_retry_exhausts_attempts(self) -> None:
        calls = []
        def fn():
            calls.append(1)
            raise URLError("always fails")
        with self.assertRaises(URLError):
            with_retry(fn, max_attempts=3, sleep_fn=lambda _: None)
        self.assertEqual(len(calls), 3)

    def test_with_retry_does_not_retry_non_retryable(self) -> None:
        calls = []
        def fn():
            calls.append(1)
            raise ValueError("permanent")
        with self.assertRaises(ValueError):
            with_retry(fn, max_attempts=3, sleep_fn=lambda _: None)
        self.assertEqual(len(calls), 1)


class TestOpenAIAdapter(unittest.TestCase):
    """OpenAI adapter parity with Anthropic adapter."""

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_success_path(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": "Hello!"}}],
            "model": "gpt-4o",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        })
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = execute_openai({"model": "gpt-4o", "prompt": "Hi"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["output"], "Hello!")
        self.assertGreater(result["manifest"]["cost_usd"], 0)

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_api_key_from_request_body(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5},
        })
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            result = execute_openai({
                "model": "gpt-4o",
                "prompt": "Hi",
                "api_key": "sk-from-body",
            })
        self.assertEqual(result["status"], "success")
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        self.assertEqual(http_req.headers.get("Authorization"), "Bearer sk-from-body")

    def test_missing_api_key_returns_error(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            result = execute_openai({"model": "gpt-4o", "prompt": "Hi"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("OPENAI_API_KEY", result["error"])

    def test_missing_model_returns_contract_violation(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = execute_openai({"prompt": "Hi"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("model", result["error"])

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_o1_uses_max_completion_tokens(self, mock_urlopen: MagicMock) -> None:
        """o1/o3 models use max_completion_tokens, not max_tokens."""
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": "reasoning"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        })
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            execute_openai({"model": "o1", "prompt": "Hi"})
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        body = json.loads(http_req.data.decode("utf-8"))
        self.assertIn("max_completion_tokens", body)
        self.assertNotIn("max_tokens", body)

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_gpt4_uses_max_tokens(self, mock_urlopen: MagicMock) -> None:
        """Non-reasoning models use max_tokens."""
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5},
        })
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            execute_openai({"model": "gpt-4o", "prompt": "Hi"})
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        body = json.loads(http_req.data.decode("utf-8"))
        self.assertIn("max_tokens", body)
        self.assertNotIn("max_completion_tokens", body)

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_context_becomes_system_message(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5},
        })
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            execute_openai({
                "model": "gpt-4o",
                "prompt": "Hi",
                "context": "You are a helpful assistant.",
            })
        call_args = mock_urlopen.call_args
        http_req = call_args[0][0]
        body = json.loads(http_req.data.decode("utf-8"))
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(body["messages"][0]["content"], "You are a helpful assistant.")
        self.assertEqual(body["messages"][1]["role"], "user")

    @patch("adapters.cloud.openai_adapter.urlopen", side_effect=URLError("refused"))
    def test_network_failure_returns_structured_error(self, mock_urlopen: MagicMock) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = execute_openai({"model": "gpt-4o", "prompt": "Hi"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("OpenAI request failed", result["error"])

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_http_error_includes_diagnostic(self, mock_urlopen: MagicMock) -> None:
        error_body = json.dumps({"error": {"message": "invalid model"}}).encode("utf-8")
        mock_urlopen.side_effect = HTTPError(
            "http://x", 400, "Bad Request", {}, BytesIO(error_body)
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = execute_openai({"model": "bad-model", "prompt": "Hi"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("invalid model", result["error"])


class TestExecutorDispatch(unittest.TestCase):
    """OpenAI handler is registered in EXECUTOR_MAP."""

    def test_openai_in_executor_map(self) -> None:
        self.assertIn("openai", EXECUTOR_MAP)
        self.assertTrue(callable(EXECUTOR_MAP["openai"]))

    def test_all_4_providers_present(self) -> None:
        for p in ("non_llm_execution", "ollama", "anthropic", "openai"):
            self.assertIn(p, EXECUTOR_MAP, f"{p} should be in EXECUTOR_MAP")


class TestPerModelTimeout(unittest.TestCase):
    """get_timeout_for_model honors MODEL_TIMEOUTS overrides."""

    def test_default_when_no_override(self) -> None:
        from core.config import get_timeout_for_model
        # No env var set in test environment
        self.assertEqual(get_timeout_for_model("any-model", 120), 120)

    def test_model_specific_override_applied(self) -> None:
        with patch("core.config.MODEL_TIMEOUTS", {"o1": 600, "gpt-5": 300}):
            from core.config import get_timeout_for_model
            self.assertEqual(get_timeout_for_model("o1", 120), 600)
            self.assertEqual(get_timeout_for_model("gpt-5", 120), 300)
            self.assertEqual(get_timeout_for_model("other", 120), 120)


class TestAnthropicPricingMigration(unittest.TestCase):
    """Anthropic adapter now uses pricing module (not hardcoded)."""

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_haiku_cost_uses_haiku_pricing(self, mock_urlopen: MagicMock) -> None:
        """Haiku should be cheaper than Sonnet 4 (was hardcoded to Sonnet rates)."""
        mock_urlopen.return_value = _mock_response({
            "content": [{"type": "text", "text": "Hi"}],
            "usage": {"input_tokens": 1000, "output_tokens": 1000},
        })
        from adapters.cloud.anthropic_adapter import execute_anthropic
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = execute_anthropic({"model": "claude-3-5-haiku-20241022", "prompt": "Hi"})
        # Haiku cost should be MUCH less than Sonnet 4 ($3/$15 vs $0.80/$4)
        self.assertLess(result["manifest"]["cost_usd"], 0.005)


if __name__ == "__main__":
    unittest.main()
