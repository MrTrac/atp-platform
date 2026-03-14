"""Workspace materialization helpers for ATP v0.2 Slice 1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]
SLICE1_RUN_ZONES = (
    "request",
    "manifests",
    "routing",
    "executor-outputs",
    "validation",
    "decisions",
    "final",
    "logs",
)


def _resolve_repo_root(repo_root: Path | None = None) -> Path:
    return (repo_root or DEFAULT_REPO_ROOT).resolve()


def resolve_workspace_root(repo_root: Path | None = None) -> Path:
    """Resolve the ATP runtime workspace root from the ATP repo boundary."""

    resolved_repo_root = _resolve_repo_root(repo_root)
    if resolved_repo_root.name != "ATP":
        raise ValueError("ATP runtime workspace resolution requires the ATP repo root.")

    platforms_root = resolved_repo_root.parent
    source_dev_root = platforms_root.parent
    if platforms_root.name != "platforms" or source_dev_root.name != "SOURCE_DEV":
        raise ValueError("ATP runtime workspace must resolve from SOURCE_DEV/platforms/ATP.")

    return source_dev_root / "workspace"


def resolve_run_root(
    run_id: str,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> Path:
    """Resolve the per-run root under SOURCE_DEV/workspace/atp-runs."""

    if not str(run_id).strip():
        raise ValueError("run_id is required for runtime materialization.")

    runtime_root = workspace_root.resolve() if workspace_root is not None else resolve_workspace_root(repo_root)
    return runtime_root / "atp-runs" / run_id


def workspace_path(run_id: str, area: str) -> str:
    """Return the approved runtime workspace path for a run area."""

    if area not in SLICE1_RUN_ZONES:
        raise ValueError(f"Unsupported Slice 1 runtime area: {area}")
    return str(Path("SOURCE_DEV") / "workspace" / "atp-runs" / run_id / area)


def repo_local_serialization_path(run_id: str, area: str) -> Path:
    """Return a legacy repo-local fixture path for test-only compatibility."""

    return Path("tests") / "fixtures" / "outputs" / area / run_id


def materialize_run_tree(
    run_id: str,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Path]:
    """Create the approved ATP v0.2 Slice 1 run tree."""

    run_root = resolve_run_root(run_id, repo_root=repo_root, workspace_root=workspace_root)
    run_root.mkdir(parents=True, exist_ok=True)

    zone_paths: dict[str, Path] = {}
    for zone in SLICE1_RUN_ZONES:
        zone_path = run_root / zone
        zone_path.mkdir(exist_ok=True)
        zone_paths[zone] = zone_path
    return {"workspace_root": run_root.parent.parent, "run_root": run_root, **zone_paths}


def _write_json(path: Path, payload: Any) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_log(path: Path, lines: list[str]) -> Path:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def materialize_run_outputs(
    run_id: str,
    payloads: dict[str, Any],
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Materialize the minimal ATP v0.2 Slice 1 run tree outputs."""

    zone_paths = materialize_run_tree(run_id, repo_root=repo_root, workspace_root=workspace_root)
    created_files = {
        "request": [
            _write_json(zone_paths["request"] / "request.raw.json", payloads["raw_request"]),
            _write_json(zone_paths["request"] / "request.normalized.json", payloads["normalized_request"]),
            _write_json(zone_paths["request"] / "classification.json", payloads["classification"]),
        ],
        "manifests": [
            _write_json(zone_paths["manifests"] / "resolution.json", payloads["resolution"]),
            _write_json(zone_paths["manifests"] / "task-manifest.json", payloads["task_manifest"]),
            _write_json(zone_paths["manifests"] / "product-context.json", payloads["product_context"]),
            _write_json(zone_paths["manifests"] / "manifest-reference.json", payloads["manifest_reference"]),
            _write_json(zone_paths["manifests"] / "run-record.json", payloads["run_record"]),
        ],
        "routing": [
            _write_json(zone_paths["routing"] / "route-preparation.json", payloads["prepared_route"]),
            _write_json(zone_paths["routing"] / "routing-result.json", payloads["routing_result"]),
        ],
        "executor-outputs": [
            _write_json(zone_paths["executor-outputs"] / "execution-result.json", payloads["execution_result"]),
            _write_json(zone_paths["executor-outputs"] / "artifacts.json", payloads["artifacts"]),
        ],
        "validation": [
            _write_json(zone_paths["validation"] / "validation-summary.json", payloads["validation_summary"]),
        ],
        "decisions": [
            _write_json(zone_paths["decisions"] / "review-decision.json", payloads["review_decision"]),
            _write_json(zone_paths["decisions"] / "approval-result.json", payloads["approval_result"]),
            _write_json(zone_paths["decisions"] / "close-or-continue.json", payloads["close_or_continue"]),
            _write_json(zone_paths["decisions"] / "decision-state.json", payloads["decision_state"]),
        ],
        "final": [
            _write_json(zone_paths["final"] / "finalization-summary.json", payloads["finalization_summary"]),
        ],
        "logs": [
            _write_log(
                zone_paths["logs"] / "execution.log",
                [
                    f"run_id={run_id}",
                    f"execution_id={payloads['execution_result'].get('execution_id', '')}",
                    f"status={payloads['execution_result'].get('status', '')}",
                    f"exit_code={payloads['execution_result'].get('exit_code', '')}",
                    "command=" + " ".join(payloads["execution_result"].get("command", [])),
                    "--- stdout ---",
                    str(payloads["execution_result"].get("stdout", "")),
                    "--- stderr ---",
                    str(payloads["execution_result"].get("stderr", "")),
                ],
            ),
        ],
    }

    materialization_lines = [
        f"run_id={run_id}",
        f"workspace_root={zone_paths['workspace_root']}",
        f"run_root={zone_paths['run_root']}",
        "zones=" + ",".join(SLICE1_RUN_ZONES),
    ]
    for zone in SLICE1_RUN_ZONES:
        materialization_lines.append(f"{zone}={zone_paths[zone]}")
    for zone_name, files in created_files.items():
        for path in files:
            materialization_lines.append(f"file[{zone_name}]={path}")
    created_files["logs"].append(_write_log(zone_paths["logs"] / "materialization.log", materialization_lines))

    return {
        "workspace_root": str(zone_paths["workspace_root"]),
        "run_root": str(zone_paths["run_root"]),
        "zones": {zone: str(zone_paths[zone]) for zone in SLICE1_RUN_ZONES},
        "files": {zone: [str(path) for path in files] for zone, files in created_files.items()},
    }
