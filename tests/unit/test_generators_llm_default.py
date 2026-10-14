"""Guard: the model generators/llm.py sends by default must resolve to a provider the executor can actually run.

The default used to be "ollama/qwen3:8b". bridge_request parsed it as provider "ollama", core.execution.executor.EXECUTOR_MAP has no such handler since the Ollama adapter
was removed in 2.6.0, so the call fell through to the deferred SSH stub (status "deferred", empty stdout) and every llm_mode=real call without an explicit model raised
LlmError. Measured 14/10/2026 by calling invoke_executor directly; nothing was launched, which is also why this went unnoticed: the failure was silent until someone
used real mode. macOS hosts must not run Ollama or any local LLM (Global_Mac_No_Ollama_Rule), so a default that names it is wrong twice.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from bridge.openclaw_bridge import _parse_model_spec
from core.execution.executor import EXECUTOR_MAP
from generators import llm

_ROOT = Path(__file__).resolve().parents[2]
_OVERRIDE = "ATP_GENERATORS_DEFAULT_MODEL"


def _default_model_in_fresh_interpreter() -> str:
    """DEFAULT_MODEL is computed at import time, so read it in a clean interpreter with the override variable removed."""
    env = {k: v for k, v in os.environ.items() if k != _OVERRIDE}
    code = f"import sys; sys.path.insert(0, {str(_ROOT)!r}); from generators import llm; print(llm.DEFAULT_MODEL)"
    r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, env=env, cwd=_ROOT, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class TestGeneratorsDefaultModel(unittest.TestCase):
    def test_default_resolves_to_a_provider_with_an_executor_handler(self) -> None:
        default = _default_model_in_fresh_interpreter()
        provider, _model = _parse_model_spec(default)
        self.assertIn(provider, EXECUTOR_MAP, f"default model {default!r} resolves to provider {provider!r}, which has no executor handler")

    def test_default_does_not_name_a_local_llm(self) -> None:
        default = _default_model_in_fresh_interpreter().lower()
        for local in ("ollama", "llama", "qwen", "gemma", "mlx"):
            self.assertNotIn(local, default, f"default model {default!r} names a local LLM (forbidden on macOS)")

    def test_call_without_model_sends_the_default_and_it_is_runnable(self) -> None:
        if os.environ.get(_OVERRIDE):
            self.skipTest(f"{_OVERRIDE} is set in this environment")
        seen: dict = {}

        def fake_bridge_request(incoming: dict) -> dict:
            seen.update(incoming)
            return {"status": "succeeded", "stdout": "ok"}

        with mock.patch("bridge.openclaw_bridge.bridge_request", fake_bridge_request):
            self.assertEqual(llm._default_provider("prompt"), "ok")

        self.assertEqual(seen["model"], llm.DEFAULT_MODEL)
        provider, _model = _parse_model_spec(seen["model"])
        self.assertIn(provider, EXECUTOR_MAP)


if __name__ == "__main__":
    unittest.main()
