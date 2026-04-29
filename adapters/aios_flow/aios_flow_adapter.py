"""ATP → aios-flow DAG runner adapter (AI_OS Doctrine v5 §3).

Dispatches a workflow to the aios-flow orchestration engine at :7700.
ATP owns the envelope and governance classification; aios-flow owns
DAG execution, approval gates, and stage runners.

Contract: ATP_aios-flow_v1

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
    pipeline   (str, required) — flow name or inline YAML
    inputs     (dict, optional) — context variables for the flow

Request shape (status / wait):
    flow_run_id (str, required)
    timeout_s   (int, optional, default 300) — wait only
    poll_interval_s (int, optional, default 2) — wait only
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.trace import generate_request_id, record_trace, trace_headers

AIOS_FLOW_URL = os.environ.get("AIOS_FLOW_URL", "http://localhost:7700")
_CONTRACT = "ATP_aios-flow_v1"
_DEFAULT_TIMEOUT_S = 10
_TERMINAL_STATES = {"success", "succeeded", "failed", "cancelled", "canceled", "error"}
_DEFAULT_WAIT_TIMEOUT_S = 300
_DEFAULT_POLL_INTERVAL_S = 2


def _submit(incoming: dict[str, Any]) -> dict[str, Any]:
    """Submit a DAG workflow to aios-flow /api/runs (non-blocking).

    Returns
    -------
    dict
        ATP-shaped envelope with flow_run_id and initial status,
        or error envelope if aios-flow is unreachable.
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
        req = Request(
            f"{AIOS_FLOW_URL}/api/runs",
            data=payload,
            headers={"Content-Type": "application/json", **trace_headers(req_id)},
            method="POST",
        )
        with urlopen(req, timeout=_DEFAULT_TIMEOUT_S) as resp:
            body: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        trace_status = "ok"
        result: dict[str, Any] = {
            "status": "dispatched",
            "selected_provider": "aios-flow",
            "flow_run_id": body.get("id"),
            "flow_status": body.get("status"),
            "request_id": req_id,
            "aios_flow_url": AIOS_FLOW_URL,
        }
    except (HTTPError, URLError, OSError) as exc:
        trace_status = "error"
        result = {
            "status": "error",
            "error": f"aios-flow unreachable: {exc}",
            "selected_provider": "aios-flow",
            "request_id": req_id,
        }
    except json.JSONDecodeError as exc:
        trace_status = "error"
        result = {
            "status": "error",
            "error": f"aios-flow returned non-JSON: {exc}",
            "selected_provider": "aios-flow",
            "request_id": req_id,
        }

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
) -> dict[str, Any]:
    """Single-shot snapshot of a flow run via GET /api/runs/{id}."""
    if not flow_run_id:
        return {
            "status": "error",
            "error": "aios-flow status: 'flow_run_id' is required",
            "selected_provider": "aios-flow",
        }

    req_id = generate_request_id()
    t0 = time.monotonic()
    try:
        req = Request(
            f"{AIOS_FLOW_URL}/api/runs/{flow_run_id}",
            headers=trace_headers(req_id),
            method="GET",
        )
        with urlopen(req, timeout=timeout_s) as resp:
            body: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        trace_status = "ok"
        result: dict[str, Any] = {
            "status": "ok",
            "selected_provider": "aios-flow",
            "flow_run_id": body.get("id", flow_run_id),
            "flow_status": body.get("status"),
            "flow_run": body,
            "request_id": req_id,
        }
    except (HTTPError, URLError, OSError) as exc:
        trace_status = "error"
        result = {
            "status": "error",
            "error": f"aios-flow unreachable: {exc}",
            "selected_provider": "aios-flow",
            "flow_run_id": flow_run_id,
            "request_id": req_id,
        }
    except json.JSONDecodeError as exc:
        trace_status = "error"
        result = {
            "status": "error",
            "error": f"aios-flow returned non-JSON: {exc}",
            "selected_provider": "aios-flow",
            "flow_run_id": flow_run_id,
            "request_id": req_id,
        }

    if record:
        record_trace(
            request_id=req_id,
            target_module="aios-flow",
            route=f"/api/runs/{flow_run_id}",
            method="GET",
            status=trace_status,
            duration_ms=int((time.monotonic() - t0) * 1000),
            contract_version=_CONTRACT,
        )
    return result


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

    Returns the final ATP-shaped envelope. Adds:
        ``waited_s``  — total wall-clock seconds waited
        ``poll_count`` — number of /api/runs/{id} calls issued
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
    last_result: dict[str, Any] = {}

    while True:
        poll_count += 1
        last_result = _get_run_status(flow_run_id, timeout_s=_DEFAULT_TIMEOUT_S)
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
