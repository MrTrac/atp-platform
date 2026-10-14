"""The aios-flow adapter's authentication over REAL sockets: real urllib, real HTTP parsing, a fake aios-flow and a fake aios-identity on 127.0.0.1.

The unit tests replace `urlopen`; these exist for what a replacement cannot show — that the header is on the wire, that urllib does not forward it when a server redirects,
that `Retry-After` arrives as a real header object, and that a server which accepts a connection and never answers is retried like any other network failure.
"""

from __future__ import annotations

import base64
import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from adapters.aios_flow import aios_flow_adapter as adapter

SECRET = "wire-test-secret-0123456789"


def _jwt(serial: int) -> str:
    def seg(obj) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")

    now = int(time.time())
    return f"{seg({'alg': 'EdDSA'})}.{seg({'sub': 'svc:atp', 'iat': now, 'exp': now + 3600, 'jti': serial})}.c2ln{serial}"


class _Site:
    """A throwaway HTTP server whose behaviour is a function of (handler, state)."""

    def __init__(self, behave) -> None:
        site = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_a) -> None:
                pass

            def _serve(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length)) if length else None
                site.requests.append({"method": self.command, "path": self.path, "headers": {k.lower(): v for k, v in self.headers.items()}, "body": body})
                behave(site, self, body)

            do_GET = do_POST = _serve

        self.requests: list[dict] = []
        self.state: dict = {}
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def reply(self, handler: BaseHTTPRequestHandler, code: int, body: dict | None = None, headers: dict | None = None) -> None:
        raw = json.dumps(body if body is not None else {}).encode()
        handler.send_response(code)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(raw)))
        for k, v in (headers or {}).items():
            handler.send_header(k, v)
        handler.end_headers()
        handler.wfile.write(raw)


def _identity_behaviour(site: _Site, h: BaseHTTPRequestHandler, body: dict | None) -> None:
    if h.path != "/identity/service-account/token" or h.command != "POST":
        return site.reply(h, 404, {"error": "not_found", "message": "no such route"})
    if not body or body.get("secret") != SECRET or body.get("username") != "svc:atp" or body.get("consumer") != "ATP":
        return site.reply(h, 401, {"error": "invalid_service_credentials", "message": "invalid credentials"})
    token = _jwt(len(site.requests))
    site.state.setdefault("issued", set()).add(token)
    # like identity 1.2.4: advertises a year, the JWT itself lives 3600 s
    return site.reply(h, 200, {"access_token": token, "expires_in": 31_536_000, "token_type": "Bearer", "session_id": "s"})


@pytest.fixture
def identity():
    site = _Site(_identity_behaviour)
    yield site
    site.close()


@pytest.fixture
def foreign():
    """Another host a misbehaving or compromised aios-flow might redirect to."""
    site = _Site(lambda s, h, b: s.reply(h, 200, {"id": "run-redir", "status": "running"}))
    yield site
    site.close()


@pytest.fixture
def flow(identity, foreign):
    def behave(site: _Site, h: BaseHTTPRequestHandler, body: dict | None) -> None:
        if h.path == "/api/redirect-me":
            return site.reply(h, 302, {}, {"Location": f"{foreign.url}/api/runs/run-redir"})
        auth = h.headers.get("Authorization", "")
        if not auth:
            return site.reply(h, 401, {"detail": {"error": "missing_token", "message": "Authorization Bearer header required"}})
        if auth.removeprefix("Bearer ") not in identity.state.get("issued", set()):
            return site.reply(h, 401, {"detail": {"error": "invalid_token", "message": "token failed verification"}})
        if h.command == "POST" and h.path == "/api/runs":
            return site.reply(h, 201, {"id": "run-1", "status": "queued"})
        if h.command == "GET" and h.path == "/api/runs/run-1":
            polls = site.state["polls"] = site.state.get("polls", 0) + 1
            if polls == 1:
                return site.reply(h, 503, {"detail": {"error": "identity_unavailable", "message": "identity unreachable"}}, {"Retry-After": "5"})
            return site.reply(h, 200, {"id": "run-1", "status": "running" if polls == 2 else "succeeded"})
        return site.reply(h, 404, {"detail": {"error": "run_not_found", "message": "no such run"}})

    site = _Site(behave)
    yield site
    site.close()


@pytest.fixture
def wired(monkeypatch, flow, identity):
    monkeypatch.setattr(adapter, "AIOS_FLOW_URL", flow.url)
    monkeypatch.setattr(adapter, "record_trace", lambda **kw: None)
    monkeypatch.setattr("adapters.aios_flow.identity_token.record_trace", lambda **kw: None)
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_URL", f"{identity.url}/identity")
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_SECRET", SECRET)
    return flow


def test_dispatch_and_a_wait_that_survives_a_503_work_end_to_end_with_the_token_on_the_wire(wired, identity):
    sent = adapter.dispatch({"pipeline": "ok-flow"})
    assert sent["status"] == "dispatched" and sent["flow_run_id"] == "run-1"

    sleeps: list[float] = []
    done = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert done["status"] == "ok" and done["flow_status"] == "succeeded" and done["timed_out"] is False
    assert sleeps == [5.0, 1]  # the real Retry-After: 5 header was honoured, then one ordinary poll interval

    (mint,) = [r for r in identity.requests]
    assert mint["body"] == {"username": "svc:atp", "secret": SECRET, "consumer": "ATP"} and "authorization" not in mint["headers"]
    token = next(iter(identity.state["issued"]))
    assert len(identity.state["issued"]) == 1  # one token served the dispatch and every poll, retries included
    assert [r["headers"].get("authorization") for r in wired.requests] == [f"Bearer {token}"] * len(wired.requests) and len(wired.requests) == 4


def test_a_redirect_does_not_carry_the_token_to_another_host(wired, foreign):
    """urllib copies `request.headers` onto a redirected request, whatever the new host. The token is therefore not in `request.headers`."""
    out = adapter._open_json("GET", "/api/redirect-me", req_id="a" * 16)
    assert out == {"id": "run-redir", "status": "running"}  # the redirect was followed ...
    assert len(foreign.requests) == 1
    assert "authorization" not in foreign.requests[0]["headers"]  # ... without the token
    assert "x-request-id" in foreign.requests[0]["headers"]  # (other headers still go along: the point is only the credential)


def test_wrong_credentials_are_an_auth_failure_and_aios_flow_is_never_contacted(wired, identity, monkeypatch):
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_SECRET", "not-the-right-secret-at-all")
    out = adapter.dispatch({"pipeline": "ok-flow"})
    assert out["status"] == "error" and out["error_code"] == "auth_failed" and out["retryable"] is False
    assert "invalid_service_credentials" in out["error"]
    assert wired.requests == []


def test_a_server_that_never_answers_is_retried_like_any_network_failure(wired, monkeypatch):
    """urlopen lets a read timeout escape as a bare TimeoutError; it is converted so that core.retry sees a network error and the wait retries it."""
    hung = socket.socket()
    hung.bind(("127.0.0.1", 0))
    hung.listen(8)
    accepted: list[socket.socket] = []

    def accept_and_hold() -> None:
        while True:
            try:
                accepted.append(hung.accept()[0])
            except OSError:
                return

    threading.Thread(target=accept_and_hold, daemon=True).start()
    try:
        monkeypatch.setattr(adapter, "AIOS_FLOW_URL", f"http://127.0.0.1:{hung.getsockname()[1]}")
        started = time.monotonic()
        out = adapter._get_run_status("run-1", timeout_s=0.3, retry_sleep=lambda _s: None, retry_budget_s=30)
        assert out["status"] == "error" and out["error_code"] == "unreachable" and out["retryable"] is True
        assert len(accepted) == 4  # first try + three retries
        assert time.monotonic() - started < 10
    finally:
        hung.close()
        for conn in accepted:
            conn.close()
