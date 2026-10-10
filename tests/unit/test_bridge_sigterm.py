"""SIGTERM must stop the bridge promptly (systemd restarts send SIGTERM first).

Regression: the handler called server.shutdown() on the thread that runs serve_forever(), which
deadlocked, so the process ignored SIGTERM until SIGKILL (90 s under systemd). This starts the real
server in a subprocess, because the failure only exists in a real process with a real signal.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(os.name == "posix", "SIGTERM semantics are POSIX")
class TestBridgeSigterm(unittest.TestCase):
    def test_sigterm_stops_the_server_promptly_with_exit_code_0(self) -> None:
        port = _free_port()
        with tempfile.TemporaryDirectory() as home:
            env = {**os.environ, "HOME": home, "ATP_BRIDGE_PORT": str(port)}
            proc = subprocess.Popen(
                [sys.executable, str(_ROOT / "bridge" / "bridge_server.py")],
                cwd=_ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                deadline = time.monotonic() + 15
                up = False
                while time.monotonic() < deadline and proc.poll() is None:
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                            up = r.status == 200
                            break
                    except OSError:
                        time.sleep(0.2)
                self.assertTrue(up, "bridge did not come up")

                started = time.monotonic()
                proc.send_signal(signal.SIGTERM)
                try:
                    rc = proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("bridge ignored SIGTERM for 5 s (shutdown deadlock)")
                self.assertEqual(rc, 0)
                self.assertLess(time.monotonic() - started, 5)
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()


if __name__ == "__main__":
    unittest.main()
