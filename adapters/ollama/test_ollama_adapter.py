"""Tests for ATP Ollama adapter.

Covers:
1. Happy path: call qwen3:14b, verify response structure
2. Contract validation: missing model → clear error
3. Completion validation: output is non-empty
4. Manifest check: all manifest fields have real values
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from adapters.ollama.ollama_adapter import (
    OllamaAdapterError,
    execute_ollama,
    execute_ollama_stream,
)


# --- Fixtures ---

MOCK_OLLAMA_RESPONSE = json.dumps({
    "message": {"role": "assistant", "content": "Hello! How can I help you?"},
    "eval_count": 12,
    "prompt_eval_count": 8,
}).encode("utf-8")

MOCK_EMPTY_RESPONSE = json.dumps({
    "message": {"role": "assistant", "content": ""},
}).encode("utf-8")

REQUIRED_TOP_KEYS = {
    "status", "route_type", "provider", "model",
    "output", "manifest", "escalation_triggered", "error",
}
REQUIRED_MANIFEST_KEYS = {
    "timestamp", "response_time_ms", "token_count", "completion_validated",
}


def _mock_urlopen(raw_bytes):
    """Return a context-manager mock that yields raw_bytes on read()."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw_bytes
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# --- Test Cases ---


class TestHappyPath(unittest.TestCase):
    """1. Happy path: structured response from qwen3:14b."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_successful_call(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_OLLAMA_RESPONSE)
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Say hello"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["route_type"], "local")
        self.assertEqual(result["provider"], "ollama")
        self.assertEqual(result["model"], "qwen3:14b")
        self.assertIn("Hello", result["output"])
        self.assertIsNone(result["error"])
        self.assertFalse(result["escalation_triggered"])

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_response_structure_complete(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_OLLAMA_RESPONSE)
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        self.assertEqual(set(result.keys()), REQUIRED_TOP_KEYS)
        self.assertEqual(set(result["manifest"].keys()), REQUIRED_MANIFEST_KEYS)


class TestContractValidation(unittest.TestCase):
    """2. Contract validation: missing required fields → structured error."""

    def test_missing_model(self):
        result = execute_ollama({"prompt": "Hello"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("model", result["error"])

    def test_missing_prompt_and_messages(self):
        result = execute_ollama({"model": "qwen3:14b"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("prompt", result["error"])

    def test_empty_request(self):
        result = execute_ollama({})
        self.assertEqual(result["status"], "failed")


class TestCompletionValidation(unittest.TestCase):
    """3. Completion validation: empty response → failed status."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_empty_response_fails_validation(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_EMPTY_RESPONSE)
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["manifest"]["completion_validated"])
        self.assertIsNotNone(result["error"])

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_non_empty_response_passes(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_OLLAMA_RESPONSE)
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["manifest"]["completion_validated"])


class TestManifest(unittest.TestCase):
    """4. Manifest check: all fields have real values."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_manifest_fields_populated(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_OLLAMA_RESPONSE)
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        manifest = result["manifest"]
        self.assertIsInstance(manifest["timestamp"], str)
        self.assertGreater(len(manifest["timestamp"]), 0)
        self.assertIsInstance(manifest["response_time_ms"], int)
        self.assertGreaterEqual(manifest["response_time_ms"], 0)
        self.assertEqual(manifest["token_count"], 20)  # 12 + 8
        self.assertTrue(manifest["completion_validated"])

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_manifest_on_error_still_populated(self, mock_urlopen_fn):
        mock_urlopen_fn.side_effect = URLError("Connection refused")
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        manifest = result["manifest"]
        self.assertIsInstance(manifest["timestamp"], str)
        self.assertIsInstance(manifest["response_time_ms"], int)
        self.assertIsNone(manifest["token_count"])
        self.assertFalse(manifest["completion_validated"])


class TestContextHandling(unittest.TestCase):
    """Verify bounded context is injected as system message."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_context_becomes_system_message(self, mock_urlopen_fn):
        mock_urlopen_fn.return_value = _mock_urlopen(MOCK_OLLAMA_RESPONSE)

        execute_ollama({
            "model": "qwen3:14b",
            "prompt": "Hello",
            "context": "You are a helpful assistant.",
        })

        call_args = mock_urlopen_fn.call_args
        sent_request = call_args[0][0]
        sent_body = json.loads(sent_request.data.decode("utf-8"))
        self.assertEqual(sent_body["messages"][0]["role"], "system")
        self.assertEqual(sent_body["messages"][0]["content"], "You are a helpful assistant.")


class TestNetworkError(unittest.TestCase):
    """Network errors return structured error result, not exceptions."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_connection_refused(self, mock_urlopen_fn):
        mock_urlopen_fn.side_effect = URLError("Connection refused")
        result = execute_ollama({"model": "qwen3:14b", "prompt": "Test"})

        self.assertEqual(result["status"], "failed")
        self.assertIn("Connection refused", result["error"])
        self.assertEqual(result["route_type"], "local")
        self.assertEqual(result["provider"], "ollama")


class _FakeStreamResponse:
    """Mock urlopen response that iterates NDJSON lines like Ollama's stream."""

    def __init__(self, lines):
        self._lines = [
            ln.encode("utf-8") if isinstance(ln, str) else ln
            for ln in lines
        ]

    def __iter__(self):
        return iter(self._lines)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _FlagAbortEvent:
    """Minimal abort_event mimicking threading.Event.is_set()."""

    def __init__(self, set_after: int = 0):
        self._set_after = set_after
        self._calls = 0

    def is_set(self) -> bool:
        self._calls += 1
        return self._calls > self._set_after


class TestExecuteOllamaStream(unittest.TestCase):
    """v2.2.0 — Ollama streaming via /api/chat (NDJSON)."""

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_stream_yields_token_then_manifest(self, mock_urlopen):
        mock_urlopen.return_value = _FakeStreamResponse([
            json.dumps({"message": {"content": "Hello"}, "done": False}) + "\n",
            json.dumps({"message": {"content": " world"}, "done": False}) + "\n",
            json.dumps({
                "message": {"content": ""},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 4,
                "eval_count": 2,
            }) + "\n",
        ])
        events = list(execute_ollama_stream({"model": "qwen3:14b", "prompt": "hi"}))
        kinds = [k for k, _ in events]
        self.assertEqual(kinds, ["token", "token", "manifest"])
        self.assertEqual(events[0][1]["text"], "Hello")
        self.assertEqual(events[1][1]["text"], " world")
        manifest = events[2][1]["manifest"]
        self.assertEqual(manifest["input_tokens"], 4)
        self.assertEqual(manifest["output_tokens"], 2)
        self.assertEqual(manifest["token_count"], 6)
        self.assertEqual(manifest["stop_reason"], "stop")
        self.assertTrue(manifest["completion_validated"])
        self.assertEqual(manifest["cost_usd"], 0.0)

    def test_stream_validates_required_model(self):
        events = list(execute_ollama_stream({"prompt": "hi"}))
        self.assertEqual(len(events), 1)
        kind, data = events[0]
        self.assertEqual(kind, "error")
        self.assertEqual(data["error_code"], "contract_violation")

    def test_stream_validates_required_prompt_or_messages(self):
        events = list(execute_ollama_stream({"model": "qwen3:14b"}))
        self.assertEqual(events[0][0], "error")
        self.assertEqual(events[0][1]["error_code"], "contract_violation")

    @patch("adapters.ollama.ollama_adapter.urlopen", side_effect=URLError("connection refused"))
    def test_stream_url_error_yields_error_event(self, _mock):
        events = list(execute_ollama_stream({"model": "qwen3:14b", "prompt": "hi"}))
        self.assertEqual(events[0][0], "error")
        self.assertIn("Ollama stream failed", events[0][1]["message"])

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_stream_aborts_when_abort_event_set(self, mock_urlopen):
        mock_urlopen.return_value = _FakeStreamResponse([
            json.dumps({"message": {"content": "first"}, "done": False}) + "\n",
            json.dumps({"message": {"content": "second"}, "done": False}) + "\n",
            json.dumps({"message": {"content": ""}, "done": True}) + "\n",
        ])
        events = list(execute_ollama_stream(
            {"model": "qwen3:14b", "prompt": "hi"},
            abort_event=_FlagAbortEvent(set_after=0),
        ))
        kinds = [k for k, _ in events]
        self.assertIn("aborted", kinds)
        self.assertNotIn("manifest", kinds)

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_stream_skips_blank_and_invalid_json_lines(self, mock_urlopen):
        mock_urlopen.return_value = _FakeStreamResponse([
            "\n",
            "not-json\n",
            json.dumps({"message": {"content": "ok"}, "done": False}) + "\n",
            json.dumps({"message": {"content": ""}, "done": True}) + "\n",
        ])
        events = list(execute_ollama_stream({"model": "qwen3:14b", "prompt": "hi"}))
        kinds = [k for k, _ in events]
        self.assertEqual(kinds, ["token", "manifest"])
        self.assertEqual(events[0][1]["text"], "ok")

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_stream_payload_sets_stream_true(self, mock_urlopen):
        captured = {}

        def fake(req, timeout=120):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeStreamResponse([
                json.dumps({"message": {"content": "x"}, "done": True}) + "\n",
            ])

        mock_urlopen.side_effect = fake
        list(execute_ollama_stream({"model": "qwen3:14b", "prompt": "hi"}))
        self.assertTrue(captured["body"]["stream"])
        self.assertEqual(captured["body"]["model"], "qwen3:14b")

    @patch("adapters.ollama.ollama_adapter.urlopen")
    def test_stream_empty_output_marks_completion_invalid(self, mock_urlopen):
        mock_urlopen.return_value = _FakeStreamResponse([
            json.dumps({"message": {"content": ""}, "done": True}) + "\n",
        ])
        events = list(execute_ollama_stream({"model": "qwen3:14b", "prompt": "hi"}))
        manifest = events[-1][1]["manifest"]
        self.assertFalse(manifest["completion_validated"])


if __name__ == "__main__":
    unittest.main()
