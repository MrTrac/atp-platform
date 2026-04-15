"""Unit tests for ATP v1.9.0 agentic capabilities.

Covers:
- Tool use: tools/tool_choice payload, tool_calls extraction (Anthropic + OpenAI)
- JSON mode: payload modification (Anthropic system instruction; OpenAI response_format)
- Vision: messages with image blocks pass through unchanged
- Capabilities matrix: registry entries loadable
- Bridge propagation: tools/tool_choice/json_mode flow incoming → adapter
- Executor flow: agentic fields propagate through _build_llm_request
"""

from __future__ import annotations

import json
import os
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from adapters.cloud.anthropic_adapter import (
    _build_payload as _anthropic_build_payload,
    _extract_tool_calls as _anthropic_extract_tool_calls,
    _validate_completion as _anthropic_validate_completion,
    execute_anthropic,
)
from adapters.cloud.openai_adapter import (
    _build_payload as _openai_build_payload,
    _extract_tool_calls as _openai_extract_tool_calls,
    _validate_completion as _openai_validate_completion,
    execute_openai,
)


def _mock_response(body: dict) -> MagicMock:
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


# Sample weather tool — Anthropic format
SAMPLE_TOOL_ANTHROPIC = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
}

# Sample weather tool — OpenAI format
SAMPLE_TOOL_OPENAI = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
}


class TestAnthropicToolUse(unittest.TestCase):
    """Anthropic tool use payload + extraction."""

    def test_tools_added_to_payload(self) -> None:
        payload = _anthropic_build_payload({
            "model": "claude-sonnet-4-20250514",
            "prompt": "What's the weather in Saigon?",
            "tools": [SAMPLE_TOOL_ANTHROPIC],
        })
        self.assertEqual(payload["tools"], [SAMPLE_TOOL_ANTHROPIC])

    def test_tool_choice_added(self) -> None:
        payload = _anthropic_build_payload({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Use the tool.",
            "tools": [SAMPLE_TOOL_ANTHROPIC],
            "tool_choice": {"type": "tool", "name": "get_weather"},
        })
        self.assertEqual(payload["tool_choice"]["name"], "get_weather")

    def test_no_tools_no_tools_field(self) -> None:
        payload = _anthropic_build_payload({"model": "claude-sonnet-4-20250514", "prompt": "Hi"})
        self.assertNotIn("tools", payload)

    def test_extract_tool_calls(self) -> None:
        body = {
            "content": [
                {"type": "text", "text": "Let me check."},
                {"type": "tool_use", "id": "toolu_1", "name": "get_weather",
                 "input": {"location": "Saigon"}},
            ]
        }
        calls = _anthropic_extract_tool_calls(body)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "get_weather")
        self.assertEqual(calls[0]["input"]["location"], "Saigon")

    def test_completion_valid_with_tool_use_only(self) -> None:
        """Tool-use-only response (no text) is still a valid completion."""
        body = {"content": [{"type": "tool_use", "id": "x", "name": "get_weather", "input": {}}]}
        self.assertTrue(_anthropic_validate_completion(body))


class TestAnthropicJsonMode(unittest.TestCase):
    """Anthropic JSON mode appends instruction to system prompt."""

    def test_json_mode_appends_instruction(self) -> None:
        payload = _anthropic_build_payload({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Give me a fact",
            "json_mode": True,
        })
        self.assertIn("JSON", payload["system"])

    def test_json_mode_with_existing_context_appends(self) -> None:
        payload = _anthropic_build_payload({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Hi",
            "context": "You are helpful.",
            "json_mode": True,
        })
        self.assertIn("You are helpful.", payload["system"])
        self.assertIn("JSON", payload["system"])

    def test_no_json_mode_no_instruction(self) -> None:
        payload = _anthropic_build_payload({
            "model": "claude-sonnet-4-20250514",
            "prompt": "Hi",
            "context": "You are helpful.",
        })
        self.assertEqual(payload.get("system"), "You are helpful.")


class TestAnthropicVision(unittest.TestCase):
    """Vision: image content blocks pass through messages naturally."""

    def test_image_content_block_passes_through(self) -> None:
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}},
            ],
        }]
        payload = _anthropic_build_payload({"model": "claude-sonnet-4-20250514", "messages": messages})
        self.assertEqual(payload["messages"], messages)


class TestOpenAIToolUse(unittest.TestCase):
    """OpenAI tool use payload + extraction."""

    def test_tools_added_to_payload(self) -> None:
        payload = _openai_build_payload({
            "model": "gpt-4o",
            "prompt": "Weather?",
            "tools": [SAMPLE_TOOL_OPENAI],
        })
        self.assertEqual(payload["tools"], [SAMPLE_TOOL_OPENAI])

    def test_tool_choice_added(self) -> None:
        payload = _openai_build_payload({
            "model": "gpt-4o",
            "prompt": "Weather?",
            "tools": [SAMPLE_TOOL_OPENAI],
            "tool_choice": {"type": "function", "function": {"name": "get_weather"}},
        })
        self.assertEqual(payload["tool_choice"]["function"]["name"], "get_weather")

    def test_extract_tool_calls(self) -> None:
        body = {
            "choices": [{
                "message": {
                    "content": None,
                    "tool_calls": [{
                        "id": "call_abc",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"location": "Saigon"}',
                        },
                    }],
                },
                "finish_reason": "tool_calls",
            }]
        }
        calls = _openai_extract_tool_calls(body)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "get_weather")
        self.assertEqual(calls[0]["input"]["location"], "Saigon")
        self.assertEqual(calls[0]["id"], "call_abc")

    def test_extract_tool_calls_handles_invalid_json_args(self) -> None:
        body = {
            "choices": [{"message": {"tool_calls": [{
                "id": "x", "function": {"name": "f", "arguments": "not-json"},
            }]}}]
        }
        calls = _openai_extract_tool_calls(body)
        self.assertEqual(calls[0]["input"]["_raw"], "not-json")

    def test_completion_valid_with_tool_calls_only(self) -> None:
        """Tool-call-only response (no content) is still a valid completion."""
        body = {"choices": [{"message": {"content": None, "tool_calls": [{"id": "x", "function": {"name": "f", "arguments": "{}"}}]}}]}
        self.assertTrue(_openai_validate_completion(body))


class TestOpenAIJsonMode(unittest.TestCase):
    """OpenAI JSON mode sets response_format."""

    def test_json_mode_sets_response_format(self) -> None:
        payload = _openai_build_payload({
            "model": "gpt-4o",
            "prompt": "Give me a JSON fact",
            "json_mode": True,
        })
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    def test_no_json_mode_no_response_format(self) -> None:
        payload = _openai_build_payload({"model": "gpt-4o", "prompt": "Hi"})
        self.assertNotIn("response_format", payload)


class TestOpenAIVision(unittest.TestCase):
    """OpenAI vision: image_url content parts pass through."""

    def test_image_url_passes_through(self) -> None:
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
            ],
        }]
        payload = _openai_build_payload({"model": "gpt-4o", "messages": messages})
        self.assertEqual(payload["messages"], messages)


class TestCapabilitiesRegistry(unittest.TestCase):
    """New v1.9.0 capability YAML entries are loadable."""

    REGISTRY = Path(__file__).resolve().parents[2] / "registry" / "capabilities"

    def test_llm_tool_use_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(self.REGISTRY / "llm_tool_use.yaml")
        self.assertEqual(entry["capability"], "llm_tool_use")

    def test_llm_json_mode_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(self.REGISTRY / "llm_json_mode.yaml")
        self.assertEqual(entry["capability"], "llm_json_mode")

    def test_llm_vision_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(self.REGISTRY / "llm_vision.yaml")
        self.assertEqual(entry["capability"], "llm_vision")

    def test_anthropic_provider_lists_v19_capabilities(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(self.REGISTRY.parent / "providers" / "anthropic_cloud.yaml")
        for cap in ("llm_tool_use", "llm_json_mode", "llm_vision"):
            self.assertIn(cap, entry["supported_capabilities"], f"anthropic missing {cap}")

    def test_openai_provider_lists_v19_capabilities(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(self.REGISTRY.parent / "providers" / "openai_cloud.yaml")
        for cap in ("llm_tool_use", "llm_json_mode", "llm_vision"):
            self.assertIn(cap, entry["supported_capabilities"], f"openai missing {cap}")


class TestExecutorAgenticFlow(unittest.TestCase):
    """Executor _build_llm_request propagates agentic fields."""

    def test_tools_propagate(self) -> None:
        from core.execution.executor import _build_llm_request
        normalized = {"payload": {
            "input_text": "Hi",
            "model": "claude-sonnet-4-20250514",
            "tools": [SAMPLE_TOOL_ANTHROPIC],
            "tool_choice": {"type": "auto"},
        }}
        routing = {"selected_provider_model": "claude-sonnet-4-20250514"}
        req = _build_llm_request(normalized, routing)
        self.assertEqual(req["tools"], [SAMPLE_TOOL_ANTHROPIC])
        self.assertEqual(req["tool_choice"], {"type": "auto"})

    def test_json_mode_propagates(self) -> None:
        from core.execution.executor import _build_llm_request
        normalized = {"payload": {"input_text": "Hi", "model": "gpt-4o", "json_mode": True}}
        routing = {"selected_provider_model": "gpt-4o"}
        req = _build_llm_request(normalized, routing)
        self.assertTrue(req["json_mode"])

    def test_no_agentic_fields_omitted(self) -> None:
        from core.execution.executor import _build_llm_request
        normalized = {"payload": {"input_text": "Hi", "model": "gpt-4o"}}
        routing = {"selected_provider_model": "gpt-4o"}
        req = _build_llm_request(normalized, routing)
        self.assertNotIn("tools", req)
        self.assertNotIn("json_mode", req)


class TestBridgePropagation(unittest.TestCase):
    """bridge_request routes tools/json_mode through to executor."""

    @patch("bridge.openclaw_bridge.invoke_executor")
    def test_tools_in_incoming_reach_executor(self, mock_exec: MagicMock) -> None:
        from bridge.openclaw_bridge import bridge_request
        mock_exec.return_value = {
            "status": "completed", "stdout": "ok", "exit_code": 0,
            "notes": [], "command": [], "stderr": "",
        }
        bridge_request({
            "text": "Use weather tool",
            "model": "claude-sonnet-4-20250514",
            "tools": [SAMPLE_TOOL_ANTHROPIC],
            "tool_choice": {"type": "auto"},
            "json_mode": True,
        })
        normalized_request = mock_exec.call_args[0][0]
        self.assertEqual(normalized_request["payload"]["tools"], [SAMPLE_TOOL_ANTHROPIC])
        self.assertEqual(normalized_request["payload"]["tool_choice"], {"type": "auto"})
        self.assertTrue(normalized_request["payload"]["json_mode"])

    @patch("bridge.openclaw_bridge.invoke_executor")
    def test_tool_calls_surface_in_response(self, mock_exec: MagicMock) -> None:
        from bridge.openclaw_bridge import bridge_request
        mock_exec.return_value = {
            "status": "completed", "stdout": "Calling tool", "exit_code": 0,
            "notes": [], "command": [], "stderr": "",
            "tool_calls": [{"id": "t1", "name": "get_weather", "input": {"location": "Saigon"}}],
        }
        result = bridge_request({"text": "Hi", "model": "claude-sonnet-4-20250514"})
        self.assertEqual(result["tool_calls"][0]["name"], "get_weather")


class TestAdapterEndToEndAgentic(unittest.TestCase):
    """End-to-end: adapter receives agentic params, produces correct result."""

    @patch("adapters.cloud.anthropic_adapter.urlopen")
    def test_anthropic_tool_use_full_flow(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "content": [
                {"type": "text", "text": "Let me check."},
                {"type": "tool_use", "id": "toolu_xyz", "name": "get_weather",
                 "input": {"location": "Saigon"}},
            ],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 50, "output_tokens": 30},
            "stop_reason": "tool_use",
        })
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = execute_anthropic({
                "model": "claude-sonnet-4-20250514",
                "prompt": "What's the weather in Saigon?",
                "tools": [SAMPLE_TOOL_ANTHROPIC],
            })
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "get_weather")
        self.assertEqual(result["manifest"]["stop_reason"], "tool_use")

    @patch("adapters.cloud.openai_adapter.urlopen")
    def test_openai_json_mode_full_flow(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "choices": [{"message": {"content": '{"answer": "ok"}'}, "finish_reason": "stop"}],
            "model": "gpt-4o",
            "usage": {"prompt_tokens": 20, "completion_tokens": 10},
        })
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = execute_openai({
                "model": "gpt-4o",
                "prompt": "Give me a JSON object",
                "json_mode": True,
            })
        self.assertEqual(result["status"], "success")
        # Verify the request had response_format set
        sent_body = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
        self.assertEqual(sent_body["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()
