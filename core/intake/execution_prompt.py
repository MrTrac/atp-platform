"""Build Slice 04 one-shot AI-ready execution prompt artifacts."""

from __future__ import annotations

from typing import Any

from core.intake.review_bundle import (
    ReviewBundleError,
    prepare_reviewable_single_ai_output_bundle,
)


class ExecutionPromptError(ValueError):
    """Raised when a one-shot AI-ready prompt cannot be constructed."""


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExecutionPromptError(f"{field_name} must be a mapping.")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ExecutionPromptError(f"{field_name} is required.")

    text = value.strip()
    if not text:
        raise ExecutionPromptError(f"{field_name} is required.")
    return text


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ExecutionPromptError(f"{field_name} must be a list of strings.")

    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if not text:
            raise ExecutionPromptError(f"{field_name} must contain only non-empty strings.")
        result.append(text)
    return result


def _render_prompt_text(
    request_identity: dict[str, Any],
    task_summary: dict[str, Any],
    scope_and_constraints: dict[str, Any],
    single_ai_package_payload: dict[str, Any],
    traceability: dict[str, Any],
) -> str:
    scope_lines = "\n".join(f"- {item}" for item in scope_and_constraints["request_scope"])
    constraint_lines = "\n".join(
        f"- {item}" for item in scope_and_constraints["request_constraints"]
    )
    policy_lines = "\n".join(
        f"- {item}" for item in scope_and_constraints["request_policy_context"]
    )
    capability_lines = "\n".join(
        f"- {item}" for item in task_summary["required_capabilities"]
    )

    return "\n".join(
        [
            "You are handling one bounded ATP request.",
            "",
            "Task summary:",
            f"- Request ID: {request_identity['request_id']}",
            f"- Product: {request_identity['product']}",
            f"- Task goal: {task_summary['task_goal']}",
            f"- Task type: {task_summary['task_type']}",
            f"- Execution intent: {task_summary['execution_intent']}",
            "",
            "Scope:",
            scope_lines,
            "",
            "Constraints:",
            constraint_lines,
            "",
            "Policy context:",
            policy_lines,
            "",
            "Required capabilities:",
            capability_lines,
            "",
            "Execution package payload:",
            f"- Package ID: {single_ai_package_payload['package_id']}",
            f"- Package type: {single_ai_package_payload['package_type']}",
            f"- Target mode: {single_ai_package_payload['target_mode']}",
            "",
            "Instructions:",
            "- Work only within the explicit scope and constraints above.",
            "- Do not expand into unrelated architecture or orchestration work.",
            "- Treat this as a manual one-shot execution prompt only.",
            "",
            "Traceability:",
            f"- Request traceability seed: {traceability['request_traceability_seed']}",
            f"- Task manifest ID: {traceability['task_manifest_id']}",
            f"- Preparation contract ID: {traceability['preparation_contract_id']}",
        ]
    )


def build_one_shot_ai_ready_execution_prompt(
    reviewable_bundle_summary: dict[str, Any],
) -> dict[str, Any]:
    """Transform a Slice 03 reviewable bundle into a one-shot AI-ready artifact."""

    summary = _require_mapping(reviewable_bundle_summary, "reviewable_bundle_summary")
    request_id = _require_string(
        summary.get("request_id"), "reviewable_bundle_summary.request_id"
    )
    flow_id = _require_string(
        summary.get("flow_id"), "reviewable_bundle_summary.flow_id"
    )
    supported_flow = _require_string(
        summary.get("supported_flow"), "reviewable_bundle_summary.supported_flow"
    )
    product = _require_string(
        summary.get("product"), "reviewable_bundle_summary.product"
    )

    reviewable_bundle = _require_mapping(
        summary.get("reviewable_output_bundle"),
        "reviewable_bundle_summary.reviewable_output_bundle",
    )
    request_identity = _require_mapping(
        reviewable_bundle.get("request_identity"),
        "reviewable_bundle_summary.reviewable_output_bundle.request_identity",
    )
    task_summary = _require_mapping(
        reviewable_bundle.get("normalized_task_summary"),
        "reviewable_bundle_summary.reviewable_output_bundle.normalized_task_summary",
    )
    scope_and_constraints = _require_mapping(
        reviewable_bundle.get("scope_and_constraints"),
        "reviewable_bundle_summary.reviewable_output_bundle.scope_and_constraints",
    )
    single_ai_package_payload = _require_mapping(
        reviewable_bundle.get("single_ai_package_payload"),
        "reviewable_bundle_summary.reviewable_output_bundle.single_ai_package_payload",
    )
    traceability = _require_mapping(
        reviewable_bundle.get("traceability"),
        "reviewable_bundle_summary.reviewable_output_bundle.traceability",
    )

    _require_string(request_identity.get("request_id"), "request_identity.request_id")
    _require_string(request_identity.get("product"), "request_identity.product")
    _require_string(task_summary.get("task_goal"), "normalized_task_summary.task_goal")
    _require_string(task_summary.get("task_type"), "normalized_task_summary.task_type")
    _require_string(
        task_summary.get("execution_intent"),
        "normalized_task_summary.execution_intent",
    )
    _require_string_list(
        task_summary.get("required_capabilities", []),
        "normalized_task_summary.required_capabilities",
    )
    _require_string_list(
        scope_and_constraints.get("request_scope"),
        "scope_and_constraints.request_scope",
    )
    _require_string_list(
        scope_and_constraints.get("request_constraints"),
        "scope_and_constraints.request_constraints",
    )
    _require_string_list(
        scope_and_constraints.get("request_policy_context"),
        "scope_and_constraints.request_policy_context",
    )
    _require_string(
        single_ai_package_payload.get("package_id"),
        "single_ai_package_payload.package_id",
    )
    _require_string(
        single_ai_package_payload.get("package_type"),
        "single_ai_package_payload.package_type",
    )
    _require_string(
        single_ai_package_payload.get("target_mode"),
        "single_ai_package_payload.target_mode",
    )
    _require_string(
        traceability.get("request_traceability_seed"),
        "traceability.request_traceability_seed",
    )
    _require_string(traceability.get("task_manifest_id"), "traceability.task_manifest_id")
    _require_string(
        traceability.get("preparation_contract_id"),
        "traceability.preparation_contract_id",
    )

    prompt_text = _render_prompt_text(
        request_identity=request_identity,
        task_summary=task_summary,
        scope_and_constraints=scope_and_constraints,
        single_ai_package_payload=single_ai_package_payload,
        traceability=traceability,
    )

    return {
        "artifact_id": f"one-shot-ai-prompt-{request_id}",
        "artifact_version": "v1.1-slice-04",
        "artifact_type": "one_shot_ai_ready_execution_prompt",
        "usage_mode": "manual_single_ai_handoff",
        "request_id": request_id,
        "flow_id": flow_id,
        "product": product,
        "supported_flow": supported_flow,
        "prompt_sections": {
            "request_identity": request_identity,
            "task_summary": task_summary,
            "scope_and_constraints": scope_and_constraints,
            "single_ai_package_payload": single_ai_package_payload,
            "traceability": traceability,
        },
        "prompt_text": prompt_text,
        "handoff_notes": [
            "Slice 04 one-shot artifact only.",
            "This artifact is intended for manual use with one AI only.",
            "No hidden execution, routing, orchestration, or release/integration behavior is performed here.",
        ],
    }


def prepare_one_shot_ai_ready_execution_prompt(
    raw_request: dict[str, Any],
    *,
    run_id: str = "slice-04-preview-0001",
) -> dict[str, Any]:
    """Prepare the Slice 04 one-shot AI-ready prompt artifact from a raw request."""

    reviewable_bundle_summary = prepare_reviewable_single_ai_output_bundle(
        raw_request, run_id=run_id
    )
    artifact = build_one_shot_ai_ready_execution_prompt(reviewable_bundle_summary)
    return {
        "request_id": reviewable_bundle_summary["request_id"],
        "product": reviewable_bundle_summary["product"],
        "flow_id": reviewable_bundle_summary["flow_id"],
        "artifact_status": "ai_ready",
        "supported_flow": reviewable_bundle_summary["supported_flow"],
        "reviewable_output_bundle": reviewable_bundle_summary["reviewable_output_bundle"],
        "one_shot_ai_ready_artifact": artifact,
        "notes": [
            "Slice 04 extends Slice 03 by materializing one deterministic AI-ready artifact.",
            "The artifact remains manual, one-shot, and single-AI only.",
        ],
    }
