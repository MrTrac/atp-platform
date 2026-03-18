"""Bounded output-contract helpers for ATP request-chain CLIs."""

from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any


_PREFERRED_KEY_ORDER = [
    "command",
    "status",
    "request_file",
    "run_id",
    "review_summary",
    "summary",
    "error_stage",
    "error_kind",
    "error",
    "next_step",
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
    "primary_artifact",
    "primary_review_target",
    "handoff_target",
    "next_bounded_action",
    "review_first",
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
    return order_for_operator_review(payload)


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
    primary_review_target: dict[str, Any]
    handoff_target: dict[str, Any]
    next_bounded_action: dict[str, Any]
    review_first: dict[str, Any]
    handoff_surface: dict[str, Any]
    if "one_shot_ai_ready_artifact" in summary:
        artifact = summary["one_shot_ai_ready_artifact"]
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
        handoff_surface = {
            "section": "one_shot_ai_ready_artifact",
            "artifact_field": "prompt_text",
            "mode": artifact.get("usage_mode"),
        }
    elif "reviewable_output_bundle" in summary:
        artifact = summary["reviewable_output_bundle"]
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
        handoff_surface = {
            "section": "reviewable_output_bundle",
            "mode": "prepare_request_prompt",
            "next_command": "request-prompt",
        }
    else:
        artifact = summary.get("single_ai_execution_package", {})
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
        "primary_artifact": primary_artifact,
        "primary_review_target": primary_review_target,
        "handoff_target": handoff_target,
        "next_bounded_action": next_bounded_action,
        "review_first": review_first,
        "handoff_surface": handoff_surface,
        "review_sections": review_sections,
    }
