"""ATP Bridge HTTP Server — thin wrapper around openclaw_bridge.py.

Exposes the ATP bridge as an HTTP service for AIOS-OC integration.

Endpoints:
    POST /run    — accept JSON body, run bridge_request(), return result
    GET  /health — return {"status": "ok", "version": "1.0"}

Usage:
    python3 bridge/bridge_server.py
    # or with custom port:
    ATP_BRIDGE_PORT=9000 python3 bridge/bridge_server.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure the ATP project root is on sys.path so we can import bridge modules
_bridge_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_bridge_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bridge.openclaw_bridge import bridge_request, BridgeError  # noqa: E402


ALLOWED_ORIGIN = os.environ.get("ATP_BRIDGE_CORS_ORIGIN", "http://localhost:3000")
DEFAULT_PORT = 8765


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class BridgeHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for the ATP bridge."""

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle CORS preflight."""
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._log("GET /health")
            self._send_json(200, {"status": "ok", "version": "1.0"})
        else:
            self._send_json(404, {"error": f"Not found: {self.path}"})

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
            self._send_json(200, result)
        except BridgeError as exc:
            self._send_json(400, {"status": "failed", "error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"status": "failed", "error": f"Bridge execution failed: {exc}"})

    def _log(self, message: str) -> None:
        print(f"[{_timestamp()}] {message}", flush=True)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        """Override default logging to use our timestamp format."""
        self._log(f"{args[0]} {args[1]} {args[2]}")


def main() -> None:
    port = int(os.environ.get("ATP_BRIDGE_PORT", DEFAULT_PORT))
    server = HTTPServer(("0.0.0.0", port), BridgeHandler)
    print(f"[{_timestamp()}] ATP Bridge Server starting on port {port}")
    print(f"[{_timestamp()}] CORS allowed origin: {ALLOWED_ORIGIN}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{_timestamp()}] Shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
