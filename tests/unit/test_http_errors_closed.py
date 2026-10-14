"""Guard: an `HTTPError` that production code catches must have its open response closed (KD-ATP-012).

`urlopen` raises HTTPError for every non-2xx answer and the exception object IS the response: it owns the open socket / file. Nine `except HTTPError` blocks and six
`except (URLError, OSError, ...)` blocks (HTTPError is a URLError) caught it, read or ignored the body and moved on, leaving the close to the garbage collector. Measured 14/10/2026
with a probe over the whole suite: 15 HTTPError objects created, 0 closed by anyone; with `ResourceWarning` enabled that shows as `Implicitly cleaning up <HTTPError ...>` ×8. CPython frees
the object at once, so nothing ever failed — it is a hidden dependency on refcounting, not a crash.

Three layers, because each catches what the others cannot:
  * the helper itself (`core/http_errors.close_http_error`);
  * a static guard: every handler in a module that calls `urlopen` and can receive an HTTPError must call the helper on the exception it bound (new handlers cannot forget);
  * a behaviour test per call site: an HTTPError whose response is a tracked buffer is raised through the real code path and the buffer must be closed afterwards.
"""

from __future__ import annotations

import ast
import os
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from core.http_errors import close_http_error

_ROOT = Path(__file__).resolve().parents[2]
_SCAN_DIRS = ("adapters", "core", "bridge", "generators", "cli")
_NETWORK_MODULES_EXPECTED = {
    "adapters/aios_flow/aios_flow_adapter.py",
    "adapters/aokp/aokp_adapter.py",
    "adapters/cloud/anthropic_adapter.py",
    "adapters/cloud/openai_adapter.py",
    "adapters/cloud/openai_batch.py",
    "bridge/tdf_run.py",
    "core/evaluator.py",
}


def _error(code: int = 400) -> tuple[HTTPError, BytesIO]:
    """An HTTPError whose response is a buffer the test can inspect, with a JSON body like the real APIs send."""
    fp = BytesIO(b'{"error": {"message": "boom"}}')
    return HTTPError("http://x", code, "Err", {}, fp), fp


class TestCloseHttpError(unittest.TestCase):
    def test_closes_the_response_of_an_http_error(self) -> None:
        exc, fp = _error()
        close_http_error(exc)
        self.assertTrue(fp.closed)

    def test_status_and_text_stay_usable_after_the_close(self) -> None:
        """Handlers read what they need first, but str(exc), .code and .reason are used after the close in several of them."""
        exc, _fp = _error(502)
        close_http_error(exc)
        self.assertEqual((exc.code, exc.reason), (502, "Err"))
        self.assertIn("502", str(exc))

    def test_other_exceptions_and_none_are_left_alone(self) -> None:
        for other in (URLError("refused"), OSError("x"), ValueError("v"), None):
            close_http_error(other)  # must not raise

    def test_is_idempotent_and_never_raises(self) -> None:
        exc, _fp = _error()
        close_http_error(exc)
        close_http_error(exc)
        boom = MagicMock(spec=HTTPError)
        boom.close.side_effect = OSError("already gone")
        close_http_error(boom)  # an error while closing must not replace the error being handled


def _call_names(handler: ast.ExceptHandler) -> list[ast.Call]:
    return [n for n in ast.walk(handler) if isinstance(n, ast.Call)]


def _caught(handler: ast.ExceptHandler) -> set[str]:
    t = handler.type
    if t is None:
        return {"<bare>"}
    elts = t.elts if isinstance(t, ast.Tuple) else [t]
    return {e.attr if isinstance(e, ast.Attribute) else e.id for e in elts if isinstance(e, (ast.Attribute, ast.Name))}


def _calls_urlopen(tree: ast.AST) -> bool:
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Name) and f.id == "urlopen") or (isinstance(f, ast.Attribute) and f.attr == "urlopen"):
                return True
    return False


def _network_modules() -> dict[str, ast.AST]:
    mods = {}
    for d in _SCAN_DIRS:
        for p in sorted((_ROOT / d).rglob("*.py")):
            if p.name.startswith("test_") or "__pycache__" in p.parts:
                continue
            tree = ast.parse(p.read_text(encoding="utf-8"))
            if _calls_urlopen(tree):
                mods[str(p.relative_to(_ROOT))] = tree
    return mods


def _handlers_that_can_receive_an_http_error(tree: ast.AST) -> list[ast.ExceptHandler]:
    out = []
    for t in (n for n in ast.walk(tree) if isinstance(n, ast.Try)):
        for i, h in enumerate(t.handlers):
            if not ({"HTTPError", "URLError", "OSError"} & _caught(h)):
                continue
            if any("HTTPError" in _caught(e) for e in t.handlers[:i]):
                continue  # an earlier handler of the same try already takes every HTTPError
            out.append(h)
    return out


def _closes_its_exception(h: ast.ExceptHandler) -> bool:
    if not h.name:
        return False
    for c in _call_names(h):
        f = c.func
        if isinstance(f, ast.Name) and f.id == "close_http_error" and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == h.name:
            return True
        if isinstance(f, ast.Attribute) and f.attr == "close" and isinstance(f.value, ast.Name) and f.value.id == h.name:
            return True
    return False


class TestEveryHandlerClosesTheError(unittest.TestCase):
    def test_the_guard_sees_the_network_modules(self) -> None:
        """Guards the guard: if the scan finds fewer modules or handlers, the check below would pass vacuously."""
        mods = _network_modules()
        self.assertTrue(_NETWORK_MODULES_EXPECTED <= set(mods), sorted(_NETWORK_MODULES_EXPECTED - set(mods)))
        total = sum(len(_handlers_that_can_receive_an_http_error(t)) for t in mods.values())
        self.assertGreaterEqual(total, 14, "the 14 handlers known on 14/10/2026 were not all found")

    def test_every_handler_that_can_receive_an_http_error_closes_it(self) -> None:
        missing = []
        for rel, tree in _network_modules().items():
            for h in _handlers_that_can_receive_an_http_error(tree):
                if not _closes_its_exception(h):
                    missing.append(f"{rel}:{h.lineno} except {sorted(_caught(h))} as {h.name}")
        self.assertEqual(missing, [], "handlers that can receive an open HTTPError but never close it (call core.http_errors.close_http_error(<exc>))")


class TestEachCallSiteClosesTheResponse(unittest.TestCase):
    """Raise a tracked HTTPError through the real code path of each site; its response buffer must be closed afterwards."""

    def _check(self, label: str, target: str, call) -> None:
        exc, fp = _error(400)  # 400: not retried, so no backoff sleeps
        with patch(target, side_effect=exc):
            try:
                call()
            except Exception:  # noqa: BLE001 - tdf_run re-raises as its own error type; only the close matters here
                pass
        self.assertTrue(fp.closed, f"{label}: the HTTPError's response was left open")

    def test_anthropic_execute(self) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            self._check("anthropic execute", "adapters.cloud.anthropic_adapter.urlopen", lambda: execute_anthropic({"model": "m", "prompt": "p"}))

    def test_anthropic_stream(self) -> None:
        from adapters.cloud.anthropic_adapter import execute_anthropic_stream
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            self._check("anthropic stream", "adapters.cloud.anthropic_adapter.urlopen", lambda: list(execute_anthropic_stream({"model": "m", "prompt": "p"})))

    def test_openai_execute(self) -> None:
        from adapters.cloud.openai_adapter import execute_openai
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            self._check("openai execute", "adapters.cloud.openai_adapter.urlopen", lambda: execute_openai({"model": "gpt-4o", "prompt": "p"}))

    def test_openai_stream(self) -> None:
        from adapters.cloud.openai_adapter import execute_openai_stream
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            self._check("openai stream", "adapters.cloud.openai_adapter.urlopen", lambda: list(execute_openai_stream({"model": "gpt-4o", "prompt": "p"})))

    def test_openai_batch(self) -> None:
        from adapters.cloud.openai_batch import create_batch
        self._check("openai batch", "adapters.cloud.openai_batch.urlopen",
                    lambda: create_batch([{"custom_id": "r1", "body": {"model": "gpt-4o-mini"}}], api_key="sk-bad"))

    def test_evaluator_http_probe(self) -> None:
        from core.evaluator import _run_http_probe
        self._check("evaluator", "core.evaluator.urlopen", lambda: _run_http_probe({"url": "http://localhost/health"}))

    def test_aios_flow_dispatch_and_status(self) -> None:
        from adapters.aios_flow.aios_flow_adapter import _get_run_status, dispatch
        with patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
            self._check("aios-flow dispatch", "adapters.aios_flow.aios_flow_adapter.urlopen", lambda: dispatch({"pipeline": "flows/test.yml"}))
            self._check("aios-flow status", "adapters.aios_flow.aios_flow_adapter.urlopen", lambda: _get_run_status("run-1", record=False))

    def test_tdf_run_dispatch(self) -> None:
        from bridge.tdf_run import dispatch
        with patch("bridge.tdf_run.record_trace"):
            self._check("tdf-run", "bridge.tdf_run.urllib.request.urlopen", lambda: dispatch({"target": {"tool": "ops/checkos"}}))

    def test_aokp_every_query(self) -> None:
        """AOKP's handlers catch URLError, not HTTPError by name: the error arrives as a subclass and must still be closed."""
        from adapters.aokp import aokp_adapter as a
        calls = {
            "check_health": lambda: a.check_health(base_url="http://localhost:3002"),
            "query_knowledge": lambda: a.query_knowledge({"query": "q"}),
            "query_graph": lambda: a.query_graph({"term": "t"}),
            "query_chat": lambda: a.query_chat({"query": "q"}),
            "query_graph_rag": lambda: a.query_graph_rag({"query": "q"}),
            "query_temporal": lambda: a.query_temporal({"query": "q"}),
        }
        for name, call in calls.items():
            with self.subTest(site=name), patch("adapters.aokp.aokp_adapter.record_trace"):
                self._check(f"aokp {name}", "adapters.aokp.aokp_adapter.urlopen", call)


if __name__ == "__main__":
    unittest.main()
