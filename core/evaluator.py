"""ATP evaluator pattern — post-run validation (AI_OS Doctrine v5 §6).

Supports http-probe evaluator natively (stdlib only).
llm-judge and visual-diff return a stub pointing to aios-flow delegation.

Invoke from bridge_request by including an "evaluator" key in the request:
    {
        "text": "...",
        "evaluator": {
            "type": "http-probe-evaluator",
            "url": "http://localhost:3002/api/health",
            "expect_json_key": "status",
            "expect_json_value": "ok"
        }
    }

The evaluator result is appended to the bridge response under "evaluator".
"""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def _run_http_probe(spec: dict[str, Any]) -> dict[str, Any]:
    url = spec.get("url", "")
    if not url:
        return {"passed": False, "error": "http-probe: 'url' is required"}
    expect_status = spec.get("expect_status", 200)
    expect_key = spec.get("expect_json_key")
    expect_val = spec.get("expect_json_value")
    timeout = spec.get("timeout_seconds", 10)

    t0 = time.monotonic()
    try:
        with urlopen(url, timeout=timeout) as resp:
            code = resp.status
            body = resp.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        code, body = exc.code, ""
    except (URLError, OSError) as exc:
        return {"passed": False, "error": str(exc),
                "duration_ms": int((time.monotonic() - t0) * 1000)}

    elapsed = int((time.monotonic() - t0) * 1000)
    passed = code == expect_status
    if passed and expect_key is not None:
        try:
            passed = json.loads(body).get(expect_key) == expect_val
        except Exception:  # noqa: BLE001
            passed = False

    return {
        "passed": passed,
        "http_status": code,
        "http_body": body[:500],
        "duration_ms": elapsed,
    }


def run_evaluator(spec: dict[str, Any]) -> dict[str, Any]:
    """Dispatch an evaluator spec and return the result.

    Only ``http-probe-evaluator`` runs natively.
    ``llm-judge-evaluator`` and ``visual-diff-evaluator`` require aios-flow
    and return a stub until that delegation is wired (Phase 2).
    """
    eval_type = spec.get("type", "http-probe-evaluator")
    if eval_type == "http-probe-evaluator":
        return _run_http_probe(spec)
    return {
        "passed": None,
        "skipped": True,
        "reason": f"'{eval_type}' requires aios-flow delegation — not yet wired (Phase 2)",
    }
