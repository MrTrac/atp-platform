"""ATP → aios-flow DAG runner adapter (AI_OS Doctrine v5 §3).

Dispatches a workflow to the aios-flow orchestration engine at :7700.
ATP owns the envelope and governance classification; aios-flow owns
DAG execution, approval gates, and stage runners.

Contract: ATP_aios-flow_v1  (HTTP API: aios-flow docs/RUNS_API.md)

Three actions, dispatched via the top-level ``dispatch()`` router by
``incoming["action"]``:
  - ``"dispatch"`` (default) — submit a flow, return immediately with the
    new ``flow_run_id`` and initial ``flow_status``.
  - ``"status"`` — fetch a single-shot snapshot of an existing run via
    ``GET /api/runs/{id}``.
  - ``"wait"`` (v2.4.0) — poll a run until it reaches a terminal state
    (success | failed | cancelled), bounded by ``timeout_s`` and
    ``poll_interval_s``.

Request shape (dispatch):
    pipeline   (str, required) — name of a flow that already exists on the
               aios-flow server (inline YAML is refused by aios-flow with 400)
    inputs     (dict, optional) — values for the variables the flow declares

Request shape (status / wait):
    flow_run_id (str, required)
    timeout_s   (int, optional, default 300) — wait only
    poll_interval_s (int, optional, default 2) — wait only

Authentication (aios-flow >= 1.2.0 enforces it): when ``AIOS_FLOW_IDENTITY_URL`` is set, every
request carries ``Authorization: Bearer <access token of svc:atp>``. See ``identity_token`` for
the configuration, the token's lifetime and how minting is rationed. Unset, nothing is sent and
the adapter behaves as before (right for an aios-flow that does not enforce). The token goes to
aios-flow and nowhere else, only over https or to a loopback address, never follows a redirect,
and is never in a result, an error text or the trace file. A 401 makes the adapter obtain a
fresh token and repeat the request once.

Failures keep ``status == "error"`` and ``error`` (text) and add, so a caller need not parse text:
    error_code  "auth_failed"  aios-flow answered 401/403, aios-identity refused the credentials,
                               or the authentication settings cannot work: no retry helps
                "unavailable"  aios-flow answered 429/502/503/504 (503 identity_unavailable is how
                               aios-flow says identity is briefly unreachable), or identity could
                               not issue a token: try again later
                "unreachable"  no answer at all (refused, DNS, timeout)
                "http_error"   any other HTTP status from aios-flow (404 unknown run or flow,
                               400 invalid input, ...)
                "bad_response" the answer was not JSON
    retryable   bool: True for "unavailable" and "unreachable"
    http_status (int) when there was an HTTP answer; retry_after_s (float) when the server named a delay
    reason_code the specific code: the server's own (invalid_token, forbidden, identity_unavailable,
                flow_not_found, invalid_service_credentials, ...) or ours for a settings problem
                (missing_secret, insecure_transport)
    auth_source with "auth_failed": who refused ("aios-flow", "aios-identity" or "config")

``wait`` retries "unavailable" and "unreachable" within each poll (``core.retry``: exponential
backoff, ``Retry-After`` honoured, at most 4 attempts and 60 s per poll, never beyond the wait's
own ``timeout_s``) because a poll only reads. ``dispatch`` never retries by itself (a transport
failure of a POST may have started the run) and ``status`` is a single shot.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from adapters.aios_flow import identity_token
from adapters.aios_flow.identity_token import AuthError, IdentityUnavailable
from core.http_errors import close_http_error, error_code_and_message, read_error_body
from core.retry import _retry_after_seconds, with_retry
from core.trace import generate_request_id, record_trace, trace_headers

AIOS_FLOW_URL = os.environ.get("AIOS_FLOW_URL", "http://localhost:7700")
_CONTRACT = "ATP_aios-flow_v1"
_DEFAULT_TIMEOUT_S = 10
_TERMINAL_STATES = {"success", "succeeded", "failed", "cancelled", "canceled", "error"}
_DEFAULT_WAIT_TIMEOUT_S = 300
_DEFAULT_POLL_INTERVAL_S = 2
_POLL_RETRY_ATTEMPTS = 4  # per poll, the first try included
_POLL_RETRY_BASE_DELAY_S = 1.0
_POLL_RETRY_MAX_DELAY_S = 30.0
_POLL_RETRY_BUDGET_S = 60.0  # most time one poll may spend sleeping between attempts


# -- transport ------------------------------------------------------------


def _send(
    method: str,
    path: str,
    *,
    req_id: str,
    timeout_s: float,
    payload: bytes | None,
    token: str | None,
) -> dict[str, Any]:
    """One HTTP exchange with aios-flow. Returns the parsed JSON body.

    Raises what urllib raises (an HTTPError for every non-2xx answer)."""
    headers = dict(trace_headers(req_id))
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = Request(f"{AIOS_FLOW_URL}{path}", data=payload, headers=headers, method=method)
    if token is not None:
        # unredirected: urllib copies `request.headers` onto a redirected request, Authorization
        # included and whatever the new host; it does not copy this dict
        request.add_unredirected_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(request, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (TimeoutError, ConnectionError) as exc:
        # getresponse() raises these outside urlopen's own wrapping, so core.retry would not see
        # a network error; never an HTTPError
        raise URLError(exc) from exc


def _flow_refusal(status: int, code: str | None, message: str | None, *, sent_token: bool, declined: bool) -> AuthError:
    if status == 401:
        what = "rejected the identity token" if sent_token else "requires an identity token"
    else:
        what = "denied the request"
    text = f"aios-flow {what}: HTTP {status}" + (f" {code}" if code else "") + (f" - {message}" if message else "")
    if not sent_token:
        text += (
            " - no token was sent: set AIOS_FLOW_IDENTITY_URL and AIOS_FLOW_IDENTITY_SECRET"
            " (service account svc:atp)"
        )
    elif declined:
        text += " - identity issued that token moments ago, not asking for another"
    return AuthError(text, code=code or f"http_{status}", source="aios-flow", http_status=status)


def _open_json(
    method: str,
    path: str,
    *,
    req_id: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
    payload: bytes | None = None,
) -> dict[str, Any]:
    """One call to aios-flow, authenticated when the environment says so. Returns the parsed JSON body.

    Raises AuthError (authentication cannot succeed), IdentityUnavailable / URLError / OSError
    (transport), ValueError (not JSON) and, for every other non-2xx answer, the HTTPError itself,
    still open: whoever catches it reads what it needs and closes it (the envelope builders, and
    `with_retry` for the attempts it drops). A 401 or 403 is read and closed here, because this
    function interprets it."""
    provider = identity_token.get_provider()
    token: str | None = None
    if provider is not None:
        # before any mint: a token that cannot be sent safely is not requested
        identity_token.check_transport(AIOS_FLOW_URL, what="AIOS_FLOW_URL")
        token = provider.get_token()
    sent_token = token is not None
    declined = False
    for attempt in (1, 2):
        try:
            return _send(method, path, req_id=req_id, timeout_s=timeout_s, payload=payload, token=token)
        except HTTPError as exc:
            if exc.code not in (401, 403):
                raise
            status = exc.code
            code, message = error_code_and_message(read_error_body(exc))
            close_http_error(exc)
        if status == 401 and attempt == 1 and provider is not None and token is not None:
            token = provider.refresh_after_rejection(token)
            if token is not None:
                continue
            declined = True
        raise _flow_refusal(status, code, message, sent_token=sent_token, declined=declined)
    raise AssertionError("unreachable")  # the loop either returns, continues once, or raises


# -- failures → envelopes --------------------------------------------------


def _failure_envelope(exc: BaseException, *, req_id: str, flow_run_id: str | None = None) -> dict[str, Any]:
    """The ATP-shaped error envelope for a failure of `_open_json`.

    Reads the body of an HTTPError, so call it BEFORE `close_http_error(exc)`."""
    out: dict[str, Any] = {"status": "error", "selected_provider": "aios-flow", "request_id": req_id}
    if flow_run_id:
        out["flow_run_id"] = flow_run_id
    if isinstance(exc, AuthError):
        out.update(
            error=str(exc), error_code="auth_failed", retryable=False, auth_source=exc.source, reason_code=exc.code,
        )
        if exc.http_status is not None:
            out["http_status"] = exc.http_status
    elif isinstance(exc, IdentityUnavailable):
        out.update(error=f"cannot get an identity token for aios-flow: {exc}", error_code="unavailable", retryable=True)
        if exc.http_status is not None:
            out["http_status"] = exc.http_status
    elif isinstance(exc, HTTPError):
        status = exc.code
        code, message = error_code_and_message(read_error_body(exc))
        retry_after = _retry_after_seconds(exc)
        transient = status in (429, 502, 503, 504)
        text = f"aios-flow {'unavailable' if transient else 'answered'}: HTTP {status}"
        text += f" {code}" if code else (f" {exc.reason}" if exc.reason else "")
        text += f" - {message}" if message else ""
        if retry_after is not None:
            text += f" (retry after {retry_after:g} s)"
            out["retry_after_s"] = retry_after
        out.update(
            error=text,
            error_code="unavailable" if transient else "http_error",
            retryable=transient,
            http_status=status,
        )
        if code:
            out["reason_code"] = code
    else:
        out.update(error=f"aios-flow unreachable: {exc}", error_code="unreachable", retryable=True)
    return out


def _non_json_envelope(exc: ValueError, *, req_id: str, flow_run_id: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "status": "error",
        "error": f"aios-flow returned non-JSON: {exc}",
        "error_code": "bad_response",
        "retryable": False,
        "selected_provider": "aios-flow",
        "request_id": req_id,
    }
    if flow_run_id:
        out["flow_run_id"] = flow_run_id
    return out


# -- actions ---------------------------------------------------------------


def _submit(incoming: dict[str, Any]) -> dict[str, Any]:
    """Submit a DAG workflow to aios-flow /api/runs (non-blocking).

    Returns
    -------
    dict
        ATP-shaped envelope with flow_run_id and initial status,
        or error envelope if aios-flow is unreachable or refuses.
    """
    pipeline = incoming.get("pipeline") or (incoming.get("target") or {}).get("flow")
    if not pipeline:
        return {
            "status": "error",
            "error": "aios-flow adapter: 'pipeline' field required (or 'target.flow')",
            "selected_provider": "aios-flow",
        }

    req_id = generate_request_id()
    payload = json.dumps({
        "pipeline": pipeline,
        "inputs": incoming.get("inputs", {}),
    }).encode("utf-8")

    t0 = time.monotonic()
    try:
        body = _open_json("POST", "/api/runs", req_id=req_id, payload=payload)
        trace_status = "ok"
        result: dict[str, Any] = {
            "status": "dispatched",
            "selected_provider": "aios-flow",
            "flow_run_id": body.get("id"),
            "flow_status": body.get("status"),
            "request_id": req_id,
            "aios_flow_url": AIOS_FLOW_URL,
        }
    except (AuthError, HTTPError, URLError, OSError) as exc:
        trace_status = "error"
        result = _failure_envelope(exc, req_id=req_id)
        close_http_error(exc)
    except ValueError as exc:
        trace_status = "error"
        result = _non_json_envelope(exc, req_id=req_id)

    record_trace(
        request_id=req_id,
        target_module="aios-flow",
        route="/api/runs",
        method="POST",
        status=trace_status,
        duration_ms=int((time.monotonic() - t0) * 1000),
        contract_version=_CONTRACT,
    )
    return result


def _get_run_status(
    flow_run_id: str,
    *,
    timeout_s: int = _DEFAULT_TIMEOUT_S,
    record: bool = True,
    retry_sleep: Any = None,
    retry_budget_s: float = 0.0,
) -> dict[str, Any]:
    """Snapshot of a flow run via GET /api/runs/{id}.

    A single shot unless ``retry_budget_s`` > 0: then transient failures (see the module
    docstring) are retried through ``core.retry.with_retry``, sleeping with ``retry_sleep``, for
    at most that many seconds of waiting. Every attempt leaves its own G9 trace record.
    """
    if not flow_run_id:
        return {
            "status": "error",
            "error": "aios-flow status: 'flow_run_id' is required",
            "selected_provider": "aios-flow",
        }

    path = f"/api/runs/{flow_run_id}"
    last = {"req_id": ""}

    def attempt() -> dict[str, Any]:
        req_id = last["req_id"] = generate_request_id()
        t0 = time.monotonic()
        ok = False
        try:
            body = _open_json("GET", path, req_id=req_id, timeout_s=timeout_s)
            ok = True
            return body
        finally:
            if record:
                record_trace(
                    request_id=req_id,
                    target_module="aios-flow",
                    route=path,
                    method="GET",
                    status="ok" if ok else "error",
                    duration_ms=int((time.monotonic() - t0) * 1000),
                    contract_version=_CONTRACT,
                )

    try:
        if retry_budget_s > 0:
            body = with_retry(
                attempt,
                max_attempts=_POLL_RETRY_ATTEMPTS,
                base_delay=_POLL_RETRY_BASE_DELAY_S,
                max_delay=_POLL_RETRY_MAX_DELAY_S,
                max_total_wait=retry_budget_s,
                sleep_fn=retry_sleep or time.sleep,
            )
        else:
            body = attempt()
        return {
            "status": "ok",
            "selected_provider": "aios-flow",
            "flow_run_id": body.get("id", flow_run_id),
            "flow_status": body.get("status"),
            "flow_run": body,
            "request_id": last["req_id"],
        }
    except (AuthError, HTTPError, URLError, OSError) as exc:
        result = _failure_envelope(exc, req_id=last["req_id"], flow_run_id=flow_run_id)
        close_http_error(exc)
        return result
    except ValueError as exc:
        return _non_json_envelope(exc, req_id=last["req_id"], flow_run_id=flow_run_id)


def _wait_for_run(
    flow_run_id: str,
    *,
    timeout_s: int = _DEFAULT_WAIT_TIMEOUT_S,
    poll_interval_s: int = _DEFAULT_POLL_INTERVAL_S,
    sleep_fn: "callable | None" = None,
    now_fn: "callable | None" = None,
) -> dict[str, Any]:
    """Poll until the run reaches a terminal state or timeout elapses.

    Terminal states: success | succeeded | failed | cancelled | canceled |
    error.

    A poll that fails transiently (aios-flow 429/502/503/504, e.g. 503 identity_unavailable
    while identity is briefly unreachable, or no answer at all) is retried within that poll
    (see the module docstring) before the wait gives up on it; a failure no retry can fix
    (401/403, 404, non-JSON) ends the wait at once.

    Returns the final ATP-shaped envelope. Adds:
        ``waited_s``  — total wall-clock seconds waited
        ``poll_count`` — number of polls issued (retries within a poll are not counted)
        ``timed_out`` — True if the wait hit ``timeout_s`` first
    """
    if not flow_run_id:
        return {
            "status": "error",
            "error": "aios-flow wait: 'flow_run_id' is required",
            "selected_provider": "aios-flow",
        }

    sleep = sleep_fn or time.sleep
    now = now_fn or time.monotonic
    start = now()
    poll_count = 0
    elapsed = 0.0
    last_result: dict[str, Any] = {}

    while True:
        poll_count += 1
        budget = max(0.0, min(_POLL_RETRY_BUDGET_S, timeout_s - elapsed))
        last_result = _get_run_status(
            flow_run_id, timeout_s=_DEFAULT_TIMEOUT_S, retry_sleep=sleep, retry_budget_s=budget,
        )
        flow_status = (last_result.get("flow_status") or "").lower()
        if flow_status in _TERMINAL_STATES:
            last_result["waited_s"] = round(now() - start, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = False
            return last_result
        if last_result.get("status") == "error":
            last_result["waited_s"] = round(now() - start, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = False
            return last_result
        elapsed = now() - start
        if elapsed >= timeout_s:
            last_result["status"] = "timeout"
            last_result["error"] = (
                f"aios-flow wait: run {flow_run_id} did not reach terminal "
                f"state within {timeout_s}s (last status: {flow_status})"
            )
            last_result["waited_s"] = round(elapsed, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = True
            return last_result
        sleep(poll_interval_s)


def dispatch(incoming: dict[str, Any]) -> dict[str, Any]:
    """Route ``provider='aios-flow'`` bridge requests by ``action``.

    Default action (``"dispatch"`` or missing) preserves v2.1.0 behavior:
    submit and return immediately. New v2.4.0 actions:

    - ``status``: single-shot ``GET /api/runs/{id}``.
    - ``wait``:   poll until terminal or timeout.
    """
    action = (incoming.get("action") or "dispatch").strip()

    if action in ("dispatch", "submit", ""):
        return _submit(incoming)
    if action == "status":
        return _get_run_status(incoming.get("flow_run_id", ""))
    if action == "wait":
        return _wait_for_run(
            incoming.get("flow_run_id", ""),
            timeout_s=int(incoming.get("timeout_s", _DEFAULT_WAIT_TIMEOUT_S)),
            poll_interval_s=int(incoming.get("poll_interval_s", _DEFAULT_POLL_INTERVAL_S)),
        )
    return {
        "status": "error",
        "error": f"aios-flow adapter: unknown action '{action}' "
                 "(expected: dispatch | status | wait)",
        "selected_provider": "aios-flow",
    }
