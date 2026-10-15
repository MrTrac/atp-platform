"""KD-ATP-022: a missing or unrunnable `aios-gate` must degrade the governance verdict, never destroy the request's result.

`run_governance_review` shells out to `~/AI_OS/30_RUNTIME/bin/aios-gate` after EVERY successful `POST /run`. It handled three failures (non-zero exit, timeout, unparseable output) and
let two others escape: `FileNotFoundError` (the file is not there) and `PermissionError` (it is not executable). `BridgeHandler.do_POST`'s catch-all turned either into HTTP 500
`Bridge execution failed: [Errno 2] ...` AFTER the provider had already done its work, so the caller lost a real result. Measured 15/10/2026 on aios-server, which has no AI_OS tree and no
`aios-gate`: a status call through ATP reached aios-flow (404, authenticated) and ATP still answered 500. For `provider=aios-flow` the work is a run started in aios-flow, so the 500 is
also an invitation to retry and start it twice.

CI hit the same wall once (500 "No such file ... aios-gate" on a runner without the file) and the test was patched around it instead of the hook; this file fixes the hook itself.

Every other failure of the gate already returns `{"governance_class": "E", "governance_status": "error", ...}` with HTTP 200; a gate that cannot be started is the same kind of failure.
"""

from __future__ import annotations

import glob
import http.client
import json
import os
import stat
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from bridge import governance_hook


def _script(directory: str, name: str, body: str, *, executable: bool = True) -> str:
    path = os.path.join(directory, name)
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, 0o755 if executable else 0o644)
    return path


class TestRunGovernanceReview(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _review(self, gate: str, request_id: str = "t-gate") -> dict:
        with patch.object(governance_hook, "AIOS_GATE", gate):
            return governance_hook.run_governance_review({"request_id": request_id})

    def _assert_error_verdict(self, verdict: dict) -> None:
        self.assertEqual(verdict["governance_status"], "error")
        self.assertEqual(verdict["governance_class"], "E")
        self.assertIs(verdict["requires_human"], False)

    def test_a_missing_gate_returns_an_error_verdict_instead_of_raising(self) -> None:
        gate = os.path.join(self.tmp.name, "no-such-dir", "aios-gate")
        verdict = self._review(gate)
        self._assert_error_verdict(verdict)
        self.assertIn("aios-gate unavailable", verdict["governance_reason"])
        self.assertIn(gate, verdict["governance_reason"], "the operator must be told WHICH path was looked up")

    def test_a_gate_that_is_not_executable_returns_an_error_verdict_instead_of_raising(self) -> None:
        gate = _script(self.tmp.name, "aios-gate", "#!/bin/sh\nexit 0\n", executable=False)
        self.assertFalse(os.stat(gate).st_mode & stat.S_IXUSR, "fixture must not be executable")
        verdict = self._review(gate)
        self._assert_error_verdict(verdict)
        self.assertIn("aios-gate unavailable", verdict["governance_reason"])

    def test_a_gate_that_cannot_be_started_does_not_leak_the_artifact_file(self) -> None:
        marker = "t-leak-check-kd-atp-016"
        before = set(glob.glob(os.path.join(tempfile.gettempdir(), f"aios_artifact_{marker}_*")))
        self._review(os.path.join(self.tmp.name, "missing"), request_id=marker)
        after = set(glob.glob(os.path.join(tempfile.gettempdir(), f"aios_artifact_{marker}_*")))
        self.assertEqual(after - before, set(), "the temp artifact must be removed even when the gate never ran")

    def test_a_gate_that_exits_non_zero_is_unchanged(self) -> None:
        gate = _script(self.tmp.name, "aios-gate", "#!/bin/sh\necho boom >&2\nexit 3\n")
        verdict = self._review(gate)
        self._assert_error_verdict(verdict)
        self.assertEqual(verdict["governance_reason"], "aios-gate failed: boom")

    def test_a_gate_that_prints_garbage_is_unchanged(self) -> None:
        gate = _script(self.tmp.name, "aios-gate", "#!/bin/sh\necho not-json\n")
        verdict = self._review(gate)
        self._assert_error_verdict(verdict)
        self.assertIn("Failed to parse aios-gate output", verdict["governance_reason"])

    def test_a_timeout_is_unchanged(self) -> None:
        with patch.object(governance_hook.subprocess, "run", side_effect=subprocess.TimeoutExpired("aios-gate", 10)):
            verdict = governance_hook.run_governance_review({"request_id": "t-timeout"})
        self._assert_error_verdict(verdict)
        self.assertEqual(verdict["governance_reason"], "aios-gate timed out")

    def test_a_working_gate_still_passes_its_verdict_through(self) -> None:
        reply = json.dumps({"governance_class": "B", "governance_status": "approved", "governance_reason": "ok", "requires_human": False})
        gate = _script(self.tmp.name, "aios-gate", f"#!/bin/sh\ncat <<'EOF'\n{reply}\nEOF\n")
        verdict = self._review(gate)
        self.assertEqual(verdict, {"governance_class": "B", "governance_status": "approved", "governance_reason": "ok", "requires_human": False})


class TestRunOverHttpWithoutAGate(unittest.TestCase):
    """The real BridgeHandler: the caller must get the provider's result, with the governance problem reported alongside it."""

    @classmethod
    def setUpClass(cls) -> None:
        import bridge.bridge_server as bs

        cls.tmp = tempfile.TemporaryDirectory()
        cls._allowlist = patch.object(bs, "MODEL_ALLOWLIST", [])
        cls._allowlist.start()
        cls._gate = patch.object(governance_hook, "AIOS_GATE", os.path.join(cls.tmp.name, "no-aios-gate-here"))
        cls._gate.start()
        cls.server = bs.ThreadedHTTPServer(("127.0.0.1", 0), bs.BridgeHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls._gate.stop()
        cls._allowlist.stop()
        cls.tmp.cleanup()

    def _post_run(self, body: dict) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            raw = json.dumps(body).encode("utf-8")
            conn.request("POST", "/run", body=raw, headers={"Content-Type": "application/json", "Content-Length": str(len(raw))})
            resp = conn.getresponse()
            return resp.status, json.loads(resp.read().decode("utf-8"))
        finally:
            conn.close()

    def test_the_providers_result_survives_a_missing_gate(self) -> None:
        import bridge.bridge_server as bs

        def provider_did_its_work(_incoming: dict, kind: str) -> dict:
            return {"status": "completed", "adapter": kind, "flow_run_id": "run-123"}

        with patch.object(bs, "_run_cli_agent_adapter", provider_did_its_work):
            status, payload = self._post_run({"adapter": "claude-code", "config": {}, "context": {}})
        self.assertEqual(status, 200, f"a missing gate turned a successful dispatch into HTTP {status}: {payload}")
        self.assertEqual(payload.get("status"), "completed")
        self.assertEqual(payload.get("flow_run_id"), "run-123", "the provider's own fields must reach the caller")
        self.assertEqual(payload["governance"]["governance_status"], "error")
        self.assertIn("aios-gate unavailable", payload["governance"]["governance_reason"])


if __name__ == "__main__":
    unittest.main()
