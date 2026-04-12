"""Optional persistence of bridge run results to the ATP workspace.

When ``ATP_PERSIST_RUNS`` is enabled, each bridge execution writes its
request, routing, and execution result to ``SOURCE_DEV/workspace/atp-runs/``.
Disabled by default. Never blocks execution — persistence errors are caught.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PERSIST_RUNS = os.environ.get("ATP_PERSIST_RUNS", "").lower() in ("1", "true", "yes")


def persist_bridge_run(
    request_id: str,
    normalized_request: dict[str, Any],
    routing_result: dict[str, Any],
    raw_result: dict[str, Any],
    normalized_output: dict[str, Any],
    *,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Persist a bridge run to the workspace.

    Returns a manifest dict describing what was written.
    Returns ``{"persisted": False}`` if disabled or on error.
    """
    if not PERSIST_RUNS and workspace_root is None:
        return {"persisted": False, "reason": "disabled"}

    try:
        ws = workspace_root or _resolve_workspace()
        run_dir = ws / "atp-runs" / request_id
        run_dir.mkdir(parents=True, exist_ok=True)

        written: list[str] = []

        # Request zone
        req_dir = run_dir / "request"
        req_dir.mkdir(exist_ok=True)
        _write(req_dir / "request.normalized.json", normalized_request)
        written.append("request/request.normalized.json")

        # Routing zone
        routing_dir = run_dir / "routing"
        routing_dir.mkdir(exist_ok=True)
        _write(routing_dir / "routing-result.json", routing_result)
        written.append("routing/routing-result.json")

        # Executor outputs zone
        exec_dir = run_dir / "executor-outputs"
        exec_dir.mkdir(exist_ok=True)
        _write(exec_dir / "execution-result.json", normalized_output)
        written.append("executor-outputs/execution-result.json")

        if raw_result.get("ollama_manifest"):
            _write(exec_dir / "ollama-manifest.json", raw_result["ollama_manifest"])
            written.append("executor-outputs/ollama-manifest.json")

        if raw_result.get("ollama_routing"):
            _write(exec_dir / "ollama-routing.json", raw_result["ollama_routing"])
            written.append("executor-outputs/ollama-routing.json")

        # Run summary
        summary = {
            "run_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": normalized_output.get("status", "unknown"),
            "provider": routing_result.get("selected_provider", "unknown"),
            "model": routing_result.get("selected_provider_model", "unknown"),
            "files_written": written,
        }
        _write(run_dir / "run-summary.json", summary)
        written.append("run-summary.json")

        return {
            "persisted": True,
            "run_id": request_id,
            "run_path": str(run_dir),
            "files_written": written,
        }
    except Exception as exc:
        return {"persisted": False, "reason": f"persistence error: {exc}"}


def list_runs(*, workspace_root: Path | None = None) -> list[dict[str, Any]]:
    """List recent runs from the workspace, newest first."""
    try:
        ws = workspace_root or _resolve_workspace()
        runs_dir = ws / "atp-runs"
        if not runs_dir.is_dir():
            return []

        runs: list[dict[str, Any]] = []
        for run_dir in sorted(runs_dir.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
            summary_path = run_dir / "run-summary.json"
            if summary_path.is_file():
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                runs.append(summary)
            else:
                runs.append({"run_id": run_dir.name, "status": "unknown"})
        return runs
    except Exception:
        return []


def get_run(run_id: str, *, workspace_root: Path | None = None) -> dict[str, Any] | None:
    """Read a specific run's summary and available files."""
    try:
        ws = workspace_root or _resolve_workspace()
        run_dir = ws / "atp-runs" / run_id
        if not run_dir.is_dir():
            return None

        result: dict[str, Any] = {"run_id": run_id, "path": str(run_dir)}

        summary_path = run_dir / "run-summary.json"
        if summary_path.is_file():
            result["summary"] = json.loads(summary_path.read_text(encoding="utf-8"))

        # List available zone files
        zones: dict[str, list[str]] = {}
        for zone_dir in sorted(run_dir.iterdir()):
            if zone_dir.is_dir():
                zones[zone_dir.name] = [f.name for f in sorted(zone_dir.iterdir()) if f.is_file()]
        result["zones"] = zones

        return result
    except Exception:
        return None


def _write(path: Path, data: Any) -> None:
    """Write JSON to a file."""
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_workspace() -> Path:
    """Resolve workspace from ATP repo layout."""
    from adapters.filesystem.workspace_writer import resolve_workspace_root
    return resolve_workspace_root()
