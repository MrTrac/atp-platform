"""Workspace materialization helpers for ATP v0.2-v0.7 foundational runtime slices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.handoff.continuation_state import build_continuation_state


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


def resolve_exchange_current_task_root(
    run_id: str,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> Path:
    """Resolve the minimal current-task exchange root for a run."""

    if not str(run_id).strip():
        raise ValueError("run_id is required for exchange materialization.")

    runtime_root = workspace_root.resolve() if workspace_root is not None else resolve_workspace_root(repo_root)
    return runtime_root / "exchange" / "current-task" / run_id


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


def summarize_request_to_product_resolution_contract(contract: dict[str, Any], contract_path: Path) -> dict[str, Any]:
    """Summarize the explicit v0.5 Slice A request-to-product contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "resolution_scope": str(contract.get("resolution_scope", "")),
        "product_target": str(contract.get("product_target", {}).get("product", "")),
        "capability_target": str(contract.get("capability_target", {}).get("capability", "")),
        "product_source": str(contract.get("resolution_rationale", {}).get("product_source", "")),
        "capability_source": str(contract.get("capability_target", {}).get("source", "")),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_resolution_to_handoff_intent_contract(contract: dict[str, Any], contract_path: Path) -> dict[str, Any]:
    """Summarize the explicit v0.5 Slice B resolution-to-handoff intent contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "handoff_scope": str(contract.get("handoff_scope", "")),
        "handoff_intent": str(contract.get("handoff_intent", {}).get("intent", "")),
        "target_product": str(contract.get("handoff_intent", {}).get("target_product", "")),
        "target_capability": str(contract.get("handoff_intent", {}).get("target_capability", "")),
        "resolution_contract_id": str(contract.get("request_to_product_resolution_ref", {}).get("contract_id", "")),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_product_execution_preparation_contract(contract: dict[str, Any], contract_path: Path) -> dict[str, Any]:
    """Summarize the explicit v0.5 Slice C product execution preparation contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "preparation_scope": str(contract.get("preparation_scope", "")),
        "preparation_mode": str(contract.get("execution_preparation", {}).get("preparation_mode", "")),
        "target_product": str(contract.get("execution_preparation", {}).get("target_product", "")),
        "target_capability": str(contract.get("execution_preparation", {}).get("target_capability", "")),
        "resolution_contract_id": str(contract.get("request_to_product_resolution_ref", {}).get("contract_id", "")),
        "handoff_intent_contract_id": str(contract.get("resolution_to_handoff_intent_ref", {}).get("contract_id", "")),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_product_execution_result_contract(contract: dict[str, Any], contract_path: Path) -> dict[str, Any]:
    """Summarize the explicit v0.5 Slice D product execution result contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "result_scope": str(contract.get("result_scope", "")),
        "execution_id": str(contract.get("execution_result", {}).get("execution_id", "")),
        "status": str(contract.get("execution_result", {}).get("status", "")),
        "exit_code": int(contract.get("execution_result", {}).get("exit_code", -1)),
        "execution_preparation_contract_id": str(contract.get("product_execution_preparation_ref", {}).get("contract_id", "")),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_post_execution_decision_contract(contract: dict[str, Any], contract_path: Path) -> dict[str, Any]:
    """Summarize the explicit v0.6 Slice A post-execution decision contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "decision_scope": str(contract.get("decision_scope", "")),
        "bounded_outcome": str(contract.get("post_execution_decision", {}).get("bounded_outcome", "")),
        "review_followup_action": str(contract.get("post_execution_decision", {}).get("review_followup_action", "")),
        "execution_result_contract_id": str(contract.get("product_execution_result_ref", {}).get("contract_id", "")),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_decision_to_closure_continuation_handoff_contract(
    contract: dict[str, Any],
    contract_path: Path,
) -> dict[str, Any]:
    """Summarize the explicit v0.6 Slice B decision-to-handoff contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "handoff_scope": str(contract.get("handoff_scope", "")),
        "bounded_next_path": str(
            contract.get("closure_or_continuation_handoff", {}).get("bounded_next_path", "")
        ),
        "next_record_type": str(
            contract.get("closure_or_continuation_handoff", {}).get("next_record_type", "")
        ),
        "review_escalation_mode": str(
            contract.get("closure_or_continuation_handoff", {}).get("review_escalation_mode", "")
        ),
        "post_execution_decision_contract_id": str(
            contract.get("post_execution_decision_ref", {}).get("contract_id", "")
        ),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_closure_continuation_state_contract(
    contract: dict[str, Any],
    contract_path: Path,
) -> dict[str, Any]:
    """Summarize the explicit v0.6 Slice C closure/continuation state contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "state_scope": str(contract.get("state_scope", "")),
        "bounded_path": str(contract.get("closure_or_continuation_state", {}).get("bounded_path", "")),
        "state_status": str(contract.get("closure_or_continuation_state", {}).get("state_status", "")),
        "continuation_required": bool(
            contract.get("closure_or_continuation_state", {}).get("continuation_required", False)
        ),
        "decision_to_handoff_contract_id": str(
            contract.get("decision_to_closure_continuation_handoff_ref", {}).get("contract_id", "")
        ),
        "traceability": dict(contract.get("traceability", {})),
    }


def summarize_finalization_closure_record_contract(
    contract: dict[str, Any],
    contract_path: Path,
) -> dict[str, Any]:
    """Summarize the explicit v0.7 Slice A finalization/closure record contract."""

    return {
        "contract_id": str(contract.get("contract_id", "")),
        "contract_path": str(contract_path),
        "record_scope": str(contract.get("record_scope", "")),
        "bounded_path": str(contract.get("finalization_or_closure_record", {}).get("bounded_path", "")),
        "record_status": str(contract.get("finalization_or_closure_record", {}).get("record_status", "")),
        "final_status": str(contract.get("finalization_or_closure_record", {}).get("final_status", "")),
        "closure_continuation_state_contract_id": str(
            contract.get("closure_continuation_state_ref", {}).get("contract_id", "")
        ),
        "traceability": dict(contract.get("traceability", {})),
    }


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


def materialize_exchange_boundary(
    run_id: str,
    exchange_boundary_decision: dict[str, Any],
    exchange_bundle: dict[str, Any],
    handoff_outputs: dict[str, Any],
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Materialize the minimal external exchange payload only when required."""

    decision = dict(exchange_boundary_decision)
    if not decision.get("requires_exchange_boundary"):
        decision["exchange_materialization_status"] = "not_required"
        return {
            "materialized": False,
            "exchange_root": "",
            "files": [],
            "decision": decision,
        }

    exchange_root = resolve_exchange_current_task_root(
        run_id,
        repo_root=repo_root,
        workspace_root=workspace_root,
    )
    exchange_root.mkdir(parents=True, exist_ok=True)
    metadata = {
        "run_id": run_id,
        "request_id": decision.get("request_id", ""),
        "decision_id": decision.get("decision_id", ""),
        "boundary_mode": decision.get("boundary_mode", ""),
        "source_manifest_reference": handoff_outputs.get("manifest_reference", {}).get("manifest_reference", ""),
        "source_evidence_bundle_id": handoff_outputs.get("evidence_bundle", {}).get("bundle_id", ""),
        "source_exchange_bundle_id": exchange_bundle.get("exchange_id", ""),
        "source_handoff_type": exchange_bundle.get("handoff_type", ""),
    }
    bundle_path = _write_json(exchange_root / "exchange-bundle.json", exchange_bundle)
    metadata_path = _write_json(exchange_root / "exchange-metadata.json", metadata)
    decision["exchange_materialization_status"] = "materialized_current_task"
    return {
        "materialized": True,
        "exchange_root": str(exchange_root),
        "files": [str(bundle_path), str(metadata_path)],
        "bundle_path": str(bundle_path),
        "metadata_path": str(metadata_path),
        "decision": decision,
    }


def build_reference_index(
    run_id: str,
    request_id: str,
    close_decision: str,
    zone_paths: dict[str, Path],
    exchange_boundary_decision: dict[str, Any],
    exchange_summary: dict[str, Any],
    continuation_state: dict[str, Any],
    manifest_reference: dict[str, Any],
    projections: dict[str, Any],
) -> dict[str, Any]:
    """Build the minimal file-based reference/index artifact for Slice D."""

    return {
        "index_id": f"reference-index-{run_id}",
        "run_id": run_id,
        "request_id": request_id,
        "close_or_continue": close_decision,
        "exchange_boundary_decision_id": exchange_boundary_decision.get("decision_id", ""),
        "exchange_boundary_mode": exchange_boundary_decision.get("boundary_mode", ""),
        "manifest_reference": {
            "value": manifest_reference.get("manifest_reference", ""),
            "manifests_path": str(zone_paths["manifests"] / "manifest-reference.json"),
            "handoff_path": str(zone_paths["handoff"] / "manifest-reference.json"),
        },
        "continuation": {
            "continuation_id": continuation_state.get("continuation_id", ""),
            "continuation_required": continuation_state.get("continuation_required", False),
            "current_source": continuation_state.get("current_source", "none"),
            "state_path": str(zone_paths["final"] / "continuation-state.json"),
        },
        "exchange_current_task": {
            "materialized": exchange_summary.get("materialized", False),
            "exchange_root": exchange_summary.get("exchange_root", ""),
            "bundle_path": exchange_summary.get("bundle_path", ""),
            "metadata_path": exchange_summary.get("metadata_path", ""),
            "current_reference_path": exchange_summary.get("current_reference_path", ""),
        },
        "authoritative_refs": [
            {
                "artifact_id": item.get("artifact_id", ""),
                "projection_root": item.get("projection_root", ""),
                "metadata_path": item.get("metadata_path", ""),
            }
            for item in projections.get("items", [])
        ],
        "notes": [
            "Slice D provides minimal file-based references only.",
            "This is not a generalized index, catalog, or persistence subsystem.",
        ],
    }


def materialize_current_exchange_reference(
    run_id: str,
    request_id: str,
    exchange_boundary_decision: dict[str, Any],
    exchange_summary: dict[str, Any],
    continuation_state_path: Path,
    reference_index_path: Path,
    manifest_reference: dict[str, Any],
) -> dict[str, Any]:
    """Write the minimal current-task exchange pointer only when exchange exists."""

    if not exchange_summary.get("materialized"):
        return {
            "materialized": False,
            "current_reference_path": "",
        }

    current_reference_path = Path(str(exchange_summary["exchange_root"])) / "current.json"
    payload = {
        "run_id": run_id,
        "request_id": request_id,
        "exchange_boundary_decision_id": exchange_boundary_decision.get("decision_id", ""),
        "exchange_boundary_mode": exchange_boundary_decision.get("boundary_mode", ""),
        "exchange_root": exchange_summary.get("exchange_root", ""),
        "exchange_bundle_path": exchange_summary.get("bundle_path", ""),
        "exchange_metadata_path": exchange_summary.get("metadata_path", ""),
        "continuation_state_path": str(continuation_state_path),
        "reference_index_path": str(reference_index_path),
        "manifest_reference": manifest_reference.get("manifest_reference", ""),
    }
    _write_json(current_reference_path, payload)
    return {
        "materialized": True,
        "current_reference_path": str(current_reference_path),
    }


def materialize_current_task_persistence_contract(
    run_id: str,
    request_id: str,
    close_decision: str,
    exchange_boundary_decision: dict[str, Any],
    exchange_summary: dict[str, Any],
    continuation_state: dict[str, Any],
    continuation_state_path: Path,
    reference_index_path: Path,
    manifest_reference: dict[str, Any],
) -> dict[str, Any]:
    """Write the minimal file-based current-task persistence contract for Slice A."""

    if not exchange_summary.get("materialized"):
        return {
            "persisted": False,
            "persistence_scope": "not_applicable",
            "persistence_state_path": "",
            "current_task_id": "",
        }

    persistence_state_path = Path(str(exchange_summary["exchange_root"])) / "current-task-state.json"
    payload = {
        "current_task_id": f"current-task-{run_id}",
        "run_id": run_id,
        "request_id": request_id,
        "close_or_continue": close_decision,
        "persistence_mode": "file_based",
        "persistence_scope": "workspace_exchange_current_task",
        "exchange_boundary_decision_id": exchange_boundary_decision.get("decision_id", ""),
        "exchange_boundary_mode": exchange_boundary_decision.get("boundary_mode", ""),
        "exchange_materialization_status": exchange_boundary_decision.get("exchange_materialization_status", ""),
        "current_task_root": exchange_summary.get("exchange_root", ""),
        "current_reference_path": exchange_summary.get("current_reference_path", ""),
        "exchange_bundle_path": exchange_summary.get("bundle_path", ""),
        "exchange_metadata_path": exchange_summary.get("metadata_path", ""),
        "continuation_required": continuation_state.get("continuation_required", False),
        "continuation_state_path": str(continuation_state_path),
        "reference_index_path": str(reference_index_path),
        "manifest_reference": manifest_reference.get("manifest_reference", ""),
        "notes": [
            "Slice A persists only the current-task contract for the originating run.",
            "This is not a recovery engine, scheduler, or generalized persistence subsystem.",
        ],
    }
    _write_json(persistence_state_path, payload)
    return {
        "persisted": True,
        "persistence_mode": payload["persistence_mode"],
        "persistence_scope": payload["persistence_scope"],
        "persistence_state_path": str(persistence_state_path),
        "current_task_id": payload["current_task_id"],
    }


def materialize_continue_pending_recovery_contract(
    run_id: str,
    request_id: str,
    close_decision: str,
    exchange_boundary_decision: dict[str, Any],
    exchange_summary: dict[str, Any],
    continuation_state: dict[str, Any],
    current_task_persistence: dict[str, Any],
    continuation_state_path: Path,
    reference_index_path: Path,
) -> dict[str, Any]:
    """Write the minimal file-based recovery contract for continue_pending."""

    if close_decision != "continue_pending" or not current_task_persistence.get("persisted"):
        return {
            "recovery_ready": False,
            "recovery_contract_path": "",
            "recovery_entry_mode": "not_applicable",
        }

    recovery_contract_path = Path(str(exchange_summary["exchange_root"])) / "continue-pending-recovery.json"
    payload = {
        "recovery_contract_id": f"continue-pending-recovery-{run_id}",
        "run_id": run_id,
        "request_id": request_id,
        "close_or_continue": close_decision,
        "recovery_entry_mode": "manual_file_based",
        "recovery_scope": "continue_pending_current_task",
        "current_task_id": current_task_persistence.get("current_task_id", ""),
        "current_task_persistence_state_path": current_task_persistence.get("persistence_state_path", ""),
        "continuation_id": continuation_state.get("continuation_id", ""),
        "continuation_state_path": str(continuation_state_path),
        "continuity_status": continuation_state.get("continuity_status", ""),
        "exchange_boundary_decision_id": exchange_boundary_decision.get("decision_id", ""),
        "exchange_boundary_mode": exchange_boundary_decision.get("boundary_mode", ""),
        "exchange_root": exchange_summary.get("exchange_root", ""),
        "exchange_bundle_path": exchange_summary.get("bundle_path", ""),
        "exchange_metadata_path": exchange_summary.get("metadata_path", ""),
        "current_reference_path": exchange_summary.get("current_reference_path", ""),
        "reference_index_path": str(reference_index_path),
        "notes": [
            "Slice B defines only the recovery entry contract for continue_pending.",
            "No resume execution, scheduler, queue, or generalized recovery engine is introduced.",
        ],
    }
    _write_json(recovery_contract_path, payload)
    return {
        "recovery_ready": True,
        "recovery_entry_mode": payload["recovery_entry_mode"],
        "recovery_scope": payload["recovery_scope"],
        "recovery_contract_path": str(recovery_contract_path),
        "recovery_contract_id": payload["recovery_contract_id"],
    }


def materialize_current_task_pointer_traceability(
    run_id: str,
    exchange_summary: dict[str, Any],
    current_task_persistence: dict[str, Any],
    recovery_contract: dict[str, Any],
) -> dict[str, Any]:
    """Write the minimal active pointer and supersede traceability artifacts for Slice C."""

    if not current_task_persistence.get("persisted"):
        return {
            "active_pointer_written": False,
            "active_pointer_path": "",
            "superseded_previous": False,
            "supersede_trace_path": "",
        }

    exchange_root = Path(str(exchange_summary["exchange_root"]))
    current_task_root = exchange_root.parent
    active_pointer_path = current_task_root / "active-pointer.json"
    previous_pointer: dict[str, Any] = {}
    if active_pointer_path.exists():
        previous_pointer = json.loads(active_pointer_path.read_text(encoding="utf-8"))

    superseded_previous = bool(previous_pointer) and previous_pointer.get("run_id") != run_id
    supersede_trace_path = exchange_root / "supersede-trace.json"
    if superseded_previous:
        supersede_payload = {
            "run_id": run_id,
            "supersede_mode": "replace_active_pointer",
            "active_pointer_path": str(active_pointer_path),
            "previous_run_id": previous_pointer.get("run_id", ""),
            "previous_current_task_id": previous_pointer.get("current_task_id", ""),
            "previous_current_task_state_path": previous_pointer.get("current_task_persistence_state_path", ""),
            "previous_recovery_contract_path": previous_pointer.get("recovery_contract_path", ""),
            "previous_current_reference_path": previous_pointer.get("current_reference_path", ""),
            "previous_exchange_root": previous_pointer.get("exchange_root", ""),
        }
        _write_json(supersede_trace_path, supersede_payload)

    active_pointer_payload = {
        "pointer_id": "current-task-active-pointer",
        "pointer_mode": "active_current_task",
        "run_id": run_id,
        "exchange_root": str(exchange_root),
        "current_task_id": current_task_persistence.get("current_task_id", ""),
        "current_task_persistence_state_path": current_task_persistence.get("persistence_state_path", ""),
        "recovery_contract_path": recovery_contract.get("recovery_contract_path", ""),
        "current_reference_path": exchange_summary.get("current_reference_path", ""),
        "superseded_previous": superseded_previous,
        "supersede_trace_path": str(supersede_trace_path) if superseded_previous else "",
    }
    _write_json(active_pointer_path, active_pointer_payload)
    return {
        "active_pointer_written": True,
        "active_pointer_path": str(active_pointer_path),
        "superseded_previous": superseded_previous,
        "supersede_trace_path": str(supersede_trace_path) if superseded_previous else "",
    }


def materialize_run_outputs(
    run_id: str,
    payloads: dict[str, Any],
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Materialize the approved ATP v0.2-v0.7 foundational run outputs."""

    zone_paths = materialize_run_tree(run_id, repo_root=repo_root, workspace_root=workspace_root)
    exchange_summary = materialize_exchange_boundary(
        run_id=run_id,
        exchange_boundary_decision=payloads["exchange_boundary_decision"],
        exchange_bundle=payloads["exchange_bundle"],
        handoff_outputs=payloads["handoff_outputs"],
        repo_root=repo_root,
        workspace_root=workspace_root,
    )
    exchange_boundary_decision = exchange_summary["decision"]
    request_id = str(
        payloads.get("close_or_continue", {}).get("request_id")
        or payloads.get("run_record", {}).get("request_id")
        or payloads.get("raw_request", {}).get("request_id")
        or "request-unknown"
    )
    continuation_state = build_continuation_state(
        run_id=run_id,
        request_id=request_id,
        close_decision=str(payloads["close_or_continue"]["decision"]),
        exchange_boundary_decision=exchange_boundary_decision,
        exchange_summary=exchange_summary,
        handoff_outputs={
            **payloads["handoff_outputs"],
            "exchange_bundle": payloads["exchange_bundle"],
        },
    )
    resolution_contract_path = zone_paths["manifests"] / "request-to-product-resolution-contract.json"
    handoff_intent_contract_path = zone_paths["manifests"] / "resolution-to-handoff-intent-contract.json"
    execution_preparation_contract_path = zone_paths["manifests"] / "product-execution-preparation-contract.json"
    execution_result_contract_path = zone_paths["manifests"] / "product-execution-result-contract.json"
    post_execution_decision_contract_path = zone_paths["manifests"] / "post-execution-decision-contract.json"
    decision_to_handoff_contract_path = (
        zone_paths["manifests"] / "decision-to-closure-continuation-handoff-contract.json"
    )
    closure_continuation_state_contract_path = (
        zone_paths["manifests"] / "closure-continuation-state-contract.json"
    )
    finalization_closure_record_contract_path = (
        zone_paths["manifests"] / "finalization-closure-record-contract.json"
    )
    created_files = {
        "request": [
            _write_json(zone_paths["request"] / "request.raw.json", payloads["raw_request"]),
            _write_json(zone_paths["request"] / "request.normalized.json", payloads["normalized_request"]),
            _write_json(zone_paths["request"] / "classification.json", payloads["classification"]),
        ],
        "manifests": [
            _write_json(zone_paths["manifests"] / "resolution.json", payloads["resolution"]),
            _write_json(resolution_contract_path, payloads["request_to_product_resolution"]),
            _write_json(handoff_intent_contract_path, payloads["resolution_to_handoff_intent"]),
            _write_json(execution_preparation_contract_path, payloads["product_execution_preparation"]),
            _write_json(execution_result_contract_path, payloads["product_execution_result"]),
            _write_json(post_execution_decision_contract_path, payloads["post_execution_decision"]),
            _write_json(
                decision_to_handoff_contract_path,
                payloads["decision_to_closure_continuation_handoff"],
            ),
            _write_json(
                closure_continuation_state_contract_path,
                payloads["closure_continuation_state"],
            ),
            _write_json(
                finalization_closure_record_contract_path,
                payloads["finalization_closure_record"],
            ),
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
                exchange_boundary_decision,
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
            _write_json(zone_paths["final"] / "continuation-state.json", continuation_state),
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
    reference_index_path = zone_paths["final"] / "reference-index.json"
    continuation_state_path = zone_paths["final"] / "continuation-state.json"
    current_exchange_reference = materialize_current_exchange_reference(
        run_id=run_id,
        request_id=request_id,
        exchange_boundary_decision=exchange_boundary_decision,
        exchange_summary=exchange_summary,
        continuation_state_path=continuation_state_path,
        reference_index_path=reference_index_path,
        manifest_reference=payloads["handoff_outputs"]["manifest_reference"],
    )
    exchange_summary["current_reference_path"] = current_exchange_reference.get("current_reference_path", "")
    reference_index = build_reference_index(
        run_id=run_id,
        request_id=request_id,
        close_decision=str(payloads["close_or_continue"]["decision"]),
        zone_paths=zone_paths,
        exchange_boundary_decision=exchange_boundary_decision,
        exchange_summary=exchange_summary,
        continuation_state=continuation_state,
        manifest_reference=payloads["handoff_outputs"]["manifest_reference"],
        projections=projections,
    )
    current_task_persistence = materialize_current_task_persistence_contract(
        run_id=run_id,
        request_id=request_id,
        close_decision=str(payloads["close_or_continue"]["decision"]),
        exchange_boundary_decision=exchange_boundary_decision,
        exchange_summary=exchange_summary,
        continuation_state=continuation_state,
        continuation_state_path=continuation_state_path,
        reference_index_path=reference_index_path,
        manifest_reference=payloads["handoff_outputs"]["manifest_reference"],
    )
    exchange_summary["current_task_persistence"] = current_task_persistence
    reference_index["exchange_current_task"]["persistence_state_path"] = current_task_persistence.get(
        "persistence_state_path",
        "",
    )
    recovery_contract = materialize_continue_pending_recovery_contract(
        run_id=run_id,
        request_id=request_id,
        close_decision=str(payloads["close_or_continue"]["decision"]),
        exchange_boundary_decision=exchange_boundary_decision,
        exchange_summary=exchange_summary,
        continuation_state=continuation_state,
        current_task_persistence=current_task_persistence,
        continuation_state_path=continuation_state_path,
        reference_index_path=reference_index_path,
    )
    exchange_summary["recovery_contract"] = recovery_contract
    current_task_pointer = materialize_current_task_pointer_traceability(
        run_id=run_id,
        exchange_summary=exchange_summary,
        current_task_persistence=current_task_persistence,
        recovery_contract=recovery_contract,
    )
    exchange_summary["current_task_pointer"] = current_task_pointer
    reference_index["continuation"]["recovery_contract_path"] = recovery_contract.get("recovery_contract_path", "")
    reference_index["exchange_current_task"]["active_pointer_path"] = current_task_pointer.get("active_pointer_path", "")
    reference_index["exchange_current_task"]["supersede_trace_path"] = current_task_pointer.get(
        "supersede_trace_path",
        "",
    )
    created_files["final"].append(_write_json(reference_index_path, reference_index))
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
    if exchange_summary["materialized"]:
        materialization_lines.append(f"exchange={exchange_summary['exchange_root']}")
        for path in exchange_summary["files"]:
            materialization_lines.append(f"exchange-file={path}")
    if current_exchange_reference["materialized"]:
        materialization_lines.append(f"exchange-current-reference={current_exchange_reference['current_reference_path']}")
    if current_task_persistence["persisted"]:
        materialization_lines.append(f"current-task-state={current_task_persistence['persistence_state_path']}")
    if recovery_contract["recovery_ready"]:
        materialization_lines.append(f"continue-pending-recovery={recovery_contract['recovery_contract_path']}")
    if current_task_pointer["active_pointer_written"]:
        materialization_lines.append(f"active-pointer={current_task_pointer['active_pointer_path']}")
    if current_task_pointer["superseded_previous"]:
        materialization_lines.append(f"supersede-trace={current_task_pointer['supersede_trace_path']}")
    materialization_lines.append(
        f"retention-summary={zone_paths['final'] / 'retention-summary.json'}"
    )
    materialization_lines.append(
        f"continuation-state={zone_paths['final'] / 'continuation-state.json'}"
    )
    materialization_lines.append(f"reference-index={reference_index_path}")
    materialization_lines.append(f"cleanup-log={zone_paths['logs'] / 'cleanup.log'}")
    created_files["logs"][-1] = _write_log(zone_paths["logs"] / "materialization.log", materialization_lines)
    request_to_product_resolution_summary = summarize_request_to_product_resolution_contract(
        payloads["request_to_product_resolution"],
        resolution_contract_path,
    )
    resolution_to_handoff_intent_summary = summarize_resolution_to_handoff_intent_contract(
        payloads["resolution_to_handoff_intent"],
        handoff_intent_contract_path,
    )
    product_execution_preparation_summary = summarize_product_execution_preparation_contract(
        payloads["product_execution_preparation"],
        execution_preparation_contract_path,
    )
    product_execution_result_summary = summarize_product_execution_result_contract(
        payloads["product_execution_result"],
        execution_result_contract_path,
    )
    post_execution_decision_summary = summarize_post_execution_decision_contract(
        payloads["post_execution_decision"],
        post_execution_decision_contract_path,
    )
    decision_to_closure_continuation_handoff_summary = (
        summarize_decision_to_closure_continuation_handoff_contract(
            payloads["decision_to_closure_continuation_handoff"],
            decision_to_handoff_contract_path,
        )
    )
    closure_continuation_state_summary = summarize_closure_continuation_state_contract(
        payloads["closure_continuation_state"],
        closure_continuation_state_contract_path,
    )
    finalization_closure_record_summary = summarize_finalization_closure_record_contract(
        payloads["finalization_closure_record"],
        finalization_closure_record_contract_path,
    )

    return {
        "workspace_root": str(zone_paths["workspace_root"]),
        "run_root": str(zone_paths["run_root"]),
        "zones": {zone: str(zone_paths[zone]) for zone in RUN_TREE_ZONES},
        "files": {zone: [str(path) for path in files] for zone, files in created_files.items()},
        "exchange_boundary": exchange_boundary_decision,
        "exchange": exchange_summary,
        "current_task_persistence": current_task_persistence,
        "recovery_contract": recovery_contract,
        "current_task_pointer": current_task_pointer,
        "continuation": continuation_state,
        "request_to_product_resolution": request_to_product_resolution_summary,
        "resolution_to_handoff_intent": resolution_to_handoff_intent_summary,
        "product_execution_preparation": product_execution_preparation_summary,
        "product_execution_result": product_execution_result_summary,
        "post_execution_decision": post_execution_decision_summary,
        "decision_to_closure_continuation_handoff": decision_to_closure_continuation_handoff_summary,
        "closure_continuation_state": closure_continuation_state_summary,
        "finalization_closure_record": finalization_closure_record_summary,
        "reference_index": reference_index,
        "authoritative_projection": projections,
        "retention": retention_summary,
    }
