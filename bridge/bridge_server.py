"""ATP Bridge HTTP Server — thin wrapper around openclaw_bridge.py.

Exposes the ATP bridge as an HTTP service for AIOS-OC integration.

Endpoints:
    POST /run                         — execute task via bridge (blocking)
    POST /run/stream                  — execute task with SSE streaming (v2.0.0)
    POST /api/synthesis/generate      — run a registered generator (D5.x phase 1)
    GET  /api/synthesis/generators    — list registered generators (D4.3)
    GET  /health                      — basic health check
    GET  /status                      — full ATP status (providers, nodes, AOKP, config)
    GET  /providers                   — active provider list from registry
    GET  /capabilities                — active capability list from registry
    GET  /runs                        — list persisted run history
    GET  /runs/active                 — list in-flight requests (v2.0.0)
    GET  /runs/<id>                   — detail for a specific run
    DELETE /runs/<id>                 — cancel an in-flight request (v2.0.0)
    GET  /                            — service info
    OPTIONS *                         — CORS preflight

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

from bridge.openclaw_bridge import bridge_request, BridgeError, _parse_model_spec  # noqa: E402
from bridge.governance_hook import run_governance_review  # noqa: E402
from bridge.run_persistence import persist_bridge_run, list_runs, get_run  # noqa: E402
from bridge.context_enrichment import enrich_context  # noqa: E402
from core.routing.route_prepare import _discover_active_providers, _discover_active_nodes  # noqa: E402
from core import config  # noqa: E402
from core import in_flight_tracker  # noqa: E402

# D4.3 + D5.x — synthesis generator surface (Z2 contract: ATP_AIOS-OC_v3).
import generators as _generators  # noqa: E402  (eager-imports the registry stubs)
from core import streaming as sse  # noqa: E402
from core.structured_log import log_event  # noqa: E402


ALLOWED_ORIGIN = config.BRIDGE_CORS_ORIGIN
DEFAULT_PORT = config.BRIDGE_PORT
MAX_BODY_BYTES = config.BRIDGE_MAX_BODY_BYTES
MODEL_ALLOWLIST = config.MODEL_ALLOWLIST
SERVER_VERSION = "1.7"


# ─── D4.3 + D5.x synthesis surface helpers ─────────────────────────────────

def _descriptor_to_dict(d: "_generators.GeneratorDescriptor") -> dict:
    return {
        "name": d.name,
        "version": d.version,
        "lifecycle": d.lifecycle,
        "description": d.description,
        "source_aokp_module": d.source_aokp_module,
        "params_schema": d.params_schema,
    }


def _citation_to_dict(c: "_generators.Citation") -> dict:
    return {
        "artifact_id": c.artifact_id,
        "source_id": c.source_id,
        "snippet": c.snippet,
        "classification_path": list(c.classification_path),
        "relevance_score": c.relevance_score,
        "rank": c.rank,
    }


def _synthesis_result_to_dict(r: "_generators.SynthesisResult") -> dict:
    return {
        "run_id": r.run_id,
        "generator": r.generator,
        "status": r.status,
        "answer": r.answer,
        "citations": [_citation_to_dict(c) for c in r.citations],
        "usage": r.usage,
        "diagnostics": r.diagnostics,
    }


def _build_synthesis_generators_response() -> dict:
    return {
        "registry_version": _generators.registry_version(),
        "generators": [_descriptor_to_dict(d) for d in _generators.list_generators()],
    }


def _handle_synthesis_generate(body: dict) -> tuple[int, dict]:
    """Pure-function dispatch for /api/synthesis/generate.

    Returns (http_status, json_body). Kept side-effect-free so it's easy
    to unit-test without spinning up the HTTP server.
    """
    name = str(body.get("generator", "")).strip()
    if not name:
        return 400, {"ok": False, "error": "missing_generator", "field": "generator"}

    entry = _generators.get_generator(name)
    if entry is None:
        available = sorted(d.name for d in _generators.list_generators())
        return 404, {
            "ok": False,
            "error": "generator_not_found",
            "requested": name,
            "available": available,
        }

    request_id = str(body.get("request_id", "") or "")
    consumer = str(body.get("consumer", "internal") or "internal")
    params = body.get("params") or {}
    if not isinstance(params, dict):
        return 400, {"ok": False, "error": "params_not_object"}

    req = _generators.GeneratorRequest(
        request_id=request_id,
        payload=params,
        consumer=consumer,
    )
    try:
        result = entry.handler(req)
    except NotImplementedError as e:
        return 501, {
            "ok": False,
            "error": "not_implemented",
            "generator": name,
            "message": str(e),
        }
    except Exception as e:  # pragma: no cover  (defensive)
        return 500, {"ok": False, "error": "generator_exception", "message": str(e)}

    payload = _synthesis_result_to_dict(result)
    payload["ok"] = True
    return 200, payload


def _run_cli_agent_adapter(incoming: dict, adapter_kind: str) -> dict:
    """Dispatch `adapter=claude-code|codex|cursor` requests to the matching
    Python adapter (all 3 share identical config shape; only the spawned
    CLI differs). Returns the normalized bridge response.
    """
    import asyncio
    import uuid

    cfg = incoming.get("config") or {}
    repo = str(cfg.get("repo") or "")
    template = str(cfg.get("template") or "")
    model_raw = str(cfg.get("model") or "")
    branch = cfg.get("branch") or None
    scope = cfg.get("scope") or None
    timeout_seconds = int(cfg.get("timeout_seconds") or 7200)
    # Optional workspace — caller passes an absolute stage dir; adapter writes
    # prompt.md / stdout.log / stderr.log / result.json there, keeping the
    # source repo clean. `isolation` picks direct|read-only|worktree for cwd.
    workspace_dir = cfg.get("workspace_dir") or None
    isolation = str(cfg.get("isolation") or "direct")

    if not repo or not template:
        return {"status": "failed", "error": f"{adapter_kind} adapter: repo and template are required", "success": False}

    if adapter_kind == "claude-code":
        from adapters.claude_code import ClaudeCodeAdapter, ClaudeCodeAdapterConfig
        adapter_cfg = ClaudeCodeAdapterConfig(
            repo=repo, template=template,
            model=model_raw or "sonnet",
            timeout_seconds=timeout_seconds, branch=branch, scope=scope,
            workspace_dir=workspace_dir, isolation=isolation,
        )
        adapter = ClaudeCodeAdapter(adapter_cfg)
        rid_prefix = "cc"
    elif adapter_kind == "codex":
        from adapters.codex import CodexAdapter, CodexAdapterConfig
        adapter_cfg = CodexAdapterConfig(
            repo=repo, template=template,
            model=model_raw or "gpt-5-pro",
            timeout_seconds=timeout_seconds, branch=branch, scope=scope,
            workspace_dir=workspace_dir, isolation=isolation,
        )
        adapter = CodexAdapter(adapter_cfg)
        rid_prefix = "cx"
    elif adapter_kind == "cursor":
        from adapters.cursor import CursorAdapter, CursorAdapterConfig
        adapter_cfg = CursorAdapterConfig(
            repo=repo, template=template,
            model=model_raw or "auto",
            timeout_seconds=timeout_seconds, branch=branch, scope=scope,
            workspace_dir=workspace_dir, isolation=isolation,
        )
        adapter = CursorAdapter(adapter_cfg)
        rid_prefix = "cu"
    else:
        return {"status": "failed", "error": f"unknown CLI-agent adapter: {adapter_kind}", "success": False}

    context = incoming.get("context") or {}
    result = asyncio.run(adapter.execute(prompt_context=context))
    request_id = f"{rid_prefix}-{uuid.uuid4().hex[:12]}"
    return {
        "status": "ok" if result.success else "failed",
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "error": result.error,
        "request_id": request_id,
        "adapter": adapter_kind,
        "repo": repo,
        "model": adapter_cfg.model_id,
        "workspace_dir": workspace_dir,
        "isolation": isolation,
        "bridge": {"source": f"{adapter_kind}-adapter"},
    }


def _run_claude_code_adapter(incoming: dict) -> dict:
    """Back-compat shim — delegate to the unified CLI-agent dispatcher."""
    return _run_cli_agent_adapter(incoming, "claude-code")


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _build_status_response() -> dict:
    """Build full ATP status for the /status endpoint."""
    providers = _discover_active_providers()
    nodes = _discover_active_nodes()
    aokp_status = "disabled"
    aokp_enabled = config.AOKP_ENABLED
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
        "config": config.summary(),
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
        elif self.path == "/runs/active":
            active = in_flight_tracker.list_active()
            self._send_json(200, {"active": active, "count": len(active)})
        elif self.path == "/api/synthesis/generators":
            self._send_json(200, _build_synthesis_generators_response())
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

    def do_DELETE(self) -> None:  # noqa: N802
        """Cancel an in-flight request (v2.0.0)."""
        if self.path.startswith("/runs/"):
            run_id = self.path[len("/runs/"):]
            if not run_id:
                self._send_json(400, {"error": "Missing run_id"})
                return
            cancelled = in_flight_tracker.cancel(run_id)
            if cancelled:
                log_event("bridge.cancel", request_id=run_id, status="cancelled")
                self._send_json(200, {"request_id": run_id, "cancelled": True})
            else:
                self._send_json(404, {"request_id": run_id, "cancelled": False, "error": "Not active"})
        else:
            self._send_json(404, {"error": f"Not found: {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/run/stream":
            self._handle_stream()
            return
        if self.path == "/api/synthesis/generate":
            self._handle_synthesis_generate()
            return
        if self.path != "/run":
            self._send_json(404, {"error": f"Not found: {self.path}"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"status": "failed", "error": "Empty request body"})
            return

        # Security: reject oversized payloads
        if content_length > MAX_BODY_BYTES:
            self._send_json(413, {"status": "failed", "error": f"Request body too large ({content_length} bytes, max {MAX_BODY_BYTES})"})
            return

        raw_body = self.rfile.read(content_length)

        try:
            incoming = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            self._send_json(400, {"status": "failed", "error": f"Invalid JSON: {exc}"})
            return

        # Security: validate model against allowlist if configured
        if MODEL_ALLOWLIST and incoming.get("model"):
            model_spec = incoming["model"]
            model_name = model_spec.split("/")[-1] if "/" in model_spec else model_spec
            if model_name not in MODEL_ALLOWLIST:
                self._send_json(403, {"status": "failed", "error": f"Model not in allowlist: {model_name}", "allowed": MODEL_ALLOWLIST})
                return

        self._log(f"POST /run — adapter={incoming.get('adapter', '')!r} text={incoming.get('text', '')[:80]!r}")
        start = time.monotonic()

        try:
            adapter_kind = incoming.get("adapter")
            if adapter_kind in ("claude-code", "codex", "cursor"):
                result = _run_cli_agent_adapter(incoming, adapter_kind)
            elif adapter_kind == "openai-batch":
                from adapters.cloud.openai_batch import dispatch as _batch_dispatch
                result = _batch_dispatch(incoming)
            else:
                result = bridge_request(incoming)
            elapsed_ms = round((time.monotonic() - start) * 1000)
            result["response_time_ms"] = elapsed_ms

            # Ensure top-level 'error' field for failed requests (AIOS-OC reads this)
            if result.get("status") == "failed" and not result.get("error"):
                result["error"] = result.get("stderr") or "Execution failed (no details)."

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
            else:
                # Surface the reason so `persistence: null` doesn't silently
                # hide real errors ("persistence error: ..." from the caught
                # exception inside persist_bridge_run).
                reason = persistence.get("reason")
                if reason and reason != "disabled":
                    result["persistence"] = {"persisted": False, "reason": reason}
                    log_event("bridge.persist.error", request_id=result.get("request_id"), reason=reason)

            # Structured logging
            manifest = result.get("ollama_manifest") or result.get("manifest") or {}
            log_event(
                "bridge.request",
                request_id=result.get("request_id"),
                provider=result.get("selected_provider"),
                model=result.get("bridge", {}).get("resolved_model"),
                duration_ms=elapsed_ms,
                status=result.get("status"),
                tokens=manifest.get("token_count"),
                cost_usd=manifest.get("cost_usd"),
                error_code=result.get("error_classification", {}).get("code") if result.get("error_classification") else None,
            )

            self._send_json(200, result, extra_headers=extra_headers)
        except BridgeError as exc:
            log_event("bridge.error", error=str(exc), error_code="contract_violation")
            self._send_json(400, {"status": "failed", "error": str(exc)})
        except Exception as exc:
            log_event("bridge.error", error=str(exc), error_code="unknown_error")
            self._send_json(500, {"status": "failed", "error": f"Bridge execution failed: {exc}"})

    def _handle_synthesis_generate(self) -> None:
        """POST /api/synthesis/generate — D5.x phase 1 (registry dispatch).

        Body shape (per ATP_AIOS-OC_v3.yaml SynthesisRequest):
            {
              "generator": "report" | "analyze" | "transform" | ...,
              "params":    { ... generator-specific ... },
              "consumer":  "AIOS-OC" | "ATCC_HCM" | "internal",
              "request_id": "<optional idempotency key>"
            }

        Phase 1 dispatches to the in-process generators registry.
        Generators that haven't ported yet (federation/temporal/react/
        tot/graphrag_synth) raise NotImplementedError → 501. Generators
        that have ported but only in skeletal form return status=partial
        with diagnostics flagging the LLM branch as pending.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"ok": False, "error": "empty_body"})
            return
        if content_length > MAX_BODY_BYTES:
            self._send_json(
                413,
                {"ok": False, "error": f"body_too_large", "max_bytes": MAX_BODY_BYTES},
            )
            return
        try:
            body = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        if not isinstance(body, dict):
            self._send_json(400, {"ok": False, "error": "body_not_object"})
            return

        status, payload = _handle_synthesis_generate(body)
        log_event(
            "bridge.synthesis.generate",
            generator=str(body.get("generator", "")),
            consumer=str(body.get("consumer", "internal")),
            status=str(payload.get("status") or payload.get("error") or "ok"),
            http=status,
        )
        self._send_json(status, payload)

    def _handle_stream(self) -> None:
        """SSE streaming endpoint (v2.0.0) — POST /run/stream."""
        import uuid
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"status": "failed", "error": "Empty request body"})
            return
        if content_length > MAX_BODY_BYTES:
            self._send_json(413, {"status": "failed", "error": f"Request body too large ({content_length} > {MAX_BODY_BYTES})"})
            return

        raw_body = self.rfile.read(content_length)
        try:
            incoming = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            self._send_json(400, {"status": "failed", "error": f"Invalid JSON: {exc}"})
            return

        text = (incoming.get("text") or "").strip()
        if not text:
            self._send_json(400, {"status": "failed", "error": "'text' is required"})
            return

        # Security: model allowlist
        if MODEL_ALLOWLIST and incoming.get("model"):
            model_spec = incoming["model"]
            model_name = model_spec.split("/")[-1] if "/" in model_spec else model_spec
            if model_name not in MODEL_ALLOWLIST:
                self._send_json(403, {"status": "failed", "error": f"Model not in allowlist: {model_name}"})
                return

        provider, model = _parse_model_spec(incoming.get("model", ""))
        request_id = incoming.get("request_id") or f"stream-{uuid.uuid4().hex[:12]}"

        # Streaming providers (v2.2.0 added ollama)
        if provider not in ("anthropic", "openai", "ollama"):
            self._send_json(
                400,
                {
                    "status": "failed",
                    "error": f"Streaming not supported for provider '{provider}' (supported: anthropic, openai, ollama)",
                },
            )
            return

        # Send SSE headers
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")  # disable nginx buffering
            self._set_cors_headers()
            self.end_headers()
        except BrokenPipeError:
            return

        # Register in-flight and stream
        abort_event = in_flight_tracker.register(request_id, provider=provider, model=model)
        log_event("bridge.stream.start", request_id=request_id, provider=provider, model=model)

        # Optional AOKP enrichment (same pattern as bridge_request)
        enriched = enrich_context(incoming)
        aokp_ctx_text = ""
        if enriched.get("aokp_context"):
            aokp_ctx_text = enriched["aokp_context"].get("context_text", "")

        # Build adapter request
        adapter_req: dict = {
            "model": model,
            "prompt": text,
        }
        if incoming.get("context") or aokp_ctx_text:
            ctx_parts = []
            if incoming.get("context"):
                ctx_parts.append(str(incoming["context"]))
            if aokp_ctx_text:
                ctx_parts.append(f"--- Knowledge Context (AOKP) ---\n{aokp_ctx_text}")
            adapter_req["context"] = "\n\n".join(ctx_parts)
        if incoming.get("api_key"):
            adapter_req["api_key"] = incoming["api_key"]
        if incoming.get("options"):
            adapter_req["options"] = incoming["options"]
        if incoming.get("tools"):
            adapter_req["tools"] = incoming["tools"]
        if incoming.get("tool_choice"):
            adapter_req["tool_choice"] = incoming["tool_choice"]
        if incoming.get("json_mode"):
            adapter_req["json_mode"] = bool(incoming["json_mode"])

        # Select streaming function
        if provider == "anthropic":
            from adapters.cloud.anthropic_adapter import execute_anthropic_stream as stream_fn
        elif provider == "openai":
            from adapters.cloud.openai_adapter import execute_openai_stream as stream_fn
        else:
            from adapters.ollama.ollama_adapter import execute_ollama_stream as stream_fn

        final_manifest: dict = {}
        aborted = False
        try:
            # Send start event
            self.wfile.write(sse.format_start(request_id, provider, model))
            self.wfile.flush()

            for event_kind, data in stream_fn(adapter_req, abort_event=abort_event):
                if event_kind == "token":
                    self.wfile.write(sse.format_token(data["text"]))
                elif event_kind == "tool_call":
                    self.wfile.write(sse.format_tool_delta(data))
                elif event_kind == "manifest":
                    final_manifest = data.get("manifest", {})
                    self.wfile.write(sse.format_manifest(final_manifest))
                elif event_kind == "error":
                    self.wfile.write(sse.format_error(data.get("message", ""), data.get("error_code")))
                elif event_kind == "aborted":
                    aborted = True
                    self.wfile.write(sse.format_aborted(data.get("reason", "client_cancelled")))
                try:
                    self.wfile.flush()
                except BrokenPipeError:
                    # Client disconnected — treat as abort
                    abort_event.set()
                    aborted = True
                    break

            if not aborted:
                self.wfile.write(sse.format_done())
                try:
                    self.wfile.flush()
                except BrokenPipeError:
                    pass
        except BrokenPipeError:
            abort_event.set()
            aborted = True
        except Exception as exc:
            try:
                self.wfile.write(sse.format_error(f"Stream execution failed: {exc}"))
                self.wfile.flush()
            except BrokenPipeError:
                pass
            log_event("bridge.stream.error", request_id=request_id, error=str(exc))
        finally:
            in_flight_tracker.unregister(request_id)
            log_event(
                "bridge.stream.end",
                request_id=request_id,
                provider=provider,
                model=model,
                status="aborted" if aborted else "completed",
                tokens=final_manifest.get("token_count"),
                cost_usd=final_manifest.get("cost_usd"),
            )

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
    # Startup config validation
    warnings = config.validate()
    for w in warnings:
        log_event("config.warning", key=w.key, error=w.message)
    log_event("server.startup", **config.summary())

    port = config.BRIDGE_PORT
    server = ThreadedHTTPServer(("0.0.0.0", port), BridgeHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.timeout = 120

    def _handle_sigterm(signum: int, frame: object) -> None:
        log_event("server.shutdown", reason="SIGTERM")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_sigterm)

    print(f"[{_timestamp()}] ATP Bridge Server v{SERVER_VERSION} starting on port {port}", flush=True)
    print(f"[{_timestamp()}] CORS allowed origin: {ALLOWED_ORIGIN}", flush=True)
    if MODEL_ALLOWLIST:
        print(f"[{_timestamp()}] Model allowlist: {MODEL_ALLOWLIST}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_event("server.shutdown", reason="keyboard_interrupt")
        print(f"\n[{_timestamp()}] Shutting down.", flush=True)
    except Exception as exc:
        log_event("server.error", error=str(exc))
        print(f"[{_timestamp()}] Server error: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
