"""Bounded output-contract helpers for ATP request-chain CLIs."""

from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any


_PREFERRED_KEY_ORDER = [
    "command",
    "status",
    "request_file",
    "request_files",
    "run_id",
    "review_summary",
    "summary",
    "multi_request_summary",
    "error_stage",
    "error_kind",
    "failed_request_file",
    "failed_request_index",
    "processed_request_count",
    "error",
    "next_step",
    "validation_evidence_summary",
    "multi_request_id",
    "processing_mode",
    "ordering_basis",
    "request_count",
    "accepted_request_count",
    "request_ids",
    "flow_ids",
    "request_flows",
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "bundle_id",
    "bundle_type",
    "bundle_version",
    "package_id",
    "package_type",
    "package_version",
    "product",
    "request_id",
    "flow_id",
    "flow_status",
    "bundle_status",
    "artifact_status",
    "supported_flow",
    "notes",
    "validation_summary",
    "normalized_task",
    "single_ai_execution_package",
    "task_manifest",
    "reviewable_output_bundle",
    "one_shot_ai_ready_artifact",
    "manifest_id",
    "preparation_contract_id",
    "task_manifest_id",
    "task_id",
    "task_type",
    "task_goal",
    "execution_intent",
    "request_type",
    "required_capabilities",
    "request_identity",
    "normalized_task_summary",
    "task_summary",
    "scope_and_constraints",
    "single_ai_package_payload",
    "result_status",
    "completion_signal",
    "quick_status",
    "readiness_checklist",
    "confidence_summary",
    "chain_trace_summary",
    "review_evidence_summary",
    "acceptance_evidence_hint",
    "review_sequence_summary",
    "progression_governance_summary",
    "acceptance_discipline_summary",
    "primary_artifact",
    "primary_review_target",
    "handoff_target",
    "next_bounded_action",
    "review_first",
    "manual_handoff_summary",
    "review_to_handoff_bridge",
    "handoff_surface",
    "review_sections",
    "review_surface",
    "target_mode",
    "usage_mode",
    "handoff_notes",
    "prompt_sections",
    "prompt_text",
    "traceability",
    "instructions",
    "input_artifacts",
    "target_scope",
    "request_scope",
    "request_constraints",
    "request_policy_context",
    "human_readable_sections",
    "review_notes",
    "invalid_or_out_of_scope",
    "request_shape",
    "supported_scope",
]
_PREFERRED_KEY_INDEX = {key: index for index, key in enumerate(_PREFERRED_KEY_ORDER)}
_MULTI_REQUEST_SUMMARY_ORDER = [
    "multi_request_id",
    "processing_mode",
    "ordering_basis",
    "request_count",
    "accepted_request_count",
    "supported_flow",
    "notes",
    "request_ids",
    "flow_ids",
    "request_flows",
]


def _sort_key(key: str) -> tuple[int, str]:
    return (_PREFERRED_KEY_INDEX.get(key, len(_PREFERRED_KEY_ORDER)), key)


def order_for_operator_review(value: Any) -> Any:
    """Return a recursively ordered structure with deterministic human-review shape."""

    if isinstance(value, dict):
        ordered = OrderedDict()
        for key in sorted(value.keys(), key=_sort_key):
            ordered[key] = order_for_operator_review(value[key])
        return ordered
    if isinstance(value, list):
        return [order_for_operator_review(item) for item in value]
    return value


def _order_mapping_with_explicit_keys(
    value: dict[str, Any],
    key_order: list[str],
) -> OrderedDict[str, Any]:
    ordered = OrderedDict()
    for key in key_order:
        if key in value:
            ordered[key] = order_for_operator_review(value[key])
    for key in value.keys():
        if key not in ordered:
            ordered[key] = order_for_operator_review(value[key])
    return ordered


def build_success_envelope(
    *,
    command: str,
    request_file: str,
    run_id: str,
    summary: dict[str, Any],
) -> OrderedDict[str, Any]:
    review_summary = build_review_summary(command=command, request_file=request_file, run_id=run_id, summary=summary)
    return order_for_operator_review(
        {
            "command": command,
            "status": "ok",
            "request_file": request_file,
            "run_id": run_id,
            "review_summary": review_summary,
            "summary": summary,
        }
    )


def build_error_envelope(
    *,
    command: str,
    request_file: str,
    run_id: str,
    error: str,
    error_stage: str | None = None,
    error_kind: str | None = None,
    next_step: str | None = None,
) -> OrderedDict[str, Any]:
    payload: dict[str, Any] = {
        "command": command,
        "status": "error",
        "request_file": request_file,
        "run_id": run_id,
        "error": error,
    }
    if error_stage is not None:
        payload["error_stage"] = error_stage
    if error_kind is not None:
        payload["error_kind"] = error_kind
    if next_step is not None:
        payload["next_step"] = next_step
    if error_stage is not None and error_kind is not None:
        payload["validation_evidence_summary"] = {
            "failed_command": command,
            "failed_stage": error_stage,
            "failed_kind": error_kind,
            "bounded_scope_preserved": True,
            "canonical_recheck_command": (
                f"./atp {command} tests/fixtures/requests/sample_request_slice02.yaml"
            ),
        }
    return order_for_operator_review(payload)


def build_multi_request_success_envelope(
    *,
    command: str,
    request_files: list[str],
    run_id: str,
    multi_request_summary: dict[str, Any],
) -> OrderedDict[str, Any]:
    return OrderedDict(
        [
            ("command", command),
            ("status", "ok"),
            ("request_files", order_for_operator_review(request_files)),
            ("run_id", run_id),
            (
                "multi_request_summary",
                _order_mapping_with_explicit_keys(
                    multi_request_summary,
                    _MULTI_REQUEST_SUMMARY_ORDER,
                ),
            ),
        ]
    )


def build_multi_request_error_envelope(
    *,
    command: str,
    request_files: list[str],
    run_id: str,
    error: str,
    error_stage: str,
    error_kind: str,
    failed_request_file: str,
    failed_request_index: int,
    processed_request_count: int,
    next_step: str,
) -> OrderedDict[str, Any]:
    return OrderedDict(
        [
            ("command", command),
            ("status", "error"),
            ("request_files", order_for_operator_review(request_files)),
            ("run_id", run_id),
            ("error_stage", error_stage),
            ("error_kind", error_kind),
            ("failed_request_file", failed_request_file),
            ("failed_request_index", failed_request_index),
            ("processed_request_count", processed_request_count),
            ("error", error),
            ("next_step", next_step),
        ]
    )


def render_output(payload: OrderedDict[str, Any]) -> str:
    return json.dumps(payload, indent=2)


def build_review_summary(
    *,
    command: str,
    request_file: str,
    run_id: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    result_status = (
        summary.get("flow_status")
        or summary.get("bundle_status")
        or summary.get("artifact_status")
        or "unknown"
    )
    review_sections = [
        key
        for key in (
            "validation_summary",
            "normalized_task",
            "single_ai_execution_package",
            "task_manifest",
            "reviewable_output_bundle",
            "one_shot_ai_ready_artifact",
        )
        if key in summary
    ]

    primary_artifact: dict[str, Any]
    completion_signal: dict[str, Any]
    quick_status: dict[str, Any]
    readiness_checklist: dict[str, Any]
    confidence_summary: dict[str, Any]
    chain_trace_summary: dict[str, Any]
    review_evidence_summary: dict[str, Any]
    acceptance_evidence_hint: dict[str, Any]
    review_sequence_summary: dict[str, Any]
    progression_governance_summary: dict[str, Any]
    acceptance_discipline_summary: dict[str, Any]
    primary_review_target: dict[str, Any]
    handoff_target: dict[str, Any]
    next_bounded_action: dict[str, Any]
    review_first: dict[str, Any]
    manual_handoff_summary: dict[str, Any]
    review_to_handoff_bridge: dict[str, Any]
    handoff_surface: dict[str, Any]
    if "one_shot_ai_ready_artifact" in summary:
        artifact = summary["one_shot_ai_ready_artifact"]
        bundle = summary["reviewable_output_bundle"]
        bundle_traceability = bundle.get("traceability", {})
        package_payload = bundle.get("single_ai_package_payload", {})
        package_traceability = package_payload.get("traceability", {})
        completion_signal = {
            "state": "handoff_complete_candidate",
            "review_complete_candidate": True,
            "handoff_complete_candidate": True,
        }
        quick_status = {
            "command": command,
            "result_status": result_status,
            "primary_artifact_type": artifact.get("artifact_type"),
            "ready_for_review": True,
            "ready_for_handoff": True,
        }
        readiness_checklist = {
            "ready_for_review": True,
            "ready_for_next_bounded_step": False,
            "ready_for_handoff": True,
        }
        confidence_summary = {
            "confidence_state": "low_ambiguity_for_manual_handoff",
            "confidence_basis": [
                "completion_signal_handoff_complete_candidate",
                "readiness_checklist_ready_for_handoff",
                "handoff_surface_prompt_text_present",
            ],
            "next_safe_bounded_action": "handoff one_shot_ai_ready_artifact.prompt_text to one AI manually",
        }
        chain_trace_summary = {
            "current_stage": "one_shot_ai_ready_prompt",
            "current_artifact_id": artifact.get("artifact_id"),
            "current_artifact_type": artifact.get("artifact_type"),
            "request_traceability_seed": bundle_traceability.get("request_traceability_seed")
            or package_traceability.get("request_traceability_seed"),
            "upstream_evidence": {
                "request_id": summary.get("request_id"),
                "flow_id": summary.get("flow_id"),
                "normalized_task_id": bundle_traceability.get("normalized_task_id"),
                "package_id": bundle_traceability.get("package_id"),
                "bundle_id": bundle.get("bundle_id"),
                "task_manifest_id": bundle_traceability.get("task_manifest_id")
                or package_traceability.get("task_manifest_id"),
                "preparation_contract_id": bundle_traceability.get("preparation_contract_id")
                or package_traceability.get("preparation_contract_id"),
            },
        }
        review_evidence_summary = {
            "evidence_status": "bounded_handoff_evidence_present",
            "evidence_needed": [
                "one_shot_ai_ready_artifact.prompt_text",
                "one_shot_ai_ready_artifact.prompt_sections.traceability",
                "reviewable_output_bundle.traceability",
            ],
            "evidence_present": [
                "one_shot_ai_ready_artifact",
                "one_shot_ai_ready_artifact.prompt_text",
                "reviewable_output_bundle",
                "reviewable_output_bundle.traceability",
            ],
        }
        acceptance_evidence_hint = {
            "acceptance_state": "bounded_handoff_surface_ready_for_acceptance",
            "acceptance_scope": "manual_single_ai_handoff",
            "acceptance_evidence_anchor": [
                "review_evidence_summary.evidence_status",
                "one_shot_ai_ready_artifact.prompt_text",
                "chain_trace_summary.current_artifact_id",
            ],
        }
        review_sequence_summary = {
            "start_with": "one_shot_ai_ready_artifact",
            "confirm_with": "one_shot_ai_ready_artifact.prompt_text",
            "review_goal": "confirm_manual_single_ai_handoff_payload",
        }
        progression_governance_summary = {
            "allowed_progression": "manual_single_ai_handoff_only",
            "progression_mode": "operator_initiated",
            "blocked_actions": [
                "auto_execute_ai",
                "merge_main",
                "push_main",
                "tag_release",
            ],
        }
        acceptance_discipline_summary = {
            "acceptance_mode": "human_review_then_manual_handoff",
            "acceptance_gate": "operator_confirms_prompt_surface_before_handoff",
            "release_actions_authorized": False,
        }
        primary_artifact = {
            "artifact_id": artifact.get("artifact_id"),
            "artifact_type": artifact.get("artifact_type"),
            "artifact_version": artifact.get("artifact_version"),
            "usage_mode": artifact.get("usage_mode"),
        }
        primary_review_target = {
            "section": "one_shot_ai_ready_artifact",
            "focus": "manual_single_ai_handoff_surface",
        }
        handoff_target = {
            "target_type": "manual_single_ai_handoff",
            "artifact_section": "one_shot_ai_ready_artifact",
            "usage_mode": artifact.get("usage_mode"),
        }
        next_bounded_action = {
            "action_type": "handoff_to_one_ai",
            "target_section": "one_shot_ai_ready_artifact",
        }
        review_first = {
            "section": "one_shot_ai_ready_artifact",
            "then_check": "one_shot_ai_ready_artifact.prompt_text",
        }
        manual_handoff_summary = {
            "handoff_state": "ready_for_manual_single_ai_handoff",
            "handoff_artifact_section": "one_shot_ai_ready_artifact",
            "handoff_artifact_field": "prompt_text",
            "handoff_guardrail": "operator_copy_or_send_without_scope_expansion",
        }
        review_to_handoff_bridge = {
            "bridge_state": "review_prompt_then_handoff",
            "review_complete_when": [
                "review_sequence_summary.confirm_with",
                "acceptance_evidence_hint.acceptance_state",
            ],
            "handoff_surface": "one_shot_ai_ready_artifact.prompt_text",
        }
        handoff_surface = {
            "section": "one_shot_ai_ready_artifact",
            "artifact_field": "prompt_text",
            "mode": artifact.get("usage_mode"),
        }
    elif "reviewable_output_bundle" in summary:
        artifact = summary["reviewable_output_bundle"]
        bundle_traceability = artifact.get("traceability", {})
        completion_signal = {
            "state": "review_complete_candidate",
            "review_complete_candidate": True,
            "handoff_complete_candidate": False,
        }
        quick_status = {
            "command": command,
            "result_status": result_status,
            "primary_artifact_type": artifact.get("bundle_type"),
            "ready_for_review": True,
            "ready_for_handoff": False,
        }
        readiness_checklist = {
            "ready_for_review": True,
            "ready_for_next_bounded_step": True,
            "ready_for_handoff": False,
        }
        confidence_summary = {
            "confidence_state": "low_ambiguity_for_review_then_progression",
            "confidence_basis": [
                "completion_signal_review_complete_candidate",
                "readiness_checklist_ready_for_next_bounded_step",
                "review_surface_present",
            ],
            "next_safe_bounded_action": "./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml",
        }
        chain_trace_summary = {
            "current_stage": "reviewable_single_ai_bundle",
            "current_artifact_id": artifact.get("bundle_id"),
            "current_artifact_type": artifact.get("bundle_type"),
            "request_traceability_seed": bundle_traceability.get("request_traceability_seed"),
            "upstream_evidence": {
                "request_id": summary.get("request_id"),
                "flow_id": summary.get("flow_id"),
                "normalized_task_id": bundle_traceability.get("normalized_task_id"),
                "package_id": bundle_traceability.get("package_id"),
                "task_manifest_id": bundle_traceability.get("task_manifest_id"),
                "preparation_contract_id": bundle_traceability.get("preparation_contract_id"),
            },
        }
        review_evidence_summary = {
            "evidence_status": "bounded_review_evidence_present",
            "evidence_needed": [
                "reviewable_output_bundle.review_surface",
                "reviewable_output_bundle.traceability",
                "reviewable_output_bundle.single_ai_package_payload.traceability",
            ],
            "evidence_present": [
                "reviewable_output_bundle",
                "reviewable_output_bundle.review_surface",
                "reviewable_output_bundle.traceability",
            ],
        }
        acceptance_evidence_hint = {
            "acceptance_state": "bounded_review_surface_ready_for_acceptance",
            "acceptance_scope": "reviewable_single_ai_bundle",
            "acceptance_evidence_anchor": [
                "review_evidence_summary.evidence_status",
                "reviewable_output_bundle.review_surface",
                "chain_trace_summary.current_artifact_id",
            ],
        }
        review_sequence_summary = {
            "start_with": "reviewable_output_bundle",
            "confirm_with": "reviewable_output_bundle.review_surface",
            "review_goal": "confirm_bundle_is_ready_for_human_review",
        }
        progression_governance_summary = {
            "allowed_progression": "render_request_prompt_after_review",
            "progression_mode": "operator_initiated",
            "blocked_actions": [
                "auto_execute_ai",
                "merge_main",
                "push_main",
                "tag_release",
            ],
        }
        acceptance_discipline_summary = {
            "acceptance_mode": "human_review_before_prompt_render",
            "acceptance_gate": "operator_confirms_reviewable_bundle_before_handoff_progression",
            "release_actions_authorized": False,
        }
        primary_artifact = {
            "bundle_id": artifact.get("bundle_id"),
            "bundle_type": artifact.get("bundle_type"),
            "bundle_version": artifact.get("bundle_version"),
        }
        primary_review_target = {
            "section": "reviewable_output_bundle",
            "focus": "human_reviewable_bundle_surface",
        }
        handoff_target = {
            "target_type": "next_bounded_cli_step",
            "command": "request-prompt",
            "artifact_section": "reviewable_output_bundle",
        }
        next_bounded_action = {
            "action_type": "run_cli_command",
            "command": "./atp request-prompt "
            "tests/fixtures/requests/sample_request_slice02.yaml",
        }
        review_first = {
            "section": "reviewable_output_bundle",
            "then_check": "reviewable_output_bundle.review_surface",
        }
        manual_handoff_summary = {
            "handoff_state": "not_ready_for_manual_handoff",
            "handoff_artifact_section": "reviewable_output_bundle",
            "next_bounded_surface": "one_shot_ai_ready_artifact",
            "handoff_guardrail": "render_request_prompt_before_manual_handoff",
        }
        review_to_handoff_bridge = {
            "bridge_state": "review_bundle_then_render_prompt",
            "review_complete_when": [
                "review_sequence_summary.confirm_with",
                "acceptance_evidence_hint.acceptance_state",
            ],
            "next_surface": "one_shot_ai_ready_artifact",
        }
        handoff_surface = {
            "section": "reviewable_output_bundle",
            "mode": "prepare_request_prompt",
            "next_command": "request-prompt",
        }
    else:
        artifact = summary.get("single_ai_execution_package", {})
        traceability = artifact.get("traceability", {})
        completion_signal = {
            "state": "complete_for_current_step",
            "review_complete_candidate": False,
            "handoff_complete_candidate": False,
        }
        quick_status = {
            "command": command,
            "result_status": result_status,
            "primary_artifact_type": artifact.get("package_type"),
            "ready_for_review": True,
            "ready_for_handoff": False,
        }
        readiness_checklist = {
            "ready_for_review": True,
            "ready_for_next_bounded_step": True,
            "ready_for_handoff": False,
        }
        confidence_summary = {
            "confidence_state": "low_ambiguity_for_bounded_progression",
            "confidence_basis": [
                "completion_signal_complete_for_current_step",
                "readiness_checklist_ready_for_next_bounded_step",
                "primary_artifact_identified",
            ],
            "next_safe_bounded_action": "./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml",
        }
        chain_trace_summary = {
            "current_stage": "single_ai_execution_package",
            "current_artifact_id": artifact.get("package_id"),
            "current_artifact_type": artifact.get("package_type"),
            "request_traceability_seed": traceability.get("request_traceability_seed"),
            "upstream_evidence": {
                "request_id": summary.get("request_id"),
                "flow_id": summary.get("flow_id"),
                "task_id": summary.get("normalized_task", {}).get("task_id"),
                "task_manifest_id": traceability.get("task_manifest_id"),
                "preparation_contract_id": traceability.get("preparation_contract_id"),
            },
        }
        review_evidence_summary = {
            "evidence_status": "bounded_preparation_evidence_present",
            "evidence_needed": [
                "validation_summary",
                "single_ai_execution_package.traceability",
                "task_manifest.input_artifacts",
            ],
            "evidence_present": [
                "validation_summary",
                "single_ai_execution_package",
                "single_ai_execution_package.traceability",
                "task_manifest",
            ],
        }
        acceptance_evidence_hint = {
            "acceptance_state": "bounded_step_evidence_ready_for_acceptance",
            "acceptance_scope": "single_ai_execution_package_preparation",
            "acceptance_evidence_anchor": [
                "review_evidence_summary.evidence_status",
                "single_ai_execution_package.traceability",
                "chain_trace_summary.current_artifact_id",
            ],
        }
        review_sequence_summary = {
            "start_with": "validation_summary",
            "confirm_with": "single_ai_execution_package",
            "review_goal": "confirm_bounded_request_preparation",
        }
        progression_governance_summary = {
            "allowed_progression": "materialize_reviewable_bundle_after_review",
            "progression_mode": "operator_initiated",
            "blocked_actions": [
                "auto_execute_ai",
                "merge_main",
                "push_main",
                "tag_release",
            ],
        }
        acceptance_discipline_summary = {
            "acceptance_mode": "human_review_before_bundle_progression",
            "acceptance_gate": "operator_confirms_preparation_surface_before_next_step",
            "release_actions_authorized": False,
        }
        primary_artifact = {
            "package_id": artifact.get("package_id"),
            "package_type": artifact.get("package_type"),
            "package_version": artifact.get("package_version"),
            "target_mode": artifact.get("target_mode"),
        }
        primary_review_target = {
            "section": "single_ai_execution_package",
            "focus": "bounded_execution_package_surface",
        }
        handoff_target = {
            "target_type": "next_bounded_cli_step",
            "command": "request-bundle",
            "artifact_section": "single_ai_execution_package",
        }
        next_bounded_action = {
            "action_type": "run_cli_command",
            "command": "./atp request-bundle "
            "tests/fixtures/requests/sample_request_slice02.yaml",
        }
        review_first = {
            "section": "validation_summary",
            "then_check": "single_ai_execution_package",
        }
        manual_handoff_summary = {
            "handoff_state": "not_ready_for_manual_handoff",
            "handoff_artifact_section": "single_ai_execution_package",
            "next_bounded_surface": "reviewable_output_bundle",
            "handoff_guardrail": "materialize_reviewable_bundle_first",
        }
        review_to_handoff_bridge = {
            "bridge_state": "review_flow_then_materialize_bundle",
            "review_complete_when": [
                "review_sequence_summary.confirm_with",
                "acceptance_evidence_hint.acceptance_state",
            ],
            "next_surface": "reviewable_output_bundle",
        }
        handoff_surface = {
            "section": "single_ai_execution_package",
            "mode": "prepare_reviewable_bundle",
            "next_command": "request-bundle",
        }

    return {
        "command": command,
        "request_file": request_file,
        "run_id": run_id,
        "product": summary.get("product"),
        "request_id": summary.get("request_id"),
        "flow_id": summary.get("flow_id"),
        "supported_flow": summary.get("supported_flow"),
        "result_status": result_status,
        "completion_signal": completion_signal,
        "quick_status": quick_status,
        "readiness_checklist": readiness_checklist,
        "confidence_summary": confidence_summary,
        "chain_trace_summary": chain_trace_summary,
        "review_evidence_summary": review_evidence_summary,
        "acceptance_evidence_hint": acceptance_evidence_hint,
        "review_sequence_summary": review_sequence_summary,
        "progression_governance_summary": progression_governance_summary,
        "acceptance_discipline_summary": acceptance_discipline_summary,
        "primary_artifact": primary_artifact,
        "primary_review_target": primary_review_target,
        "handoff_target": handoff_target,
        "next_bounded_action": next_bounded_action,
        "review_first": review_first,
        "manual_handoff_summary": manual_handoff_summary,
        "review_to_handoff_bridge": review_to_handoff_bridge,
        "handoff_surface": handoff_surface,
        "review_sections": review_sections,
    }
