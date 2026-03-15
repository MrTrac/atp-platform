"""ATP M1-M8 run preview CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from adapters.filesystem.artifact_store import (
    create_filtered_artifact,
    create_raw_artifact,
    mark_authoritative,
    mark_selected,
    summarize_artifacts,
)
from adapters.filesystem.workspace_writer import materialize_run_outputs
from core.approvals.approval_gate import require_approval
from core.approvals.decision_model import build_decision
from core.classification.classifier import classify_request
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.execution.executor import ExecutionError
from core.execution.orchestrator import execute_run
from core.finalization.close_or_continue import close_or_continue
from core.finalization.finalize import derive_final_status, finalize_run
from core.handoff.exchange_boundary import build_exchange_boundary_decision
from core.handoff.evidence_bundle import build_evidence_bundle
from core.handoff.exchange_bundle import build_exchange_bundle
from core.handoff.inline_context import build_inline_context
from core.handoff.manifest_reference import build_manifest_reference
from core.intake.loader import RequestLoadError, load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import (
    build_closure_continuation_state_contract,
    build_decision_to_closure_continuation_handoff_contract,
    build_finalization_closure_record_contract,
    build_gate_outcome_operational_followup_contract,
    build_review_approval_gate_contract,
    ProductResolutionError,
    build_post_execution_decision_contract,
    build_product_execution_preparation_contract,
    build_product_execution_result_contract,
    build_request_to_product_resolution_contract,
    build_resolution_to_handoff_intent_contract,
    resolve_product,
)
from core.routing.route_prepare import RoutePreparationError, prepare_route
from core.routing.route_select import RouteSelectionError, select_route
from core.state.decision_state import initial_decision_state
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state
from core.validation.validator import validate_artifacts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the ATP M1-M8 run flow.")
    parser.add_argument("request_file", help="Path to a JSON or YAML request file.")
    parser.add_argument("--run-id", default="run-preview-0001", help="Optional preview run identifier.")
    return parser


def _build_core_artifacts(
    request_id: str,
    product: str,
    task_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest_reference = task_manifest["manifest_id"]
    return [
        {"artifact_id": f"raw-request-{request_id}", "artifact_type": "request_raw", "artifact_freshness": "current", "authoritative": False, "manifest_reference": manifest_reference, "product": product},
        {"artifact_id": f"normalized-request-{request_id}", "artifact_type": "request_normalized", "artifact_freshness": "current", "authoritative": True, "manifest_reference": manifest_reference, "product": product},
        {"artifact_id": f"classification-{request_id}", "artifact_type": "classification", "artifact_freshness": "current", "authoritative": True, "manifest_reference": manifest_reference, "product": product},
        {"artifact_id": f"resolution-{request_id}", "artifact_type": "resolution", "artifact_freshness": "current", "authoritative": True, "manifest_reference": manifest_reference, "product": product},
        {"artifact_id": task_manifest["manifest_id"], "artifact_type": "task_manifest", "artifact_freshness": "current", "authoritative": True, "manifest_reference": manifest_reference, "product": product},
        {"artifact_id": f"product-context-{request_id}", "artifact_type": "product_context", "artifact_freshness": "current", "authoritative": True, "manifest_reference": manifest_reference, "product": product},
    ]


def _short_text(value: str, limit: int = 120) -> str:
    compact = value.replace("\n", "\\n")
    return compact[:limit]


def preview_run(
    request_file: str,
    run_id: str,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Load, normalize, classify, resolve, package context, route, execute, validate, review, approve, and finalize."""

    raw_request = load_request(request_file)
    normalized_request = normalize_request(raw_request)
    classification = classify_request(normalized_request)
    resolution = resolve_product(normalized_request, classification)
    task_manifest = build_task_manifest(normalized_request, classification, resolution)
    request_to_product_resolution = build_request_to_product_resolution_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        classification=classification,
        resolution=resolution,
        manifest_id=task_manifest["manifest_id"],
    )
    resolution_to_handoff_intent = build_resolution_to_handoff_intent_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        classification=classification,
        resolution_contract=request_to_product_resolution,
        manifest_id=task_manifest["manifest_id"],
    )
    product_context = build_product_context(resolution)
    evidence_selection = select_evidence(
        _build_core_artifacts(normalized_request["request_id"], resolution["product"], task_manifest)
    )
    evidence_bundle = materialize_bundle(
        request_id=normalized_request["request_id"],
        product=resolution["product"],
        evidence_selection=evidence_selection,
        manifest_reference=task_manifest["manifest_id"],
    )
    product_execution_preparation = build_product_execution_preparation_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        task_manifest=task_manifest,
        product_context=product_context,
        evidence_bundle=evidence_bundle,
    )
    prepared_route = prepare_route(
        normalized_request,
        classification,
        resolution,
        task_manifest,
        product_context,
        evidence_bundle,
    )
    routing_result = select_route(prepared_route)
    execution_result = execute_run(
        normalized_request=normalized_request,
        resolution=resolution,
        task_manifest=task_manifest,
        product_context=product_context,
        evidence_bundle=evidence_bundle,
        routing_result=routing_result,
    )

    raw_artifact = create_raw_artifact(execution_result)
    filtered_artifact = create_filtered_artifact(raw_artifact)
    selected_artifact = mark_selected(filtered_artifact)
    authoritative_artifact = mark_authoritative(selected_artifact)
    artifacts = [raw_artifact, filtered_artifact, selected_artifact, authoritative_artifact]
    artifact_summary = summarize_artifacts(artifacts)
    product_execution_result = build_product_execution_result_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        execution_preparation_contract=product_execution_preparation,
        execution_result=execution_result,
        artifact_summary=artifact_summary,
    )
    continuity_artifacts = [
        {"artifact_id": selected_artifact["artifact_id"], "artifact_type": selected_artifact["artifact_type"]}
    ]

    validation_summary = validate_artifacts(execution_result, artifacts)
    review_decision = build_decision(validation_summary)
    approval_result = require_approval(validation_summary, review_decision, artifact_summary)
    final_status = derive_final_status(approval_result)

    handoff_outputs = {
        "inline_context": build_inline_context(
            summary=f"{resolution['product']} completed ATP v0 flow",
            request_id=normalized_request["request_id"],
            product=resolution["product"],
            final_status=final_status,
            review_status=review_decision["review_status"],
            authoritative=True,
        ),
        "evidence_bundle": build_evidence_bundle(
            selected_artifacts=continuity_artifacts,
            request_id=normalized_request["request_id"],
            product=resolution["product"],
            bundle_id=f"handoff-evidence-{normalized_request['request_id']}",
            authoritative_refs=artifact_summary["authoritative_artifacts"],
            manifest_reference=task_manifest["manifest_id"],
        ),
        "exchange_bundle": build_exchange_bundle(
            artifacts=[artifact["artifact_id"] for artifact in artifacts],
            request_id=normalized_request["request_id"],
            provider=routing_result["selected_provider"],
            adapter=routing_result["execution_path"],
        ),
        "manifest_reference": build_manifest_reference(
            artifact_id=authoritative_artifact["artifact_id"],
            manifest_reference=task_manifest["manifest_id"],
            product=resolution["product"],
        ),
    }

    finalization_summary = finalize_run(
        execution_result=execution_result,
        artifact_summary=artifact_summary,
        validation_summary=validation_summary,
        review_decision=review_decision,
        approval_result=approval_result,
        handoff_outputs=handoff_outputs,
    )
    close_decision = close_or_continue(approval_result)
    post_execution_decision = build_post_execution_decision_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        execution_preparation_contract=product_execution_preparation,
        execution_result_contract=product_execution_result,
        review_decision=review_decision,
        approval_result=approval_result,
        close_decision=close_decision,
    )
    decision_to_closure_continuation_handoff = build_decision_to_closure_continuation_handoff_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        execution_preparation_contract=product_execution_preparation,
        execution_result_contract=product_execution_result,
        post_execution_decision_contract=post_execution_decision,
    )
    closure_continuation_state = build_closure_continuation_state_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        execution_preparation_contract=product_execution_preparation,
        execution_result_contract=product_execution_result,
        post_execution_decision_contract=post_execution_decision,
        decision_to_handoff_contract=decision_to_closure_continuation_handoff,
    )
    finalization_closure_record = build_finalization_closure_record_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        execution_result_contract=product_execution_result,
        post_execution_decision_contract=post_execution_decision,
        decision_to_handoff_contract=decision_to_closure_continuation_handoff,
        closure_continuation_state_contract=closure_continuation_state,
        finalization_summary=finalization_summary,
    )
    review_approval_gate = build_review_approval_gate_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        execution_result_contract=product_execution_result,
        post_execution_decision_contract=post_execution_decision,
        decision_to_handoff_contract=decision_to_closure_continuation_handoff,
        closure_continuation_state_contract=closure_continuation_state,
        finalization_closure_record_contract=finalization_closure_record,
        review_decision=review_decision,
        approval_result=approval_result,
    )
    gate_outcome_operational_followup = build_gate_outcome_operational_followup_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        finalization_closure_record_contract=finalization_closure_record,
        review_approval_gate_contract=review_approval_gate,
    )
    exchange_boundary_decision = build_exchange_boundary_decision(
        run_id=run_id,
        request_id=normalized_request["request_id"],
        close_decision=close_decision,
        handoff_outputs=handoff_outputs,
    )

    run_record = build_run_record(run_id=run_id, request_id=normalized_request["request_id"])
    run_record = advance_run_state(run_record, RunState.NORMALIZED, "request normalized")
    run_record = advance_run_state(run_record, RunState.CLASSIFIED, "request classified")
    run_record = advance_run_state(run_record, RunState.RESOLVED, "product resolved")
    run_record = advance_run_state(run_record, RunState.CONTEXT_PACKAGED, "context packaged")
    run_record = advance_run_state(run_record, RunState.ROUTED, "route selected")
    run_record = advance_run_state(run_record, RunState.EXECUTED, "execution completed")
    run_record = advance_run_state(run_record, RunState.VALIDATED, "validation summary created")
    run_record = advance_run_state(run_record, RunState.REVIEWED, "review decision created")
    if approval_result["approval_status"] == "approved":
        run_record = advance_run_state(run_record, RunState.APPROVED, "approval granted")
    run_record = advance_run_state(run_record, RunState.FINALIZED, "finalization summary created")
    if close_decision == "close":
        run_record = advance_run_state(run_record, RunState.CLOSED, "run closed")
    elif close_decision == "continue_pending":
        run_record = advance_run_state(run_record, RunState.CONTINUE_PENDING, "continuation pending")
    else:
        run_record = advance_run_state(run_record, RunState.CLOSED, "run closed as rejected")

    run_record["product"] = resolution["product"]
    run_record["resolution"] = {
        "repo_boundary": resolution["repo_boundary"],
        "profile_ref": resolution["profile_ref"],
        "policy_names": [policy["policy_name"] for policy in resolution["policies"]],
    }
    run_record["request_to_product_resolution"] = {
        "contract_id": request_to_product_resolution["contract_id"],
        "resolution_scope": request_to_product_resolution["resolution_scope"],
        "product_target": request_to_product_resolution["product_target"]["product"],
        "capability_target": request_to_product_resolution["capability_target"]["capability"],
    }
    run_record["resolution_to_handoff_intent"] = {
        "contract_id": resolution_to_handoff_intent["contract_id"],
        "handoff_scope": resolution_to_handoff_intent["handoff_scope"],
        "handoff_intent": resolution_to_handoff_intent["handoff_intent"]["intent"],
        "target_product": resolution_to_handoff_intent["handoff_intent"]["target_product"],
        "target_capability": resolution_to_handoff_intent["handoff_intent"]["target_capability"],
    }
    run_record["product_execution_preparation"] = {
        "contract_id": product_execution_preparation["contract_id"],
        "preparation_scope": product_execution_preparation["preparation_scope"],
        "preparation_mode": product_execution_preparation["execution_preparation"]["preparation_mode"],
        "task_manifest_id": product_execution_preparation["execution_preparation"]["task_manifest_id"],
        "evidence_bundle_id": product_execution_preparation["execution_preparation"]["evidence_bundle_id"],
    }
    run_record["product_execution_result"] = {
        "contract_id": product_execution_result["contract_id"],
        "result_scope": product_execution_result["result_scope"],
        "execution_id": product_execution_result["execution_result"]["execution_id"],
        "status": product_execution_result["execution_result"]["status"],
        "exit_code": product_execution_result["execution_result"]["exit_code"],
    }
    run_record["post_execution_decision"] = {
        "contract_id": post_execution_decision["contract_id"],
        "decision_scope": post_execution_decision["decision_scope"],
        "bounded_outcome": post_execution_decision["post_execution_decision"]["bounded_outcome"],
        "review_followup_action": post_execution_decision["post_execution_decision"]["review_followup_action"],
        "approval_status": post_execution_decision["post_execution_decision"]["approval_status"],
    }
    run_record["decision_to_closure_continuation_handoff"] = {
        "contract_id": decision_to_closure_continuation_handoff["contract_id"],
        "handoff_scope": decision_to_closure_continuation_handoff["handoff_scope"],
        "bounded_next_path": decision_to_closure_continuation_handoff["closure_or_continuation_handoff"][
            "bounded_next_path"
        ],
        "next_record_type": decision_to_closure_continuation_handoff["closure_or_continuation_handoff"][
            "next_record_type"
        ],
        "review_escalation_mode": decision_to_closure_continuation_handoff["closure_or_continuation_handoff"][
            "review_escalation_mode"
        ],
    }
    run_record["closure_continuation_state"] = {
        "contract_id": closure_continuation_state["contract_id"],
        "state_scope": closure_continuation_state["state_scope"],
        "bounded_path": closure_continuation_state["closure_or_continuation_state"]["bounded_path"],
        "state_status": closure_continuation_state["closure_or_continuation_state"]["state_status"],
        "continuation_required": closure_continuation_state["closure_or_continuation_state"]["continuation_required"],
    }
    run_record["finalization_closure_record"] = {
        "contract_id": finalization_closure_record["contract_id"],
        "record_scope": finalization_closure_record["record_scope"],
        "bounded_path": finalization_closure_record["finalization_or_closure_record"]["bounded_path"],
        "record_status": finalization_closure_record["finalization_or_closure_record"]["record_status"],
        "final_status": finalization_closure_record["finalization_or_closure_record"]["final_status"],
    }
    run_record["review_approval_gate"] = {
        "contract_id": review_approval_gate["contract_id"],
        "gate_scope": review_approval_gate["gate_scope"],
        "gate_decision": review_approval_gate["review_or_approval_gate"]["gate_decision"],
        "gate_status": review_approval_gate["review_or_approval_gate"]["gate_status"],
        "resulting_direction": review_approval_gate["review_or_approval_gate"]["resulting_direction"],
    }
    run_record["gate_outcome_operational_followup"] = {
        "contract_id": gate_outcome_operational_followup["contract_id"],
        "followup_scope": gate_outcome_operational_followup["followup_scope"],
        "bounded_followup": gate_outcome_operational_followup["gate_outcome_or_operational_followup"][
            "bounded_followup"
        ],
        "followup_status": gate_outcome_operational_followup["gate_outcome_or_operational_followup"][
            "followup_status"
        ],
        "continuity_signal": gate_outcome_operational_followup["gate_outcome_or_operational_followup"][
            "continuity_signal"
        ],
    }
    run_record["context_package"] = {
        "manifest_id": task_manifest["manifest_id"],
        "product_context_profile": product_context["profile_ref"],
        "selected_evidence_types": [artifact["artifact_type"] for artifact in evidence_selection["selected_artifacts"]],
        "evidence_bundle_id": evidence_bundle["bundle_id"],
    }
    run_record["routing"] = {
        "required_capabilities": routing_result["required_capabilities"],
        "selected_provider": routing_result["selected_provider"],
        "selected_node": routing_result["selected_node"],
        "reason_codes": routing_result["reason_codes"],
    }
    run_record["execution"] = {
        "execution_id": execution_result["execution_id"],
        "command": execution_result["command"],
        "exit_code": execution_result["exit_code"],
        "status": execution_result["status"],
    }
    run_record["artifacts"] = artifact_summary
    run_record["validation"] = validation_summary
    run_record["review"] = review_decision
    run_record["approval"] = approval_result
    run_record["finalization"] = finalization_summary
    run_record["close_or_continue"] = close_decision

    decision_state = initial_decision_state()
    materialization = materialize_run_outputs(
        run_id=run_id,
        workspace_root=workspace_root,
        payloads={
            "raw_request": raw_request,
            "normalized_request": normalized_request,
            "classification": classification,
            "resolution": resolution,
            "request_to_product_resolution": request_to_product_resolution,
            "resolution_to_handoff_intent": resolution_to_handoff_intent,
            "product_execution_preparation": product_execution_preparation,
            "product_execution_result": product_execution_result,
            "post_execution_decision": post_execution_decision,
            "decision_to_closure_continuation_handoff": decision_to_closure_continuation_handoff,
            "closure_continuation_state": closure_continuation_state,
            "finalization_closure_record": finalization_closure_record,
            "review_approval_gate": review_approval_gate,
            "gate_outcome_operational_followup": gate_outcome_operational_followup,
            "task_manifest": task_manifest,
            "product_context": product_context,
            "manifest_reference": handoff_outputs["manifest_reference"],
            "run_record": run_record,
            "prepared_route": prepared_route,
            "routing_result": routing_result,
            "execution_result": execution_result,
            "artifacts": {
                "items": artifacts,
                "summary": artifact_summary,
            },
            "validation_summary": validation_summary,
            "review_decision": review_decision,
            "approval_result": approval_result,
            "close_or_continue": {
                "run_id": run_id,
                "request_id": normalized_request["request_id"],
                "decision": close_decision,
            },
            "decision_state": decision_state,
            "exchange_boundary_decision": exchange_boundary_decision,
            "exchange_bundle": handoff_outputs["exchange_bundle"],
            "handoff_outputs": {
                "inline_context": handoff_outputs["inline_context"],
                "evidence_bundle": handoff_outputs["evidence_bundle"],
                "manifest_reference": handoff_outputs["manifest_reference"],
            },
            "finalization_summary": finalization_summary,
        },
    )
    exchange_boundary_decision = dict(materialization["exchange_boundary"])
    current_task_persistence = dict(materialization["current_task_persistence"])
    recovery_contract = dict(materialization["recovery_contract"])
    current_task_pointer = dict(materialization["current_task_pointer"])
    continuation_state = dict(materialization["continuation"])
    request_to_product_resolution_summary = dict(materialization["request_to_product_resolution"])
    resolution_to_handoff_intent_summary = dict(materialization["resolution_to_handoff_intent"])
    product_execution_preparation_summary = dict(materialization["product_execution_preparation"])
    product_execution_result_summary = dict(materialization["product_execution_result"])
    post_execution_decision_summary = dict(materialization["post_execution_decision"])
    decision_to_closure_continuation_handoff_summary = dict(
        materialization["decision_to_closure_continuation_handoff"]
    )
    closure_continuation_state_summary = dict(materialization["closure_continuation_state"])
    finalization_closure_record_summary = dict(materialization["finalization_closure_record"])
    review_approval_gate_summary = dict(materialization["review_approval_gate"])
    gate_outcome_operational_followup_summary = dict(materialization["gate_outcome_operational_followup"])

    return {
        "request": {
            "request_id": normalized_request["request_id"],
            "product": resolution["product"],
            "request_type": classification["request_type"],
            "execution_intent": classification["execution_intent"],
        },
        "classification": classification,
        "resolution": {
            "product": resolution["product"],
            "repo_boundary": resolution["repo_boundary"],
            "loaded_profile": resolution["profile_ref"],
            "loaded_policy_names": [policy["policy_name"] for policy in resolution["policies"]],
        },
        "request_to_product_resolution": {
            **request_to_product_resolution,
            "contract_path": request_to_product_resolution_summary["contract_path"],
        },
        "resolution_to_handoff_intent": {
            **resolution_to_handoff_intent,
            "contract_path": resolution_to_handoff_intent_summary["contract_path"],
        },
        "product_execution_preparation": {
            **product_execution_preparation,
            "contract_path": product_execution_preparation_summary["contract_path"],
        },
        "product_execution_result": {
            **product_execution_result,
            "contract_path": product_execution_result_summary["contract_path"],
        },
        "post_execution_decision": {
            **post_execution_decision,
            "contract_path": post_execution_decision_summary["contract_path"],
        },
        "decision_to_closure_continuation_handoff": {
            **decision_to_closure_continuation_handoff,
            "contract_path": decision_to_closure_continuation_handoff_summary["contract_path"],
        },
        "closure_continuation_state": {
            **closure_continuation_state,
            "contract_path": closure_continuation_state_summary["contract_path"],
        },
        "finalization_closure_record": {
            **finalization_closure_record,
            "contract_path": finalization_closure_record_summary["contract_path"],
        },
        "review_approval_gate": {
            **review_approval_gate,
            "contract_path": review_approval_gate_summary["contract_path"],
        },
        "gate_outcome_operational_followup": {
            **gate_outcome_operational_followup,
            "contract_path": gate_outcome_operational_followup_summary["contract_path"],
        },
        "context_package": {
            "task_manifest": task_manifest,
            "product_context": product_context,
            "evidence_selection": evidence_selection,
            "evidence_bundle": evidence_bundle,
        },
        "routing": {
            "prepared_route": prepared_route,
            "routing_result": routing_result,
        },
        "execution": {
            "execution_id": execution_result["execution_id"],
            "selected_provider": execution_result["selected_provider"],
            "selected_node": execution_result["selected_node"],
            "command": execution_result["command"],
            "exit_code": execution_result["exit_code"],
            "stdout_preview": _short_text(execution_result["stdout"]),
            "stderr_preview": _short_text(execution_result["stderr"]),
            "status": execution_result["status"],
        },
        "artifacts": {
            "items": artifacts,
            "summary": artifact_summary,
        },
        "validation": validation_summary,
        "review": review_decision,
        "approval": approval_result,
        "handoff": handoff_outputs,
        "exchange_boundary": exchange_boundary_decision,
        "current_task_persistence": current_task_persistence,
        "recovery_contract": recovery_contract,
        "current_task_pointer": current_task_pointer,
        "continuation": continuation_state,
        "reference_index": dict(materialization["reference_index"]),
        "finalization": finalization_summary,
        "close_or_continue": close_decision,
        "run": run_record,
        "decision_state": decision_state,
        "materialization": materialization,
        "message": "ATP v1.0 starts bounded review or approval gate recording. Approval UI and production workflow materialization are not implemented.",
    }


def main(argv: list[str] | None = None) -> int:
    """Run the ATP M1-M8 preview flow."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        preview = preview_run(args.request_file, args.run_id)
    except (
        RequestLoadError,
        ProductResolutionError,
        RoutePreparationError,
        RouteSelectionError,
        ExecutionError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc), "request_file": args.request_file},
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    print(json.dumps({"status": "preview", "summary": preview}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
