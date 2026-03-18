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
    "summary",
    "error",
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
    return order_for_operator_review(
        {
            "command": command,
            "status": "ok",
            "request_file": request_file,
            "run_id": run_id,
            "summary": summary,
        }
    )


def build_error_envelope(
    *,
    command: str,
    request_file: str,
    run_id: str,
    error: str,
) -> OrderedDict[str, Any]:
    return order_for_operator_review(
        {
            "command": command,
            "status": "error",
            "request_file": request_file,
            "run_id": run_id,
            "error": error,
        }
    )


def render_output(payload: OrderedDict[str, Any]) -> str:
    return json.dumps(payload, indent=2)
