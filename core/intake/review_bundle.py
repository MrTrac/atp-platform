"""Build Slice 03 reviewable single-AI output bundles."""

from __future__ import annotations

from typing import Any

from core.intake.request_flow import prepare_single_ai_request_flow


class ReviewBundleError(ValueError):
    """Raised when a reviewable bundle cannot be constructed."""


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReviewBundleError(f"{field_name} must be a mapping.")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ReviewBundleError(f"{field_name} is required.")

    text = value.strip()
    if not text:
        raise ReviewBundleError(f"{field_name} is required.")
    return text


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ReviewBundleError(f"{field_name} must be a list of strings.")

    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if not text:
            raise ReviewBundleError(f"{field_name} must contain only non-empty strings.")
        result.append(text)
    return result


def build_reviewable_single_ai_output_bundle(prepared_flow: dict[str, Any]) -> dict[str, Any]:
    """Transform the Slice 02 flow output into a reviewable single-AI bundle."""

    flow = _require_mapping(prepared_flow, "prepared_flow")
    flow_id = _require_string(flow.get("flow_id"), "prepared_flow.flow_id")
    request_id = _require_string(flow.get("request_id"), "prepared_flow.request_id")
    product = _require_string(flow.get("product"), "prepared_flow.product")

    normalized_task = _require_mapping(
        flow.get("normalized_task"),
        "prepared_flow.normalized_task",
    )
    single_ai_package = _require_mapping(
        flow.get("single_ai_execution_package"),
        "prepared_flow.single_ai_execution_package",
    )

    task_id = _require_string(normalized_task.get("task_id"), "prepared_flow.normalized_task.task_id")
    package_id = _require_string(
        single_ai_package.get("package_id"),
        "prepared_flow.single_ai_execution_package.package_id",
    )
    task_manifest_id = _require_string(
        single_ai_package.get("task_manifest_id"),
        "prepared_flow.single_ai_execution_package.task_manifest_id",
    )
    preparation_contract_id = _require_string(
        single_ai_package.get("preparation_contract_id"),
        "prepared_flow.single_ai_execution_package.preparation_contract_id",
    )
    instructions = _require_mapping(
        single_ai_package.get("instructions"),
        "prepared_flow.single_ai_execution_package.instructions",
    )
    traceability = _require_mapping(
        single_ai_package.get("traceability"),
        "prepared_flow.single_ai_execution_package.traceability",
    )

    request_scope = _require_string_list(
        instructions.get("scope"),
        "prepared_flow.single_ai_execution_package.instructions.scope",
    )
    request_constraints = _require_string_list(
        instructions.get("constraints"),
        "prepared_flow.single_ai_execution_package.instructions.constraints",
    )
    request_policy_context = _require_string_list(
        instructions.get("policy_context"),
        "prepared_flow.single_ai_execution_package.instructions.policy_context",
    )

    request_traceability_seed = _require_string(
        traceability.get("request_traceability_seed"),
        "prepared_flow.single_ai_execution_package.traceability.request_traceability_seed",
    )

    return {
        "bundle_id": f"reviewable-output-bundle-{request_id}",
        "bundle_version": "v1.1-slice-03",
        "bundle_type": "reviewable_single_ai_output_bundle",
        "request_identity": {
            "request_id": request_id,
            "product": product,
            "flow_id": flow_id,
            "flow_status": _require_string(flow.get("flow_status"), "prepared_flow.flow_status"),
        },
        "normalized_task_summary": {
            "task_id": task_id,
            "task_type": _require_string(normalized_task.get("task_type"), "prepared_flow.normalized_task.task_type"),
            "task_goal": _require_string(normalized_task.get("task_goal"), "prepared_flow.normalized_task.task_goal"),
            "request_type": _require_string(normalized_task.get("request_type"), "prepared_flow.normalized_task.request_type"),
            "execution_intent": _require_string(normalized_task.get("execution_intent"), "prepared_flow.normalized_task.execution_intent"),
            "required_capabilities": _require_string_list(
                normalized_task.get("required_capabilities", []),
                "prepared_flow.normalized_task.required_capabilities",
            ),
        },
        "scope_and_constraints": {
            "request_scope": request_scope,
            "request_constraints": request_constraints,
            "request_policy_context": request_policy_context,
        },
        "single_ai_package_payload": {
            "package_id": package_id,
            "package_type": _require_string(single_ai_package.get("package_type"), "prepared_flow.single_ai_execution_package.package_type"),
            "package_version": _require_string(single_ai_package.get("package_version"), "prepared_flow.single_ai_execution_package.package_version"),
            "target_mode": _require_string(single_ai_package.get("target_mode"), "prepared_flow.single_ai_execution_package.target_mode"),
            "instructions": instructions,
            "traceability": traceability,
        },
        "review_surface": {
            "human_readable_sections": [
                "request_identity",
                "normalized_task_summary",
                "scope_and_constraints",
                "single_ai_package_payload",
                "traceability",
            ],
            "handoff_mode": "single_ai_reviewable_bundle",
            "review_notes": [
                "Slice 03 reviewable bundle only.",
                "This bundle is for human inspection and single-AI handoff readiness only.",
                "No execution, routing, scheduling, or release/integration behavior is performed here.",
            ],
        },
        "traceability": {
            "request_id": request_id,
            "normalized_task_id": task_id,
            "package_id": package_id,
            "task_manifest_id": task_manifest_id,
            "preparation_contract_id": preparation_contract_id,
            "request_traceability_seed": request_traceability_seed,
        },
    }


def prepare_reviewable_single_ai_output_bundle(
    raw_request: dict[str, Any],
    *,
    run_id: str = "slice-03-preview-0001",
) -> dict[str, Any]:
    """Prepare the Slice 03 reviewable bundle from a raw request."""

    prepared_flow = prepare_single_ai_request_flow(raw_request, run_id=run_id)
    bundle = build_reviewable_single_ai_output_bundle(prepared_flow)
    return {
        "flow_id": prepared_flow["flow_id"],
        "request_id": prepared_flow["request_id"],
        "product": prepared_flow["product"],
        "bundle_status": "reviewable",
        "supported_flow": prepared_flow["supported_flow"],
        "reviewable_output_bundle": bundle,
        "notes": [
            "Slice 03 extends Slice 02 by materializing one deterministic reviewable output bundle.",
            "The bundle stays bounded to a single-AI path and does not execute AI work.",
        ],
    }
