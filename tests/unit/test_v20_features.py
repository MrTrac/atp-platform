"""Unit tests for ATP v2.0.0 streaming & cancellation.

Covers:
- In-flight tracker: register/unregister, cancel, list_active, is_active
- SSE event formatter: all event types produce valid SSE bytes
- Anthropic streaming: token + tool_call + manifest events, abort honored
- OpenAI streaming: token + tool_call (delta aggregation) + manifest events, abort honored
- Error paths: missing API key, contract violation, HTTP errors
"""

from __future__ import annotations

import json
import os
import threading
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from core import in_flight_tracker
from core import streaming as sse


def _mock_sse_response(sse_lines: list[bytes]) -> MagicMock:
    """Mock urlopen response that iterates SSE lines like a real stream."""
    resp = MagicMock()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    resp.__iter__ = lambda s: iter(sse_lines)
    return resp


class TestInFlightTracker(unittest.TestCase):

    def setUp(self) -> None:
        in_flight_tracker._reset()

    def tearDown(self) -> None:
        in_flight_tracker._reset()

    def test_register_returns_event_and_tracks(self) -> None:
        event = in_flight_tracker.register("req-1", provider="anthropic", model="claude-sonnet-4")
        self.assertIsInstance(event, threading.Event)
        self.assertTrue(in_flight_tracker.is_active("req-1"))

    def test_unregister_removes_entry(self) -> None:
        in_flight_tracker.register("req-1")
        in_flight_tracker.unregister("req-1")
        self.assertFalse(in_flight_tracker.is_active("req-1"))

    def test_cancel_sets_event_and_returns_true(self) -> None:
        event = in_flight_tracker.register("req-1")
        ok = in_flight_tracker.cancel("req-1")
        self.assertTrue(ok)
        self.assertTrue(event.is_set())

    def test_cancel_missing_returns_false(self) -> None:
        self.assertFalse(in_flight_tracker.cancel("nonexistent"))

    def test_list_active_snapshot(self) -> None:
        in_flight_tracker.register("r1", provider="anthropic", model="m1")
        in_flight_tracker.register("r2", provider="openai", model="m2")
        active = in_flight_tracker.list_active()
        ids = {e["request_id"] for e in active}
        self.assertEqual(ids, {"r1", "r2"})

    def test_get_abort_event(self) -> None:
        ev = in_flight_tracker.register("req-1")
        got = in_flight_tracker.get_abort_event("req-1")
        self.assertIs(got, ev)

    def test_get_abort_event_missing(self) -> None:
        self.assertIsNone(in_flight_tracker.get_abort_event("nonexistent"))

    def test_thread_safety_concurrent_register(self) -> None:
        """Register from 10 threads concurrently."""
        def worker(i: int) -> None:
            in_flight_tracker.register(f"req-{i}")
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(in_flight_tracker.list_active()), 10)


class TestSSEFormat(unittest.TestCase):
    """SSE event formatting produces valid UTF-8 bytes with event/data lines."""

    def _parse(self, raw: bytes) -> dict:
        text = raw.decode("utf-8")
        self.assertTrue(text.endswith("\n\n"))
        lines = text.strip().split("\n")
        event_line = [ln for ln in lines if ln.startswith("event:")][0]
        data_line = [ln for ln in lines if ln.startswith("data:")][0]
        return {
            "event": event_line[len("event:"):].strip(),
            "data": json.loads(data_line[len("data:"):].strip()),
        }

    def test_start_event(self) -> None:
        parsed = self._parse(sse.format_start("req-1", "anthropic", "claude-sonnet-4"))
        self.assertEqual(parsed["event"], "start")
        self.assertEqual(parsed["data"]["request_id"], "req-1")

    def test_token_event(self) -> None:
        parsed = self._parse(sse.format_token("hello"))
        self.assertEqual(parsed["event"], "token")
        self.assertEqual(parsed["data"]["text"], "hello")

    def test_manifest_event(self) -> None:
        parsed = self._parse(sse.format_manifest({"tokens": 42, "cost_usd": 0.001}))
        self.assertEqual(parsed["event"], "manifest")
        self.assertEqual(parsed["data"]["manifest"]["tokens"], 42)

    def test_error_event(self) -> None:
        parsed = self._parse(sse.format_error("boom", "network_error"))
        self.assertEqual(parsed["event"], "error")
        self.assertEqual(parsed["data"]["error_code"], "network_error")

    def test_done_event(self) -> None:
        parsed = self._parse(sse.format_done())
        self.assertEqual(parsed["event"], "done")

    def test_aborted_event(self) -> None:
        parsed = self._parse(sse.format_aborted("client_cancelled"))
        self.assertEqual(parsed["event"], "aborted")
        self.assertEqual(parsed["data"]["reason"], "client_cancelled")

    def test_tool_delta_event(self) -> None:
        parsed = self._parse(sse.format_tool_delta({"id": "t1", "name": "get_weather", "input": {}}))
        self.assertEqual(parsed["event"], "tool_call")
        self.assertEqual(parsed["data"]["name"], "get_weather")


class TestAnthropicStreaming(unittest.TestCase):

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_streaming_token_events(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        sse_body = [
            b'data: {"type": "message_start", "message": {"usage": {"input_tokens": 10}}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hello"}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": " world"}}\n',
            b'data: {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 5}}\n',
            b'data: [DONE]\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            events = list(execute_anthropic_stream({
                "model": "claude-sonnet-4-20250514",
                "prompt": "Hi",
            }))

        kinds = [e[0] for e in events]
        self.assertEqual(kinds.count("token"), 2)
        self.assertEqual(kinds[-1], "manifest")
        tokens = [e[1]["text"] for e in events if e[0] == "token"]
        self.assertEqual(tokens, ["Hello", " world"])
        manifest = events[-1][1]["manifest"]
        self.assertEqual(manifest["input_tokens"], 10)
        self.assertEqual(manifest["output_tokens"], 5)
        self.assertEqual(manifest["stop_reason"], "end_turn")

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_streaming_tool_use(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        sse_body = [
            b'data: {"type": "message_start", "message": {"usage": {"input_tokens": 20}}}\n',
            b'data: {"type": "content_block_start", "content_block": {"type": "tool_use", "id": "toolu_1", "name": "get_weather"}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "input_json_delta", "partial_json": "{\\"location\\":"}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "input_json_delta", "partial_json": "\\"Saigon\\"}"}}\n',
            b'data: {"type": "content_block_stop"}\n',
            b'data: {"type": "message_delta", "delta": {"stop_reason": "tool_use"}, "usage": {"output_tokens": 15}}\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            events = list(execute_anthropic_stream({
                "model": "claude-sonnet-4-20250514",
                "prompt": "Weather?",
                "tools": [{"name": "get_weather", "description": "Get weather",
                           "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}}}],
            }))

        tool_events = [e for e in events if e[0] == "tool_call"]
        self.assertEqual(len(tool_events), 1)
        self.assertEqual(tool_events[0][1]["name"], "get_weather")
        self.assertEqual(tool_events[0][1]["input"], {"location": "Saigon"})

    def test_streaming_missing_api_key_yields_error(self) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            events = list(execute_anthropic_stream({
                "model": "claude-sonnet-4-20250514", "prompt": "Hi",
            }))
        self.assertEqual(events[0][0], "error")
        self.assertIn("ANTHROPIC_API_KEY", events[0][1]["message"])

    def test_streaming_missing_model_yields_error(self) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            events = list(execute_anthropic_stream({"prompt": "Hi"}))
        self.assertEqual(events[0][0], "error")
        self.assertEqual(events[0][1]["error_code"], "contract_violation")

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_streaming_abort_stops_early(self, mock_urlopen: MagicMock) -> None:
        """abort_event.set() should cause generator to yield 'aborted' and stop."""
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        sse_body = [
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "one"}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "two"}}\n',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "three"}}\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)

        abort = threading.Event()
        abort.set()  # Pre-set so generator aborts on first iteration
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            events = list(execute_anthropic_stream(
                {"model": "claude-sonnet-4-20250514", "prompt": "Hi"},
                abort_event=abort,
            ))
        kinds = [e[0] for e in events]
        self.assertIn("aborted", kinds)
        # No manifest emitted when aborted
        self.assertNotIn("manifest", kinds)


class TestOpenAIStreaming(unittest.TestCase):

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_streaming_token_events(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        sse_body = [
            b'data: {"choices": [{"delta": {"content": "Hello"}, "finish_reason": null}]}\n',
            b'data: {"choices": [{"delta": {"content": " world"}, "finish_reason": null}]}\n',
            b'data: {"choices": [{"delta": {}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}\n',
            b'data: [DONE]\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            events = list(execute_openai_stream({"model": "gpt-4o", "prompt": "Hi"}))

        kinds = [e[0] for e in events]
        self.assertEqual(kinds.count("token"), 2)
        self.assertEqual(kinds[-1], "manifest")
        manifest = events[-1][1]["manifest"]
        self.assertEqual(manifest["input_tokens"], 10)
        self.assertEqual(manifest["output_tokens"], 5)
        self.assertEqual(manifest["finish_reason"], "stop")

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_streaming_tool_call_delta_aggregation(self, mock_urlopen: MagicMock) -> None:
        """OpenAI streams tool_calls piecewise; adapter must reassemble."""
        from adapters.cloud.openai_adapter import execute_openai_stream
        sse_body = [
            b'data: {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "call_1", "function": {"name": "get_weather"}}]}}]}\n',
            b'data: {"choices": [{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "{\\"loc"}}]}}]}\n',
            b'data: {"choices": [{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "ation\\":\\"Saigon\\"}"}}]}}]}\n',
            b'data: {"choices": [{"delta": {}, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 30, "completion_tokens": 10}}\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            events = list(execute_openai_stream({"model": "gpt-4o", "prompt": "Weather?"}))

        tool_events = [e for e in events if e[0] == "tool_call"]
        self.assertEqual(len(tool_events), 1)
        self.assertEqual(tool_events[0][1]["name"], "get_weather")
        self.assertEqual(tool_events[0][1]["input"], {"location": "Saigon"})
        self.assertEqual(tool_events[0][1]["id"], "call_1")

    def test_streaming_missing_api_key_yields_error(self) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            events = list(execute_openai_stream({"model": "gpt-4o", "prompt": "Hi"}))
        self.assertEqual(events[0][0], "error")
        self.assertIn("OPENAI_API_KEY", events[0][1]["message"])

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_streaming_http_error_yields_error(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        err_body = json.dumps({"error": {"message": "invalid model"}}).encode("utf-8")
        mock_urlopen.side_effect = HTTPError("http://x", 400, "Bad Request", {}, BytesIO(err_body))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            events = list(execute_openai_stream({"model": "bad", "prompt": "Hi"}))
        self.assertEqual(events[0][0], "error")
        self.assertIn("invalid model", events[0][1]["message"])

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_streaming_network_error_yields_error(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        mock_urlopen.side_effect = URLError("refused")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            events = list(execute_openai_stream({"model": "gpt-4o", "prompt": "Hi"}))
        self.assertEqual(events[0][0], "error")

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_streaming_abort_stops_early(self, mock_urlopen: MagicMock) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        sse_body = [
            b'data: {"choices": [{"delta": {"content": "a"}, "finish_reason": null}]}\n',
            b'data: {"choices": [{"delta": {"content": "b"}, "finish_reason": null}]}\n',
        ]
        mock_urlopen.return_value = _mock_sse_response(sse_body)
        abort = threading.Event()
        abort.set()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            events = list(execute_openai_stream(
                {"model": "gpt-4o", "prompt": "Hi"}, abort_event=abort,
            ))
        kinds = [e[0] for e in events]
        self.assertIn("aborted", kinds)


class TestBridgeServerCancellation(unittest.TestCase):
    """Verify the in-flight tracker integrates with bridge_server endpoints.

    Note: we don't spin up a real HTTP server here — just verify the tracker
    behaviors the DELETE /runs/<id> handler relies on.
    """

    def setUp(self) -> None:
        in_flight_tracker._reset()

    def tearDown(self) -> None:
        in_flight_tracker._reset()

    def test_cancel_active_request(self) -> None:
        event = in_flight_tracker.register("streaming-1", provider="anthropic", model="claude-sonnet-4")
        self.assertFalse(event.is_set())
        cancelled = in_flight_tracker.cancel("streaming-1")
        self.assertTrue(cancelled)
        self.assertTrue(event.is_set())

    def test_cancel_after_unregister_returns_false(self) -> None:
        in_flight_tracker.register("req-1")
        in_flight_tracker.unregister("req-1")
        self.assertFalse(in_flight_tracker.cancel("req-1"))

    def test_list_active_reports_abort_state(self) -> None:
        in_flight_tracker.register("r1")
        in_flight_tracker.cancel("r1")
        active = in_flight_tracker.list_active()
        self.assertEqual(len(active), 1)
        self.assertTrue(active[0]["aborted"])


if __name__ == "__main__":
    unittest.main()
