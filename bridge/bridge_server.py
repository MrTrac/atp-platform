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
from pathlib import Path
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
from bridge.run_persistence import persist_bridge_run, list_runs, get_run  # noqa: E402
from core.routing.route_prepare import _discover_active_providers, _discover_active_nodes  # noqa: E402


ALLOWED_ORIGIN = os.environ.get("ATP_BRIDGE_CORS_ORIGIN", "http://localhost:3000")
DEFAULT_PORT = 8765
SERVER_VERSION = "1.0"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _build_status_response() -> dict:
    """Build full ATP status for the /status endpoint."""
    providers = _discover_active_providers()
    nodes = _discover_active_nodes()
    aokp_status = "disabled"
    aokp_enabled = os.environ.get("ATP_AOKP_ENABLED", "").lower() in ("1", "true", "yes")
    if aokp_enabled:
        try:
            from adapters.aokp.aokp_adapter import check_health
            health = check_health(timeout=3)
            aokp_status = health.get("status", "unknown")
        except Exception:
            aokp_status = "error"

    return {
        "status": "ok",
        "version": SERVER_VERSION,
        "providers": [p.get("provider") for p in providers],
        "provider_count": len(providers),
        "nodes": [n.get("node") for n in nodes],
        "aokp": {"enabled": aokp_enabled, "status": aokp_status},
        "timestamp": _timestamp(),
    }


def _build_providers_response() -> dict:
    """Build provider list for the /providers endpoint."""
    providers = _discover_active_providers()
    return {
        "providers": [
            {
                "provider": p.get("provider"),
                "provider_type": p.get("provider_type"),
                "status": p.get("status"),
                "capabilities": p.get("supported_capabilities", []),
                "cost_profile": p.get("cost_profile"),
            }
            for p in providers
        ],
        "count": len(providers),
    }


def _build_capabilities_response() -> dict:
    """Build capability list for the /capabilities endpoint."""
    from core.intake.loader import load_request
    cap_dir = Path(_project_root) / "registry" / "capabilities"
    capabilities = []
    if cap_dir.is_dir():
        for f in sorted(cap_dir.glob("*.yaml")):
            try:
                entry = load_request(f)
                capabilities.append({
                    "capability": entry.get("capability"),
                    "category": entry.get("category"),
                    "description": entry.get("description", ""),
                })
            except Exception:
                continue
    return {"capabilities": capabilities, "count": len(capabilities)}


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
        elif self.path == "/status":
            self._send_json(200, _build_status_response())
        elif self.path == "/providers":
            self._send_json(200, _build_providers_response())
        elif self.path == "/capabilities":
            self._send_json(200, _build_capabilities_response())
        elif self.path == "/runs":
            self._send_json(200, {"runs": list_runs(), "count": len(list_runs())})
        elif self.path.startswith("/runs/"):
            run_id = self.path[len("/runs/"):]
            run_data = get_run(run_id) if run_id else None
            if run_data:
                self._send_json(200, run_data)
            else:
                self._send_json(404, {"error": f"Run not found: {run_id}"})
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

            # Optional run persistence
            persistence = persist_bridge_run(
                request_id=result.get("request_id", "unknown"),
                normalized_request={"request_id": result.get("request_id"), "payload": incoming},
                routing_result={"selected_provider": result.get("selected_provider"), "selected_node": result.get("selected_node")},
                raw_result=result,
                normalized_output=result,
            )
            if persistence.get("persisted"):
                result["persistence"] = {"run_id": persistence["run_id"], "files": len(persistence.get("files_written", []))}

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
