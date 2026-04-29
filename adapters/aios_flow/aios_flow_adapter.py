"""ATP → aios-flow DAG runner adapter (AI_OS Doctrine v5 §3).

Dispatches a workflow to the aios-flow orchestration engine at :7700.
ATP owns the envelope and governance classification; aios-flow owns
DAG execution, approval gates, and stage runners.

Contract: ATP_aios-flow_v1
Usage from openclaw_bridge.bridge_request:
    if incoming.get("provider") == "aios-flow":
        return aios_flow_adapter.dispatch(incoming)

Request shape:
    pipeline   (str, required) — flow name or inline YAML
    inputs     (dict, optional) — context variables for the flow
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


def dispatch(incoming: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a DAG workflow to aios-flow /api/runs.

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
