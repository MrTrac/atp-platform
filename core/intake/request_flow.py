"""Bounded Slice 02 request intake to single-AI package flow."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.classification.classifier import classify_request
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import (
    build_product_execution_preparation_contract,
    build_request_to_product_resolution_contract,
    build_resolution_to_handoff_intent_contract,
    resolve_product,
)


class RequestFlowError(ValueError):
    """Raised when the Slice 02 request flow cannot accept the request."""


def _as_string_list(value: Any, field_name: str) -> list[str]:
    if isinstance(value, str):
        compact = value.strip()
        if not compact:
            raise RequestFlowError(f"{field_name} must not be empty.")
        return [compact]

    if not isinstance(value, list) or not value:
        raise RequestFlowError(f"{field_name} must be a non-empty string or list of strings.")

    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RequestFlowError(f"{field_name} must contain only non-empty strings.")
        items.append(item.strip())
    return items


def _build_core_artifacts(
    request_id: str,
    product: str,
    task_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest_reference = str(task_manifest["manifest_id"])
    return [
        {
            "artifact_id": f"raw-request-{request_id}",
            "artifact_type": "request_raw",
            "artifact_freshness": "current",
            "authoritative": False,
            "manifest_reference": manifest_reference,
            "product": product,
        },
        {
            "artifact_id": f"normalized-request-{request_id}",
            "artifact_type": "request_normalized",
            "artifact_freshness": "current",
            "authoritative": True,
            "manifest_reference": manifest_reference,
            "product": product,
        },
        {
            "artifact_id": f"classification-{request_id}",
            "artifact_type": "classification",
            "artifact_freshness": "current",
            "authoritative": True,
            "manifest_reference": manifest_reference,
            "product": product,
        },
        {
            "artifact_id": f"resolution-{request_id}",
            "artifact_type": "resolution",
            "artifact_freshness": "current",
            "authoritative": True,
            "manifest_reference": manifest_reference,
            "product": product,
        },
        {
            "artifact_id": manifest_reference,
            "artifact_type": "task_manifest",
            "artifact_freshness": "current",
            "authoritative": True,
            "manifest_reference": manifest_reference,
            "product": product,
        },
    ]


def _validate_supported_request(normalized_request: dict[str, Any]) -> dict[str, Any]:
    product = str(normalized_request.get("product", "")).strip().upper()
    if product != "ATP":
        raise RequestFlowError("Slice 02 supports ATP requests only.")

    request_type = str(normalized_request.get("request_type", "")).strip()
    if request_type != "implementation":
        raise RequestFlowError(
            "Slice 02 supports only implementation requests for the first usable flow."
        )

    execution_intent = str(normalized_request.get("execution_intent", "")).strip()
    if execution_intent != "preview":
        raise RequestFlowError(
            "Slice 02 supports only preview execution_intent for the first usable flow."
        )

    payload = normalized_request.get("payload")
    if not isinstance(payload, dict):
        raise RequestFlowError("payload must be a mapping for the Slice 02 request flow.")

    input_text = str(payload.get("input_text", "")).strip()
    if not input_text:
        raise RequestFlowError("payload.input_text is required.")

    policy_context = _as_string_list(payload.get("request_policy_context"), "payload.request_policy_context")
    scope = _as_string_list(payload.get("request_scope"), "payload.request_scope")
    constraints = _as_string_list(payload.get("request_constraints"), "payload.request_constraints")

    traceability_seed = str(payload.get("request_traceability_seed", "")).strip()
    if not traceability_seed:
        raise RequestFlowError("payload.request_traceability_seed is required.")

    return {
        "input_text": input_text,
        "request_scope": scope,
        "request_constraints": constraints,
        "request_policy_context": policy_context,
        "request_traceability_seed": traceability_seed,
    }


def _build_single_ai_task_form(
    normalized_request: dict[str, Any],
    validated_payload: dict[str, Any],
    classification: dict[str, Any],
    task_manifest: dict[str, Any],
) -> dict[str, Any]:
    request_id = str(normalized_request["request_id"])
    return {
        "task_id": f"single-ai-task-{request_id}",
        "request_id": request_id,
        "product": str(normalized_request["product"]).upper(),
        "task_type": "single_ai_execution_package_preparation",
        "task_goal": validated_payload["input_text"],
        "request_scope": list(validated_payload["request_scope"]),
        "request_constraints": list(validated_payload["request_constraints"]),
        "request_policy_context": list(validated_payload["request_policy_context"]),
        "request_traceability_seed": validated_payload["request_traceability_seed"],
        "request_type": str(classification.get("request_type", "implementation")),
        "execution_intent": str(classification.get("execution_intent", "preview")),
        "required_capabilities": list(task_manifest.get("required_capabilities", [])),
    }


def _build_single_ai_execution_package(
    task_form: dict[str, Any],
    task_manifest: dict[str, Any],
    preparation_contract: dict[str, Any],
) -> dict[str, Any]:
    request_id = str(task_form["request_id"])
    return {
        "package_id": f"single-ai-package-{request_id}",
        "package_version": "v1.1-slice-02",
        "package_type": "single_ai_execution_package",
        "target_mode": "single_ai",
        "task_id": str(task_form["task_id"]),
        "request_id": request_id,
        "task_manifest_id": str(task_manifest["manifest_id"]),
        "preparation_contract_id": str(preparation_contract["contract_id"]),
        "instructions": {
            "goal": str(task_form["task_goal"]),
            "scope": list(task_form["request_scope"]),
            "constraints": list(task_form["request_constraints"]),
            "policy_context": list(task_form["request_policy_context"]),
        },
        "traceability": {
            "request_traceability_seed": str(task_form["request_traceability_seed"]),
            "task_manifest_id": str(task_manifest["manifest_id"]),
            "preparation_contract_id": str(preparation_contract["contract_id"]),
        },
        "notes": [
            "Slice 02 thin vertical flow only.",
            "Single-AI execution package preparation only. No routing, scheduling, or multi-provider orchestration is performed here.",
        ],
    }


def prepare_single_ai_request_flow(
    raw_request: dict[str, Any],
    *,
    run_id: str = "slice-02-preview-0001",
) -> dict[str, Any]:
    """Prepare the first usable request flow for a single-AI package surface."""

    normalized_request = normalize_request(deepcopy(raw_request))
    validated_payload = _validate_supported_request(normalized_request)
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
    preparation_contract = build_product_execution_preparation_contract(
        run_id=run_id,
        normalized_request=normalized_request,
        resolution_contract=request_to_product_resolution,
        handoff_intent_contract=resolution_to_handoff_intent,
        task_manifest=task_manifest,
        product_context=product_context,
        evidence_bundle=evidence_bundle,
    )
    task_form = _build_single_ai_task_form(
        normalized_request,
        validated_payload,
        classification,
        task_manifest,
    )
    execution_package = _build_single_ai_execution_package(
        task_form,
        task_manifest,
        preparation_contract,
    )

    return {
        "flow_id": f"slice-02-request-flow-{normalized_request['request_id']}",
        "flow_status": "accepted",
        "request_id": str(normalized_request["request_id"]),
        "product": str(resolution["product"]),
        "supported_flow": "first_usable_request_intake_to_single_ai_package",
        "normalized_task": task_form,
        "task_manifest": task_manifest,
        "single_ai_execution_package": execution_package,
        "validation_summary": {
            "request_shape": "accepted",
            "supported_scope": "accepted",
            "invalid_or_out_of_scope": False,
        },
        "notes": [
            "Slice 02 prepares a thin vertical request path only.",
            "No execution, routing selection, scheduler graph, or multi-provider orchestration is performed here.",
        ],
    }
