"""Workspace materialization helpers for ATP v0.2 runtime slices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_TREE_ZONES = (
    "request",
    "manifests",
    "routing",
    "executor-outputs",
    "validation",
    "decisions",
    "handoff",
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


def resolve_artifact_projection_root(
    artifact_id: str,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> Path:
    """Resolve the projection root for an authoritative artifact."""

    if not str(artifact_id).strip():
        raise ValueError("artifact_id is required for authoritative projection.")

    runtime_root = workspace_root.resolve() if workspace_root is not None else resolve_workspace_root(repo_root)
    return runtime_root / "atp-artifacts" / artifact_id


def workspace_path(run_id: str, area: str) -> str:
    """Return the approved runtime workspace path for a run area."""

    if area not in RUN_TREE_ZONES:
        raise ValueError(f"Unsupported ATP runtime area: {area}")
    return str(Path("SOURCE_DEV") / "workspace" / "atp-runs" / run_id / area)


def repo_local_serialization_path(run_id: str, area: str) -> Path:
    """Return a legacy repo-local fixture path for test-only compatibility."""

    return Path("tests") / "fixtures" / "outputs" / area / run_id


def materialize_run_tree(
    run_id: str,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Path]:
    """Create the approved ATP v0.2 run tree for the current slices."""

    run_root = resolve_run_root(run_id, repo_root=repo_root, workspace_root=workspace_root)
    run_root.mkdir(parents=True, exist_ok=True)

    zone_paths: dict[str, Path] = {}
    for zone in RUN_TREE_ZONES:
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


def project_authoritative_artifacts(
    run_id: str,
    artifacts: list[dict[str, Any]],
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Project authoritative artifacts into SOURCE_DEV/workspace/atp-artifacts."""

    projected: list[dict[str, Any]] = []
    for artifact in artifacts:
        if not artifact.get("authoritative"):
            continue

        artifact_id = str(artifact.get("artifact_id", "")).strip()
        if not artifact_id:
            continue

        projection_root = resolve_artifact_projection_root(
            artifact_id,
            repo_root=repo_root,
            workspace_root=workspace_root,
        )
        projection_root.mkdir(parents=True, exist_ok=True)
        payload_path = _write_json(projection_root / "artifact.json", artifact)
        metadata = {
            "artifact_id": artifact_id,
            "run_id": run_id,
            "artifact_type": artifact.get("artifact_type", "unknown"),
            "artifact_state": artifact.get("artifact_state", "unknown"),
            "artifact_freshness": artifact.get("artifact_freshness", "unknown"),
            "source_stage": artifact.get("source_stage", "unknown"),
            "source_ref": artifact.get("source_ref", ""),
            "projection_scope": "authoritative",
            "projection_path": str(projection_root),
        }
        metadata_path = _write_json(projection_root / "projection-metadata.json", metadata)
        projected.append(
            {
                "artifact_id": artifact_id,
                "projection_root": str(projection_root),
                "payload_path": str(payload_path),
                "metadata_path": str(metadata_path),
                "source_stage": metadata["source_stage"],
            }
        )

    return {
        "projected_count": len(projected),
        "items": projected,
    }


def build_retention_summary(
    run_id: str,
    close_decision: str,
    zone_paths: dict[str, Path],
    artifacts: list[dict[str, Any]],
    projections: dict[str, Any],
) -> dict[str, Any]:
    """Build explicit minimal retention and cleanup semantics for Slice 4."""

    deprecated_artifacts = [
        {
            "artifact_id": str(artifact.get("artifact_id", "")),
            "artifact_state": str(artifact.get("artifact_state", "")),
            "source_stage": str(artifact.get("source_stage", "unknown")),
            "reason": "deprecated artifact may be manually cleaned after close-run traceability review",
        }
        for artifact in artifacts
        if artifact.get("artifact_state") == "deprecated"
    ]
    is_closed_run = close_decision in {"close", "close_rejected"}
    cleanup_candidates = deprecated_artifacts if is_closed_run else []

    retained_projection_roots = [
        item["projection_root"]
        for item in projections.get("items", [])
    ]
    return {
        "run_id": run_id,
        "close_or_continue": close_decision,
        "retention_mode": "retain_for_continuation" if close_decision == "continue_pending" else "retain_for_traceability",
        "cleanup_mode": "manual_review_only",
        "retained_run_zones": {zone: str(zone_paths[zone]) for zone in RUN_TREE_ZONES},
        "retained_authoritative_projections": retained_projection_roots,
        "cleanup_eligible_artifacts": cleanup_candidates,
        "cleanup_actions": [],
        "policy_notes": [
            "Slice 4 does not perform automatic deletion of run-local or projected authoritative artifacts.",
            "Projected authoritative artifacts remain retained under SOURCE_DEV/workspace/atp-artifacts.",
            "Deprecated artifacts are only marked cleanup-eligible after close or close_rejected decisions.",
        ],
    }


def materialize_run_outputs(
    run_id: str,
    payloads: dict[str, Any],
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Materialize the approved ATP v0.2 run tree outputs."""

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
            _write_json(
                zone_paths["decisions"] / "exchange-boundary-decision.json",
                payloads["exchange_boundary_decision"],
            ),
        ],
        "handoff": [
            _write_json(zone_paths["handoff"] / "inline-context.json", payloads["handoff_outputs"]["inline_context"]),
            _write_json(zone_paths["handoff"] / "evidence-bundle.json", payloads["handoff_outputs"]["evidence_bundle"]),
            _write_json(
                zone_paths["handoff"] / "manifest-reference.json",
                payloads["handoff_outputs"]["manifest_reference"],
            ),
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
        "zones=" + ",".join(RUN_TREE_ZONES),
    ]
    for zone in RUN_TREE_ZONES:
        materialization_lines.append(f"{zone}={zone_paths[zone]}")
    for zone_name, files in created_files.items():
        for path in files:
            materialization_lines.append(f"file[{zone_name}]={path}")
    created_files["logs"].append(_write_log(zone_paths["logs"] / "materialization.log", materialization_lines))
    projections = project_authoritative_artifacts(
        run_id=run_id,
        artifacts=list(payloads["artifacts"]["items"]),
        repo_root=repo_root,
        workspace_root=workspace_root,
    )
    retention_summary = build_retention_summary(
        run_id=run_id,
        close_decision=str(payloads["close_or_continue"]["decision"]),
        zone_paths=zone_paths,
        artifacts=list(payloads["artifacts"]["items"]),
        projections=projections,
    )
    created_files["final"].append(_write_json(zone_paths["final"] / "retention-summary.json", retention_summary))
    created_files["logs"].append(
        _write_log(
            zone_paths["logs"] / "cleanup.log",
            [
                f"run_id={run_id}",
                f"close_or_continue={retention_summary['close_or_continue']}",
                f"cleanup_mode={retention_summary['cleanup_mode']}",
                f"cleanup_eligible_count={len(retention_summary['cleanup_eligible_artifacts'])}",
                f"cleanup_actions={len(retention_summary['cleanup_actions'])}",
                "authoritative_projections_retained=" + str(len(retention_summary["retained_authoritative_projections"])),
            ],
        )
    )
    for item in projections["items"]:
        materialization_lines.append(f"projection={item['projection_root']}")
        materialization_lines.append(f"projection-metadata={item['metadata_path']}")
        materialization_lines.append(f"projection-payload={item['payload_path']}")
    materialization_lines.append(
        f"retention-summary={zone_paths['final'] / 'retention-summary.json'}"
    )
    materialization_lines.append(f"cleanup-log={zone_paths['logs'] / 'cleanup.log'}")
    created_files["logs"][-1] = _write_log(zone_paths["logs"] / "materialization.log", materialization_lines)

    return {
        "workspace_root": str(zone_paths["workspace_root"]),
        "run_root": str(zone_paths["run_root"]),
        "zones": {zone: str(zone_paths[zone]) for zone in RUN_TREE_ZONES},
        "files": {zone: [str(path) for path in files] for zone, files in created_files.items()},
        "exchange_boundary": dict(payloads["exchange_boundary_decision"]),
        "authoritative_projection": projections,
        "retention": retention_summary,
    }
