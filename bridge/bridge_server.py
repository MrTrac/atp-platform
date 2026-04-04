"""ATP Bridge HTTP Server — thin wrapper around openclaw_bridge.py.

Exposes the ATP bridge as an HTTP service for AIOS-OC integration.

Endpoints:
    POST /run    — accept JSON body, run bridge_request(), return result
    GET  /health — return {"status": "ok", "version": "1.0"}
    GET  /       — return {"status": "ok", "service": "ATP Bridge Server"}
    GET  *       — return 200 with {"status": "ok"} (never 404 for GET)

Usage:
    python3 bridge/bridge_server.py
    # or with custom port:
    ATP_BRIDGE_PORT=9000 python3 bridge/bridge_server.py
"""

from __future__ import annotations

import json
import os
import signal
import socket
import sys
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Ensure the ATP project root is on sys.path so we can import bridge modules
_bridge_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_bridge_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bridge.openclaw_bridge import bridge_request, BridgeError  # noqa: E402
from bridge.governance_hook import run_governance_review  # noqa: E402


ALLOWED_ORIGIN = os.environ.get("ATP_BRIDGE_CORS_ORIGIN", "http://localhost:3000")
DEFAULT_PORT = 8765
SERVER_VERSION = "1.0"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class BridgeHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for the ATP bridge."""

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, body: dict, extra_headers: dict | None = None) -> None:
        try:
            payload = json.dumps(body, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            if extra_headers:
                for key, value in extra_headers.items():
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)
        except BrokenPipeError:
            pass

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle CORS preflight."""
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "version": SERVER_VERSION})
        elif self.path == "/":
            self._send_json(200, {
                "status": "ok",
                "service": "ATP Bridge Server",
                "version": SERVER_VERSION,
            })
        else:
            # Return 200 for any GET — external probes must never see 404
            self._send_json(200, {"status": "ok"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/run":
            self._send_json(404, {"error": f"Not found: {self.path}"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"status": "failed", "error": "Empty request body"})
            return

        raw_body = self.rfile.read(content_length)

        try:
            incoming = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            self._send_json(400, {"status": "failed", "error": f"Invalid JSON: {exc}"})
            return

        self._log(f"POST /run — text={incoming.get('text', '')[:80]!r}")
        start = time.monotonic()

        try:
            result = bridge_request(incoming)
            elapsed_ms = round((time.monotonic() - start) * 1000)
            result["response_time_ms"] = elapsed_ms

            # Run AI_OS governance review on the artifact
            gov = run_governance_review(result)
            result["governance"] = gov

            # Set governance header for human-required artifacts
            extra_headers = {}
            if gov.get("requires_human"):
                extra_headers["X-Governance-Gate"] = "human-required"

            self._send_json(200, result, extra_headers=extra_headers)
        except BridgeError as exc:
            self._send_json(400, {"status": "failed", "error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"status": "failed", "error": f"Bridge execution failed: {exc}"})

    def _log(self, message: str) -> None:
        print(f"[{_timestamp()}] {message}", flush=True)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        """Override default logging to use our timestamp format."""
        if args:
            self._log(" ".join(str(a) for a in args))

    def log_error(self, format: str, *args) -> None:  # noqa: A002
        """Suppress noisy errors from probes and broken connections."""
        pass

    def handle_one_request(self) -> None:
        """Wrap request handling to catch connection resets from probes."""
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            pass


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle each request in a separate thread so LLM calls don't block."""
    daemon_threads = True


def main() -> None:
    port = int(os.environ.get("ATP_BRIDGE_PORT", DEFAULT_PORT))
    server = ThreadedHTTPServer(("0.0.0.0", port), BridgeHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.timeout = 120

    def _handle_sigterm(signum: int, frame: object) -> None:
        print(f"\n[{_timestamp()}] Received SIGTERM, shutting down.", flush=True)
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_sigterm)

    print(f"[{_timestamp()}] ATP Bridge Server starting on port {port}", flush=True)
    print(f"[{_timestamp()}] CORS allowed origin: {ALLOWED_ORIGIN}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{_timestamp()}] Shutting down.", flush=True)
    except Exception as exc:
        print(f"[{_timestamp()}] Server error: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
