"""KD-ATP-015: an unknown provider on the local node is a client error everywhere it can surface, never a silent `deferred`.

Until 14/10/2026 `invoke_executor` answered `status=deferred` (HTTP 200, empty stdout) for any provider without a handler, because it treated every unknown provider as "remote". On the only registered
node, `local_mac`, that is nonsense — and it hid KD-ATP-010 (generators defaulting to the removed `ollama/qwen3:8b`) from 2.6.0 to 14/10/2026. Now: `UnsupportedProviderError` in the executor,
`BridgeError` in `bridge_request`, HTTP 400 `{"status": "failed", "error": ...}` on `POST /run`, and `LlmError` for generators. An explicit remote node still gets `deferred`
(tests/unit/test_registry_driven_dispatch.py). Nothing here reaches a provider: the error is raised before any adapter runs, so no network call is made.
"""

from __future__ import annotations

import http.client
import json
import threading
import unittest
from unittest.mock import patch

from bridge.openclaw_bridge import BridgeError, _parse_model_spec, bridge_request
from core.execution.executor import EXECUTOR_MAP
from generators import llm


class TestBridgeRequest(unittest.TestCase):
    def test_removed_provider_prefix_raises_a_bridge_error_naming_it(self) -> None:
        with self.assertRaises(BridgeError) as cm:
            bridge_request({"text": "hi", "model": "ollama/qwen3:8b"})
        msg = str(cm.exception)
        self.assertIn("Unsupported provider 'ollama'", msg)
        self.assertIn("ollama/qwen3:8b", msg, "the caller's own model spec is echoed back so the typo is easy to spot")
        self.assertIn("anthropic", msg, "and the supported providers are listed")

    def test_a_typo_in_the_prefix_is_rejected_the_same_way(self) -> None:
        with self.assertRaises(BridgeError) as cm:
            bridge_request({"text": "hi", "model": "anthropc/claude-haiku-4-5-20251001"})
        self.assertIn("Unsupported provider 'anthropc'", str(cm.exception))


class TestGeneratorsDefaultProvider(unittest.TestCase):
    def test_an_explicit_unsupported_model_surfaces_as_llm_error_not_empty_text(self) -> None:
        """The generators call goes through bridge_request; before the fix this returned status=deferred and the LlmError said only 'status=deferred'."""
        with self.assertRaises(llm.LlmError) as cm:
            llm._default_provider("prompt", model="ollama/qwen3:8b")
        self.assertIn("Unsupported provider 'ollama'", str(cm.exception))


class TestEveryModelTheOnlyConsumerSendsStillResolves(unittest.TestCase):
    """Survey of 14/10/2026 (9 ecosystem repos, read-only; independently re-checked): the only repo that talks to ATP is AIOS-OC, through POST /run. These are the `model` values it can send (RequestView,
    AgentStoreProvider, AgentCreateDialog, NodeConfigForms, FlowGenDialog, AtpLiveSurface, hub-query, flow-generate, e2e contract). The change must never reject legitimate traffic: each one has to resolve
    to a provider that has an executor. A bare `claude-*` name is the easy one to break (it carries no `provider/` prefix), and it is the default of the chat view."""

    AIOS_OC_MODELS = (
        "claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5", "claude-haiku-4-5-20251001",
        "anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-5-20250929", "anthropic/claude-opus-4-5-20251101",
        "openai/gpt-5.2", "openai/gpt-5-pro", "openai/gpt-5-mini", "openai/gpt-4o",
    )

    def test_each_model_aios_oc_sends_resolves_to_a_provider_with_an_executor(self) -> None:
        for model in self.AIOS_OC_MODELS:
            with self.subTest(model=model):
                provider, _name = _parse_model_spec(model)
                self.assertIn(provider, EXECUTOR_MAP, f"{model!r} would now be rejected as an unsupported provider")

    def test_a_bare_name_without_a_prefix_still_defaults_to_anthropic(self) -> None:
        """Unchanged by KD-ATP-015 (2.6.0: 'unprefixed/unknown models default to anthropic'): only an EXPLICIT unknown `provider/` prefix is rejected."""
        self.assertEqual(_parse_model_spec("qwen3:8b")[0], "anthropic")
        self.assertEqual(_parse_model_spec("")[0], "anthropic")


class TestRunOverHttp(unittest.TestCase):
    """The real BridgeHandler on an ephemeral port, in a thread: what a client actually sees."""

    @classmethod
    def setUpClass(cls) -> None:
        import bridge.bridge_server as bs

        cls._allowlist = patch.object(bs, "MODEL_ALLOWLIST", [])  # deterministic whatever the environment configures
        cls._allowlist.start()
        cls.server = bs.ThreadedHTTPServer(("127.0.0.1", 0), bs.BridgeHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls._allowlist.stop()

    def _post_run(self, body: dict) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            raw = json.dumps(body).encode("utf-8")
            conn.request("POST", "/run", body=raw, headers={"Content-Type": "application/json", "Content-Length": str(len(raw))})
            resp = conn.getresponse()
            return resp.status, json.loads(resp.read().decode("utf-8"))
        finally:
            conn.close()

    def test_unsupported_provider_is_http_400_failed_not_200_deferred(self) -> None:
        status, payload = self._post_run({"text": "hi", "model": "ollama/qwen3:8b"})
        self.assertEqual(status, 400, payload)
        self.assertEqual(payload.get("status"), "failed")
        self.assertIn("Unsupported provider 'ollama'", payload.get("error", ""))
        self.assertNotEqual(payload.get("status"), "deferred")

    def test_the_400_carries_the_cors_header_like_a_200(self) -> None:
        """AtpLiveSurface in AIOS-OC calls the bridge straight from the browser: without CORS headers a 400 would surface as 'Failed to fetch' and the JSON error would be lost."""
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            raw = json.dumps({"text": "hi", "model": "ollama/qwen3:8b"}).encode("utf-8")
            conn.request("POST", "/run", body=raw, headers={"Content-Type": "application/json", "Content-Length": str(len(raw)), "Origin": "http://127.0.0.1:3000"})
            resp = conn.getresponse()
            resp.read()
            status, cors = resp.status, resp.getheader("Access-Control-Allow-Origin")
        finally:
            conn.close()
        self.assertEqual(status, 400)
        self.assertIsNotNone(cors, "the 400 has no Access-Control-Allow-Origin header")

    def test_an_adapter_request_is_dispatched_before_any_provider_check(self) -> None:
        """AIOS-OC agent nodes POST {adapter, config, context} with NO top-level model. They must reach the adapter dispatcher, never the provider check that rejects unknown providers."""
        import bridge.bridge_server as bs

        seen = {}

        def fake_agent_adapter(incoming: dict, kind: str) -> dict:
            seen["kind"] = kind
            return {"status": "completed", "adapter": kind}

        def fake_governance(_artifact: dict) -> dict:
            # After ANY successful dispatch /run shells out to ~/AI_OS/30_RUNTIME/bin/aios-gate (bridge/governance_hook.py). That file exists on the developer's Mac and not on the CI
            # runner, so leaving it real made this test pass locally and fail in CI (first push of KD-ATP-015: 500 "No such file ... aios-gate" on 3.11 and 3.12). This test is about
            # dispatch order, not governance: stub the review.
            return {"governance_class": "C", "governance_status": "approved", "governance_reason": "stubbed in test", "requires_human": False}

        with patch.object(bs, "_run_cli_agent_adapter", fake_agent_adapter), patch.object(bs, "run_governance_review", fake_governance):
            status, payload = self._post_run({"adapter": "claude-code", "config": {"model": "sonnet"}, "context": {}})
        self.assertEqual((status, payload.get("status")), (200, "completed"), payload)
        self.assertEqual(seen, {"kind": "claude-code"})

    def test_the_server_keeps_serving_after_the_rejection(self) -> None:
        self._post_run({"text": "hi", "model": "ollama/qwen3:8b"})
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request("GET", "/health")
            resp = conn.getresponse()
            body = json.loads(resp.read().decode("utf-8"))
        finally:
            conn.close()
        self.assertEqual((resp.status, body.get("status")), (200, "ok"))


if __name__ == "__main__":
    unittest.main()
