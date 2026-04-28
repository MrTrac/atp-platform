"""ATP → TDF bridge: dispatch a bounded execution task to TDF Web Control Panel.

Translates an ATP request envelope into the TDF `/api/exec/execute` schema and
wraps the response back into the standard ATP run result envelope. TDF owns
bounded execution + RBAC + audit; ATP owns task orchestration + governance
classification.

Reference contract:
    ~/SOURCE_DEV/products/TDF/tdf/docs/integrations/ATP_BRIDGE_INTEGRATION.md

Usage from ``openclaw_bridge.bridge_request``:
    if incoming.get("provider") == "tdf-run":
        return tdf_run.dispatch(incoming)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request  # @allow-z3-non-canonical: no httpx dep in ATP; stdlib sufficient for single TDF endpoint
import uuid
from datetime import datetime, timezone
from typing import Any


TDF_WEB_URL_DEFAULT = "http://localhost:4180"
DEFAULT_TIMEOUT_S = 35


class TdfBridgeError(RuntimeError):
    """Raised when the TDF bridge cannot dispatch or interpret a request."""


def _governance_class(mode: dict[str, Any], params: dict[str, Any]) -> str:
    """Map a TDF operation to an ATP governance class A–E.

    See ATP_BRIDGE_INTEGRATION.md §"Governance gate mapping".
    """
    if mode.get("dry_run", True):
        return "C"
    op = (params.get("operation") or "").lower()
    if any(op.startswith(prefix) for prefix in ("rollback", "uninstall", "undeploy")):
        return "A"
    if any(op.startswith(prefix) for prefix in ("deploy", "install")):
        return "B"
    return "C"


def dispatch(incoming: dict[str, Any]) -> dict[str, Any]:
    """Pass-through ATP request → TDF /api/exec/execute → ATP result envelope.

    Parameters
    ----------
    incoming : dict
        Must contain ``target.tool``. Optional fields:
            target.partition  (str)
            params            (dict, e.g. {"operation": "validate"})
            mode              (dict, defaults to {"dry_run": True, "confirm": True})
            correlation_id    (str)

    Returns
    -------
    dict
        Standard ATP envelope with TDF response embedded under ``tdf`` key,
        plus ``bridge``, ``governance`` (preliminary class), and timestamps.
    """
    target = incoming.get("target") or {}
    tool = (target.get("tool") or "").strip()
    if not tool:
        raise TdfBridgeError(
            "'target.tool' is required for tdf-run provider (e.g. 'ops/checkos')"
        )

    mode = incoming.get("mode") or {"dry_run": True, "confirm": True}
    params = incoming.get("params") or {}

    request_id = f"bridge-tdf-{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    exec_request = {
        "schema": "tdf.web.exec.request.v1",
        "action": "tool.run",
        "correlation_id": incoming.get("correlation_id", request_id),
        "target": target,
        "params": params,
        "mode": mode,
    }

    base = os.environ.get("TDF_WEB_URL", TDF_WEB_URL_DEFAULT).rstrip("/")
    url = f"{base}/api/exec/execute"

    req = urllib.request.Request(
        url,
        data=json.dumps(exec_request).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_S) as resp:
            tdf_payload: dict[str, Any] = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise TdfBridgeError(
            f"TDF returned HTTP {exc.code}: {exc.reason}"
        ) from exc
    except (urllib.error.URLError, OSError) as exc:
        raise TdfBridgeError(f"Cannot reach TDF at {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TdfBridgeError(f"TDF returned non-JSON response: {exc}") from exc

    data = tdf_payload.get("data", {}) if isinstance(tdf_payload.get("data"), dict) else {}
    success = tdf_payload.get("status") in ("ok", "accepted")

    envelope: dict[str, Any] = {
        "request_id": request_id,
        "status": "completed" if success else "failed",
        "selected_provider": "tdf-run",
        "selected_provider_model": "tdf",
        "stdout": data.get("stdout_preview", ""),
        "stderr": data.get("stderr_preview", ""),
        "text": tdf_payload.get("message", ""),
        "tdf": tdf_payload,
        "bridge": {
            "source": "tdf-run",
            "bridge_timestamp": timestamp,
            "resolved_provider": "tdf-run",
            "resolved_model": "tdf",
            "tdf_endpoint": url,
        },
        "governance": {
            "preliminary_class": _governance_class(mode, params),
            "requires_human": _governance_class(mode, params) in ("A", "B"),
        },
    }
    if not success:
        envelope["error"] = tdf_payload.get("message") or "TDF reported failure"

    return envelope
