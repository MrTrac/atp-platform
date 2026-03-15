"""Resolve ATP products and build the v0.5-v0.7 foundational contract chain."""

from __future__ import annotations

from typing import Any

from core.intake.loader import RequestLoadError
from core.resolution.policy_loader import PolicyLoadError, load_policies
from core.resolution.registry_io import load_yaml_mapping


class ProductResolutionError(ValueError):
    """Raised when a product cannot be resolved."""


def _compact_text(value: str, limit: int = 120) -> str:
    compact = value.replace("\n", "\\n").strip()
    return compact[:limit]


def _select_product(
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
) -> str:
    product = str(normalized_request.get("product", "")).strip()
    if product and product != "unknown":
        return product.upper()

    if classification:
        classified_product = str(classification.get("product", "")).strip()
        if classified_product and classified_product != "unknown":
            return classified_product.upper()

    raise ProductResolutionError("Product could not be resolved from request.")


def _load_registry_entry(product: str) -> dict[str, Any]:
    registry_path = f"registry/products/{product}.yaml"
    try:
        registry_entry = load_yaml_mapping(registry_path)
    except RequestLoadError as exc:
        raise ProductResolutionError(f"Product registry entry not found: {product}") from exc

    if not registry_entry.get("profile_ref"):
        raise ProductResolutionError(f"Missing profile_ref for product: {product}")

    return {**registry_entry, "registry_entry_ref": registry_path}


def _load_profile(profile_ref: str) -> dict[str, Any]:
    try:
        profile = load_yaml_mapping(profile_ref)
    except RequestLoadError as exc:
        raise ProductResolutionError(f"Profile ref not found: {profile_ref}") from exc

    if not profile.get("product"):
        raise ProductResolutionError(f"Invalid profile file: {profile_ref}")

    return profile


def _select_capability_target(
    classification: dict[str, Any] | None,
    profile: dict[str, Any],
) -> tuple[str, str]:
    if classification:
        classified_capability = str(classification.get("capability", "")).strip()
        if classified_capability and classified_capability != "unspecified":
            return classified_capability, "classification.capability"

    component_scope = profile.get("component_scope", [])
    if isinstance(component_scope, list) and component_scope:
        first_component = str(component_scope[0]).strip()
        if first_component:
            return first_component, "profile.component_scope"

    return "product_resolution", "resolution.default"


def resolve_product(
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve a product from file-based registry, profile, and policies."""

    product = _select_product(normalized_request, classification)
    registry_entry = _load_registry_entry(product)
    profile_ref = str(registry_entry["profile_ref"])
    policy_refs = list(registry_entry.get("policy_refs", []))

    try:
        profile = _load_profile(profile_ref)
        policies = load_policies(policy_refs)
    except PolicyLoadError as exc:
        raise ProductResolutionError(str(exc)) from exc

    return {
        "product": registry_entry["product"],
        "product_type": registry_entry.get("product_type", "unknown"),
        "repo_boundary": registry_entry.get("repo_boundary", "unknown"),
        "registry_entry_ref": registry_entry.get("registry_entry_ref", ""),
        "status": registry_entry.get("status", "unknown"),
        "profile_ref": profile_ref,
        "profile": profile,
        "policy_refs": policy_refs,
        "policies": policies,
    }


def build_request_to_product_resolution_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
    resolution: dict[str, Any],
    manifest_id: str = "",
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice A request-to-product resolution contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the request-to-product resolution contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the request-to-product resolution contract.")

    product_target = str(resolution.get("product", "")).strip()
    if not product_target:
        raise ValueError("resolved product is required for the request-to-product resolution contract.")

    capability_target, capability_source = _select_capability_target(
        classification,
        dict(resolution.get("profile", {})),
    )
    requested_product = str(normalized_request.get("product", "")).strip()
    classified_product = str((classification or {}).get("product", "")).strip()
    rationale_codes = [
        "request_to_product_resolution_contract",
        "product_target_resolved_from_registry",
        "capability_target_selected_without_routing",
    ]
    if requested_product and requested_product != "unknown":
        product_source = "normalized_request.product"
        rationale_codes.append("product_target_from_request")
    else:
        product_source = "classification.product"
        rationale_codes.append("product_target_from_classification")

    return {
        "contract_id": f"request-to-product-resolution-{request_id}",
        "contract_version": "v0.5-slice-a",
        "request_id": request_id,
        "run_id": run_id,
        "resolution_scope": "request_to_product_only",
        "product_target": {
            "product": product_target,
            "product_type": str(resolution.get("product_type", "unknown")),
            "repo_boundary": str(resolution.get("repo_boundary", "unknown")),
            "status": str(resolution.get("status", "unknown")),
        },
        "capability_target": {
            "capability": capability_target,
            "source": capability_source,
        },
        "resolution_rationale": {
            "product_source": product_source,
            "requested_product": requested_product or "unspecified",
            "classified_product": classified_product or "unspecified",
            "profile_ref": str(resolution.get("profile_ref", "")),
            "registry_entry_ref": str(resolution.get("registry_entry_ref", "")),
            "policy_refs": list(resolution.get("policy_refs", [])),
            "rationale_codes": rationale_codes,
        },
        "traceability": {
            "manifest_id": manifest_id,
            "classification_request_type": str((classification or {}).get("request_type", "unknown")),
            "classification_execution_intent": str((classification or {}).get("execution_intent", "unknown")),
            "classification_capability": str((classification or {}).get("capability", "unspecified")),
            "profile_ref": str(resolution.get("profile_ref", "")),
            "repo_boundary": str(resolution.get("repo_boundary", "unknown")),
        },
        "notes": [
            "This contract resolves request intent to a product target and capability target only.",
            "It is distinct from classification, routing, provider selection, and broader orchestration.",
        ],
    }


def build_resolution_to_handoff_intent_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    classification: dict[str, Any] | None,
    resolution_contract: dict[str, Any],
    manifest_id: str = "",
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice B resolution-to-handoff intent contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the resolution-to-handoff intent contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the resolution-to-handoff intent contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    if not resolution_contract_id:
        raise ValueError("Slice A resolution contract is required for the resolution-to-handoff intent contract.")

    product_target = str(resolution_contract.get("product_target", {}).get("product", "")).strip()
    capability_target = str(resolution_contract.get("capability_target", {}).get("capability", "")).strip()
    if not product_target or not capability_target:
        raise ValueError("Resolved product and capability targets are required for the handoff intent contract.")

    execution_intent = str((classification or {}).get("execution_intent", "unknown")).strip() or "unknown"
    request_type = str((classification or {}).get("request_type", "unknown")).strip() or "unknown"
    rationale_codes = [
        "resolution_to_handoff_intent_contract",
        "handoff_preparation_without_routing_selection",
        "handoff_target_inherited_from_resolution_contract",
    ]

    return {
        "contract_id": f"resolution-to-handoff-intent-{request_id}",
        "contract_version": "v0.5-slice-b",
        "request_id": request_id,
        "run_id": run_id,
        "handoff_scope": "resolution_to_handoff_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "contract_version": str(resolution_contract.get("contract_version", "")),
            "resolution_scope": str(resolution_contract.get("resolution_scope", "")),
            "product_target": product_target,
            "capability_target": capability_target,
        },
        "handoff_intent": {
            "intent": "prepare_structured_product_handoff",
            "intent_stage": "pre_routing",
            "target_product": product_target,
            "target_capability": capability_target,
            "execution_intent": execution_intent,
        },
        "handoff_rationale": {
            "request_type": request_type,
            "execution_intent": execution_intent,
            "rationale_codes": rationale_codes,
            "summary": "ATP is preparing a bounded handoff intent toward the resolved product/capability target.",
        },
        "traceability": {
            "manifest_id": manifest_id,
            "request_to_product_resolution_contract_id": resolution_contract_id,
            "classification_request_type": request_type,
            "classification_execution_intent": execution_intent,
        },
        "notes": [
            "This contract prepares handoff intent only.",
            "It is distinct from classification, routing, provider selection, and broader orchestration.",
        ],
    }


def build_product_execution_preparation_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    task_manifest: dict[str, Any],
    product_context: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice C product execution preparation contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the product execution preparation contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the product execution preparation contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    if not resolution_contract_id or not handoff_intent_contract_id:
        raise ValueError("Slice A and Slice B contracts are required for the execution preparation contract.")

    manifest_id = str(task_manifest.get("manifest_id", "")).strip()
    product_target = str(resolution_contract.get("product_target", {}).get("product", "")).strip()
    capability_target = str(resolution_contract.get("capability_target", {}).get("capability", "")).strip()
    handoff_intent = str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")).strip()
    profile_ref = str(product_context.get("profile_ref", "")).strip()
    evidence_bundle_id = str(evidence_bundle.get("bundle_id", "")).strip()
    if not manifest_id or not product_target or not capability_target or not handoff_intent or not profile_ref:
        raise ValueError("Task manifest, resolved target, handoff intent, and product context are required.")

    return {
        "contract_id": f"product-execution-preparation-{request_id}",
        "contract_version": "v0.5-slice-c",
        "request_id": request_id,
        "run_id": run_id,
        "preparation_scope": "product_execution_preparation_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "resolution_scope": str(resolution_contract.get("resolution_scope", "")),
            "product_target": product_target,
            "capability_target": capability_target,
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_scope": str(handoff_intent_contract.get("handoff_scope", "")),
            "handoff_intent": handoff_intent,
        },
        "execution_preparation": {
            "preparation_mode": "pre_routing_pre_provider",
            "target_product": product_target,
            "target_capability": capability_target,
            "task_manifest_id": manifest_id,
            "product_context_profile": profile_ref,
            "evidence_bundle_id": evidence_bundle_id,
            "required_capabilities": list(task_manifest.get("required_capabilities", [])),
        },
        "preparation_rationale": {
            "rationale_codes": [
                "product_execution_preparation_contract",
                "pre_routing_pre_provider_preparation_only",
                "preparation_package_composed_from_manifest_context_evidence",
            ],
            "summary": "ATP is preparing a bounded execution package before routing, provider selection, and execution.",
            "module_scope_count": len(list(product_context.get("module_scope", []))),
            "selected_evidence_count": len(list(evidence_bundle.get("selected_artifacts", []))),
        },
        "traceability": {
            "task_manifest_id": manifest_id,
            "product_context_profile": profile_ref,
            "evidence_bundle_id": evidence_bundle_id,
            "request_to_product_resolution_contract_id": resolution_contract_id,
            "resolution_to_handoff_intent_contract_id": handoff_intent_contract_id,
        },
        "notes": [
            "This contract prepares a product execution package only.",
            "It is distinct from handoff intent, routing, provider selection, execution result, and broader orchestration.",
        ],
    }


def build_product_execution_result_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    execution_preparation_contract: dict[str, Any],
    execution_result: dict[str, Any],
    artifact_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.5 Slice D product execution result contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the product execution result contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the product execution result contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    execution_preparation_contract_id = str(execution_preparation_contract.get("contract_id", "")).strip()
    if not resolution_contract_id or not handoff_intent_contract_id or not execution_preparation_contract_id:
        raise ValueError("Slice A-C contracts are required for the product execution result contract.")

    execution_id = str(execution_result.get("execution_id", "")).strip()
    execution_status = str(execution_result.get("status", "")).strip()
    if not execution_id or not execution_status:
        raise ValueError("execution result payload is required for the product execution result contract.")

    return {
        "contract_id": f"product-execution-result-{request_id}",
        "contract_version": "v0.5-slice-d",
        "request_id": request_id,
        "run_id": run_id,
        "result_scope": "product_execution_result_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "product_target": str(resolution_contract.get("product_target", {}).get("product", "")),
            "capability_target": str(resolution_contract.get("capability_target", {}).get("capability", "")),
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_intent": str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")),
        },
        "product_execution_preparation_ref": {
            "contract_id": execution_preparation_contract_id,
            "preparation_mode": str(execution_preparation_contract.get("execution_preparation", {}).get("preparation_mode", "")),
        },
        "execution_result": {
            "execution_id": execution_id,
            "status": execution_status,
            "exit_code": int(execution_result.get("exit_code", -1)),
            "command": list(execution_result.get("command", [])),
            "stdout_preview": _compact_text(str(execution_result.get("stdout", ""))),
            "stderr_preview": _compact_text(str(execution_result.get("stderr", ""))),
        },
        "result_summary": {
            "summary": "ATP is recording the bounded result of the prepared product execution step.",
            "rationale_codes": [
                "product_execution_result_contract",
                "bounded_result_recording_only",
                "post_execution_preparation_pre_review_record",
            ],
            "artifact_count": len(list(artifact_summary.get("artifact_ids", []))),
        },
        "traceability": {
            "execution_id": execution_id,
            "request_to_product_resolution_contract_id": resolution_contract_id,
            "resolution_to_handoff_intent_contract_id": handoff_intent_contract_id,
            "product_execution_preparation_contract_id": execution_preparation_contract_id,
            "artifact_ids": list(artifact_summary.get("artifact_ids", [])),
        },
        "notes": [
            "This contract records a bounded execution result only.",
            "It is distinct from routing, provider selection, approval, recovery, and broader orchestration.",
        ],
    }


def build_post_execution_decision_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    execution_preparation_contract: dict[str, Any],
    execution_result_contract: dict[str, Any],
    review_decision: dict[str, Any],
    approval_result: dict[str, Any],
    close_decision: str,
) -> dict[str, Any]:
    """Build the explicit v0.6 Slice A post-execution decision contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the post-execution decision contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the post-execution decision contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    execution_preparation_contract_id = str(execution_preparation_contract.get("contract_id", "")).strip()
    execution_result_contract_id = str(execution_result_contract.get("contract_id", "")).strip()
    if (
        not resolution_contract_id
        or not handoff_intent_contract_id
        or not execution_preparation_contract_id
        or not execution_result_contract_id
    ):
        raise ValueError("Slice A-D contracts are required for the post-execution decision contract.")

    review_status = str(review_decision.get("review_status", "unknown")).strip() or "unknown"
    approval_status = str(approval_result.get("approval_status", "unknown")).strip() or "unknown"
    if not str(close_decision).strip():
        raise ValueError("close_decision is required for the post-execution decision contract.")

    review_followup_action = "escalate_review" if close_decision == "continue_pending" else "none"
    return {
        "contract_id": f"post-execution-decision-{request_id}",
        "contract_version": "v0.6-slice-a",
        "request_id": request_id,
        "run_id": run_id,
        "decision_scope": "post_execution_decision_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "product_target": str(resolution_contract.get("product_target", {}).get("product", "")),
            "capability_target": str(resolution_contract.get("capability_target", {}).get("capability", "")),
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_intent": str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")),
        },
        "product_execution_preparation_ref": {
            "contract_id": execution_preparation_contract_id,
            "preparation_mode": str(execution_preparation_contract.get("execution_preparation", {}).get("preparation_mode", "")),
        },
        "product_execution_result_ref": {
            "contract_id": execution_result_contract_id,
            "execution_id": str(execution_result_contract.get("execution_result", {}).get("execution_id", "")),
            "execution_status": str(execution_result_contract.get("execution_result", {}).get("status", "")),
        },
        "post_execution_decision": {
            "decision_stage": "post_execution",
            "bounded_outcome": close_decision,
            "review_followup_action": review_followup_action,
            "review_status": review_status,
            "approval_status": approval_status,
        },
        "decision_rationale": {
            "validation_status": str(review_decision.get("validation_status", "unknown")),
            "review_status": review_status,
            "approval_status": approval_status,
            "continue_recommended": bool(approval_result.get("continue_recommended", False)),
            "rationale_codes": [
                "post_execution_decision_contract",
                "bounded_post_execution_decision_only",
                "decision_derived_from_review_approval_close_semantics",
            ],
            "summary": "ATP is recording the bounded post-execution decision only.",
        },
        "traceability": {
            "product_execution_result_contract_id": execution_result_contract_id,
            "review_decision_id": str(review_decision.get("decision_id", "")),
            "approval_id": str(approval_result.get("approval_id", "")),
            "close_or_continue": close_decision,
        },
        "notes": [
            "This contract records a bounded post-execution decision only.",
            "It is distinct from approval UI, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_decision_to_closure_continuation_handoff_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    execution_preparation_contract: dict[str, Any],
    execution_result_contract: dict[str, Any],
    post_execution_decision_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.6 Slice B decision-to-closure/continuation handoff contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the decision-to-handoff contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the decision-to-handoff contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    execution_preparation_contract_id = str(execution_preparation_contract.get("contract_id", "")).strip()
    execution_result_contract_id = str(execution_result_contract.get("contract_id", "")).strip()
    post_execution_decision_contract_id = str(post_execution_decision_contract.get("contract_id", "")).strip()
    if (
        not resolution_contract_id
        or not handoff_intent_contract_id
        or not execution_preparation_contract_id
        or not execution_result_contract_id
        or not post_execution_decision_contract_id
    ):
        raise ValueError("Slice A-D and v0.6 Slice A contracts are required for the decision-to-handoff contract.")

    bounded_outcome = str(
        post_execution_decision_contract.get("post_execution_decision", {}).get("bounded_outcome", "")
    ).strip()
    review_followup_action = str(
        post_execution_decision_contract.get("post_execution_decision", {}).get("review_followup_action", "")
    ).strip() or "none"
    review_status = str(
        post_execution_decision_contract.get("post_execution_decision", {}).get("review_status", "unknown")
    ).strip() or "unknown"
    approval_status = str(
        post_execution_decision_contract.get("post_execution_decision", {}).get("approval_status", "unknown")
    ).strip() or "unknown"
    if not bounded_outcome:
        raise ValueError("bounded post-execution outcome is required for the decision-to-handoff contract.")

    next_record_type_map = {
        "close": "closure_record",
        "close_rejected": "rejected_closure_record",
        "continue_pending": "continuation_record",
    }
    next_record_type = next_record_type_map.get(bounded_outcome, "undetermined")

    return {
        "contract_id": f"decision-to-closure-continuation-handoff-{request_id}",
        "contract_version": "v0.6-slice-b",
        "request_id": request_id,
        "run_id": run_id,
        "handoff_scope": "decision_to_closure_continuation_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "product_target": str(resolution_contract.get("product_target", {}).get("product", "")),
            "capability_target": str(resolution_contract.get("capability_target", {}).get("capability", "")),
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_intent": str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")),
        },
        "product_execution_preparation_ref": {
            "contract_id": execution_preparation_contract_id,
            "preparation_mode": str(
                execution_preparation_contract.get("execution_preparation", {}).get("preparation_mode", "")
            ),
        },
        "product_execution_result_ref": {
            "contract_id": execution_result_contract_id,
            "execution_id": str(execution_result_contract.get("execution_result", {}).get("execution_id", "")),
            "execution_status": str(execution_result_contract.get("execution_result", {}).get("status", "")),
        },
        "post_execution_decision_ref": {
            "contract_id": post_execution_decision_contract_id,
            "decision_scope": str(post_execution_decision_contract.get("decision_scope", "")),
            "bounded_outcome": bounded_outcome,
            "review_followup_action": review_followup_action,
        },
        "closure_or_continuation_handoff": {
            "handoff_stage": "post_execution_transition",
            "bounded_next_path": bounded_outcome,
            "next_record_type": next_record_type,
            "review_escalation_mode": review_followup_action,
            "handoff_readiness": "ready_for_bounded_transition",
        },
        "handoff_rationale": {
            "review_status": review_status,
            "approval_status": approval_status,
            "rationale_codes": [
                "decision_to_closure_continuation_handoff_contract",
                "bounded_transition_handoff_only",
                "handoff_derived_from_post_execution_decision",
            ],
            "summary": "ATP is handing a bounded post-execution decision into a closure or continuation path only.",
        },
        "traceability": {
            "post_execution_decision_contract_id": post_execution_decision_contract_id,
            "product_execution_result_contract_id": execution_result_contract_id,
            "review_decision_id": str(post_execution_decision_contract.get("traceability", {}).get("review_decision_id", "")),
            "approval_id": str(post_execution_decision_contract.get("traceability", {}).get("approval_id", "")),
            "close_or_continue": bounded_outcome,
        },
        "notes": [
            "This contract hands a bounded post-execution decision into a closure or continuation path only.",
            "It is distinct from approval UI, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_closure_continuation_state_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    resolution_contract: dict[str, Any],
    handoff_intent_contract: dict[str, Any],
    execution_preparation_contract: dict[str, Any],
    execution_result_contract: dict[str, Any],
    post_execution_decision_contract: dict[str, Any],
    decision_to_handoff_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.6 Slice C closure/continuation state contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the closure/continuation state contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the closure/continuation state contract.")

    resolution_contract_id = str(resolution_contract.get("contract_id", "")).strip()
    handoff_intent_contract_id = str(handoff_intent_contract.get("contract_id", "")).strip()
    execution_preparation_contract_id = str(execution_preparation_contract.get("contract_id", "")).strip()
    execution_result_contract_id = str(execution_result_contract.get("contract_id", "")).strip()
    post_execution_decision_contract_id = str(post_execution_decision_contract.get("contract_id", "")).strip()
    decision_to_handoff_contract_id = str(decision_to_handoff_contract.get("contract_id", "")).strip()
    if (
        not resolution_contract_id
        or not handoff_intent_contract_id
        or not execution_preparation_contract_id
        or not execution_result_contract_id
        or not post_execution_decision_contract_id
        or not decision_to_handoff_contract_id
    ):
        raise ValueError("Slice A-D and v0.6 Slice A-B contracts are required for the closure/continuation state contract.")

    bounded_next_path = str(
        decision_to_handoff_contract.get("closure_or_continuation_handoff", {}).get("bounded_next_path", "")
    ).strip()
    review_escalation_mode = str(
        decision_to_handoff_contract.get("closure_or_continuation_handoff", {}).get("review_escalation_mode", "")
    ).strip() or "none"
    if not bounded_next_path:
        raise ValueError("bounded next path is required for the closure/continuation state contract.")

    state_status_map = {
        "close": "closed",
        "close_rejected": "closed_rejected",
        "continue_pending": "continuation_pending",
    }
    state_status = state_status_map.get(bounded_next_path, "undetermined")
    continuation_required = bounded_next_path == "continue_pending"

    return {
        "contract_id": f"closure-continuation-state-{request_id}",
        "contract_version": "v0.6-slice-c",
        "request_id": request_id,
        "run_id": run_id,
        "state_scope": "closure_continuation_state_only",
        "request_to_product_resolution_ref": {
            "contract_id": resolution_contract_id,
            "product_target": str(resolution_contract.get("product_target", {}).get("product", "")),
            "capability_target": str(resolution_contract.get("capability_target", {}).get("capability", "")),
        },
        "resolution_to_handoff_intent_ref": {
            "contract_id": handoff_intent_contract_id,
            "handoff_intent": str(handoff_intent_contract.get("handoff_intent", {}).get("intent", "")),
        },
        "product_execution_preparation_ref": {
            "contract_id": execution_preparation_contract_id,
            "preparation_mode": str(
                execution_preparation_contract.get("execution_preparation", {}).get("preparation_mode", "")
            ),
        },
        "product_execution_result_ref": {
            "contract_id": execution_result_contract_id,
            "execution_id": str(execution_result_contract.get("execution_result", {}).get("execution_id", "")),
            "execution_status": str(execution_result_contract.get("execution_result", {}).get("status", "")),
        },
        "post_execution_decision_ref": {
            "contract_id": post_execution_decision_contract_id,
            "bounded_outcome": str(
                post_execution_decision_contract.get("post_execution_decision", {}).get("bounded_outcome", "")
            ),
        },
        "decision_to_closure_continuation_handoff_ref": {
            "contract_id": decision_to_handoff_contract_id,
            "handoff_scope": str(decision_to_handoff_contract.get("handoff_scope", "")),
            "bounded_next_path": bounded_next_path,
        },
        "closure_or_continuation_state": {
            "state_stage": "post_handoff_state",
            "bounded_path": bounded_next_path,
            "state_status": state_status,
            "continuation_required": continuation_required,
            "review_escalation_active": review_escalation_mode == "escalate_review",
        },
        "state_rationale": {
            "review_escalation_mode": review_escalation_mode,
            "rationale_codes": [
                "closure_continuation_state_contract",
                "bounded_state_record_only",
                "state_derived_from_decision_to_handoff_contract",
            ],
            "summary": "ATP is recording the bounded state of the selected closure or continuation path only.",
        },
        "traceability": {
            "decision_to_closure_continuation_handoff_contract_id": decision_to_handoff_contract_id,
            "post_execution_decision_contract_id": post_execution_decision_contract_id,
            "product_execution_result_contract_id": execution_result_contract_id,
            "close_or_continue": bounded_next_path,
        },
        "notes": [
            "This contract records a bounded closure or continuation state only.",
            "It is distinct from approval UI, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_finalization_closure_record_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    execution_result_contract: dict[str, Any],
    post_execution_decision_contract: dict[str, Any],
    decision_to_handoff_contract: dict[str, Any],
    closure_continuation_state_contract: dict[str, Any],
    finalization_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v0.7 Slice A finalization/closure record contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the finalization/closure record contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the finalization/closure record contract.")

    execution_result_contract_id = str(execution_result_contract.get("contract_id", "")).strip()
    post_execution_decision_contract_id = str(post_execution_decision_contract.get("contract_id", "")).strip()
    decision_to_handoff_contract_id = str(decision_to_handoff_contract.get("contract_id", "")).strip()
    closure_continuation_state_contract_id = str(closure_continuation_state_contract.get("contract_id", "")).strip()
    if (
        not execution_result_contract_id
        or not post_execution_decision_contract_id
        or not decision_to_handoff_contract_id
        or not closure_continuation_state_contract_id
    ):
        raise ValueError("v0.5 Slice D and v0.6 Slice A-C contracts are required for the finalization/closure record contract.")

    bounded_path = str(
        closure_continuation_state_contract.get("closure_or_continuation_state", {}).get("bounded_path", "")
    ).strip()
    state_status = str(
        closure_continuation_state_contract.get("closure_or_continuation_state", {}).get("state_status", "unknown")
    ).strip() or "unknown"
    continuation_required = bool(
        closure_continuation_state_contract.get("closure_or_continuation_state", {}).get("continuation_required", False)
    )
    final_status = str(finalization_summary.get("final_status", "unknown")).strip() or "unknown"
    finalization_id = str(finalization_summary.get("finalization_id", "")).strip()
    if not bounded_path or not finalization_id:
        raise ValueError("bounded closure state and finalization summary are required for the finalization/closure record contract.")

    record_status_map = {
        "close": "closure_record_finalized",
        "close_rejected": "rejected_closure_record_finalized",
        "continue_pending": "continuation_record_finalized",
    }
    record_status = record_status_map.get(bounded_path, "undetermined")

    return {
        "contract_id": f"finalization-closure-record-{request_id}",
        "contract_version": "v0.7-slice-a",
        "request_id": request_id,
        "run_id": run_id,
        "record_scope": "finalization_closure_record_only",
        "product_execution_result_ref": {
            "contract_id": execution_result_contract_id,
            "execution_id": str(execution_result_contract.get("execution_result", {}).get("execution_id", "")),
            "execution_status": str(execution_result_contract.get("execution_result", {}).get("status", "")),
        },
        "post_execution_decision_ref": {
            "contract_id": post_execution_decision_contract_id,
            "bounded_outcome": str(
                post_execution_decision_contract.get("post_execution_decision", {}).get("bounded_outcome", "")
            ),
        },
        "decision_to_closure_continuation_handoff_ref": {
            "contract_id": decision_to_handoff_contract_id,
            "bounded_next_path": str(
                decision_to_handoff_contract.get("closure_or_continuation_handoff", {}).get("bounded_next_path", "")
            ),
        },
        "closure_continuation_state_ref": {
            "contract_id": closure_continuation_state_contract_id,
            "state_scope": str(closure_continuation_state_contract.get("state_scope", "")),
            "bounded_path": bounded_path,
            "state_status": state_status,
        },
        "finalization_or_closure_record": {
            "record_stage": "finalization_closure",
            "bounded_path": bounded_path,
            "record_status": record_status,
            "final_status": final_status,
            "continuation_required": continuation_required,
        },
        "record_rationale": {
            "finalization_id": finalization_id,
            "validation_status": str(finalization_summary.get("validation_status", "unknown")),
            "review_status": str(finalization_summary.get("review_status", "unknown")),
            "approval_status": str(finalization_summary.get("approval_status", "unknown")),
            "rationale_codes": [
                "finalization_closure_record_contract",
                "bounded_finalization_record_only",
                "record_derived_from_closure_state_and_finalization_summary",
            ],
            "summary": "ATP is recording a bounded finalization or closure record only.",
        },
        "traceability": {
            "finalization_id": finalization_id,
            "closure_continuation_state_contract_id": closure_continuation_state_contract_id,
            "decision_to_closure_continuation_handoff_contract_id": decision_to_handoff_contract_id,
            "post_execution_decision_contract_id": post_execution_decision_contract_id,
            "product_execution_result_contract_id": execution_result_contract_id,
            "close_or_continue": bounded_path,
        },
        "notes": [
            "This contract records a bounded finalization or closure record only.",
            "It is distinct from approval UI, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_review_approval_gate_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    execution_result_contract: dict[str, Any],
    post_execution_decision_contract: dict[str, Any],
    decision_to_handoff_contract: dict[str, Any],
    closure_continuation_state_contract: dict[str, Any],
    finalization_closure_record_contract: dict[str, Any],
    review_decision: dict[str, Any],
    approval_result: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v1.0 Slice A review/approval gate contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the review/approval gate contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the review/approval gate contract.")

    execution_result_contract_id = str(execution_result_contract.get("contract_id", "")).strip()
    post_execution_decision_contract_id = str(post_execution_decision_contract.get("contract_id", "")).strip()
    decision_to_handoff_contract_id = str(decision_to_handoff_contract.get("contract_id", "")).strip()
    closure_continuation_state_contract_id = str(closure_continuation_state_contract.get("contract_id", "")).strip()
    finalization_closure_record_contract_id = str(finalization_closure_record_contract.get("contract_id", "")).strip()
    if (
        not execution_result_contract_id
        or not post_execution_decision_contract_id
        or not decision_to_handoff_contract_id
        or not closure_continuation_state_contract_id
        or not finalization_closure_record_contract_id
    ):
        raise ValueError(
            "v0.5 Slice D, v0.6 Slice A-C, and v0.7 Slice A contracts are required for the review/approval gate contract."
        )

    bounded_path = str(
        finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("bounded_path", "")
    ).strip()
    record_status = str(
        finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("record_status", "unknown")
    ).strip() or "unknown"
    final_status = str(
        finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("final_status", "unknown")
    ).strip() or "unknown"
    review_status = str(review_decision.get("review_status", "unknown")).strip() or "unknown"
    validation_status = str(review_decision.get("validation_status", "unknown")).strip() or "unknown"
    approval_status = str(approval_result.get("approval_status", "unknown")).strip() or "unknown"
    review_decision_id = str(review_decision.get("decision_id", "")).strip()
    approval_id = str(approval_result.get("approval_id", "")).strip()
    if not bounded_path:
        raise ValueError("finalization/closure record bounded path is required for the review/approval gate contract.")

    if approval_status == "approved":
        gate_decision = "approved"
        gate_status = "passed"
        resulting_direction = "ready_for_approved_continuation"
    elif approval_status == "rejected" or review_status == "reject":
        gate_decision = "rejected"
        gate_status = "rejected"
        resulting_direction = "ready_for_rejected_closure"
    elif approval_status == "needs_attention":
        gate_decision = "hold"
        gate_status = "held"
        resulting_direction = "pending_further_review"
    else:
        gate_decision = "deferred"
        gate_status = "deferred"
        resulting_direction = "decision_deferred"

    return {
        "contract_id": f"review-approval-gate-{request_id}",
        "contract_version": "v1.0-slice-a",
        "request_id": request_id,
        "run_id": run_id,
        "gate_scope": "review_approval_gate_only",
        "product_execution_result_ref": {
            "contract_id": execution_result_contract_id,
            "execution_id": str(execution_result_contract.get("execution_result", {}).get("execution_id", "")),
            "execution_status": str(execution_result_contract.get("execution_result", {}).get("status", "")),
        },
        "post_execution_decision_ref": {
            "contract_id": post_execution_decision_contract_id,
            "bounded_outcome": str(
                post_execution_decision_contract.get("post_execution_decision", {}).get("bounded_outcome", "")
            ),
        },
        "decision_to_closure_continuation_handoff_ref": {
            "contract_id": decision_to_handoff_contract_id,
            "bounded_next_path": str(
                decision_to_handoff_contract.get("closure_or_continuation_handoff", {}).get("bounded_next_path", "")
            ),
        },
        "closure_continuation_state_ref": {
            "contract_id": closure_continuation_state_contract_id,
            "bounded_path": str(
                closure_continuation_state_contract.get("closure_or_continuation_state", {}).get("bounded_path", "")
            ),
            "state_status": str(
                closure_continuation_state_contract.get("closure_or_continuation_state", {}).get("state_status", "")
            ),
        },
        "finalization_closure_record_ref": {
            "contract_id": finalization_closure_record_contract_id,
            "record_scope": str(finalization_closure_record_contract.get("record_scope", "")),
            "bounded_path": bounded_path,
            "record_status": record_status,
            "final_status": final_status,
        },
        "review_or_approval_gate": {
            "gate_stage": "post_finalization_review_gate",
            "gate_subject": "finalization_closure_record",
            "gate_decision": gate_decision,
            "gate_status": gate_status,
            "resulting_direction": resulting_direction,
        },
        "gate_rationale": {
            "validation_status": validation_status,
            "review_status": review_status,
            "approval_status": approval_status,
            "rationale_codes": [
                "review_approval_gate_contract",
                "bounded_operational_gate_only",
                "gate_derived_from_finalization_record_and_review_approval_state",
            ],
            "summary": "ATP is recording a bounded review or approval gate only.",
        },
        "traceability": {
            "finalization_closure_record_contract_id": finalization_closure_record_contract_id,
            "closure_continuation_state_contract_id": closure_continuation_state_contract_id,
            "decision_to_closure_continuation_handoff_contract_id": decision_to_handoff_contract_id,
            "post_execution_decision_contract_id": post_execution_decision_contract_id,
            "product_execution_result_contract_id": execution_result_contract_id,
            "review_decision_id": review_decision_id,
            "approval_id": approval_id,
            "close_or_continue": bounded_path,
        },
        "notes": [
            "This contract records a bounded review or approval gate only.",
            "It is distinct from approval UI, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_gate_outcome_operational_followup_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    finalization_closure_record_contract: dict[str, Any],
    review_approval_gate_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v1.0 Slice B gate outcome / operational follow-up contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the gate outcome / operational follow-up contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the gate outcome / operational follow-up contract.")

    finalization_closure_record_contract_id = str(finalization_closure_record_contract.get("contract_id", "")).strip()
    review_approval_gate_contract_id = str(review_approval_gate_contract.get("contract_id", "")).strip()
    if not finalization_closure_record_contract_id or not review_approval_gate_contract_id:
        raise ValueError(
            "v0.7 Slice A and v1.0 Slice A contracts are required for the gate outcome / operational follow-up contract."
        )

    bounded_path = str(
        finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("bounded_path", "")
    ).strip()
    final_status = str(
        finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("final_status", "unknown")
    ).strip() or "unknown"
    gate_decision = str(
        review_approval_gate_contract.get("review_or_approval_gate", {}).get("gate_decision", "unknown")
    ).strip() or "unknown"
    gate_status = str(
        review_approval_gate_contract.get("review_or_approval_gate", {}).get("gate_status", "unknown")
    ).strip() or "unknown"
    resulting_direction = str(
        review_approval_gate_contract.get("review_or_approval_gate", {}).get("resulting_direction", "unknown")
    ).strip() or "unknown"
    validation_status = str(
        review_approval_gate_contract.get("gate_rationale", {}).get("validation_status", "unknown")
    ).strip() or "unknown"
    review_status = str(
        review_approval_gate_contract.get("gate_rationale", {}).get("review_status", "unknown")
    ).strip() or "unknown"
    approval_status = str(
        review_approval_gate_contract.get("gate_rationale", {}).get("approval_status", "unknown")
    ).strip() or "unknown"
    review_decision_id = str(review_approval_gate_contract.get("traceability", {}).get("review_decision_id", "")).strip()
    approval_id = str(review_approval_gate_contract.get("traceability", {}).get("approval_id", "")).strip()
    if not bounded_path:
        raise ValueError(
            "finalization/closure record bounded path is required for the gate outcome / operational follow-up contract."
        )

    if gate_decision == "approved":
        bounded_followup = "approved_operational_followup"
        followup_status = "operationally_ready"
        continuity_signal = "approved_continuation_available"
    elif gate_decision == "rejected":
        bounded_followup = "rejected_operational_followup"
        followup_status = "operationally_closed"
        continuity_signal = "rejected_closure_confirmed"
    elif gate_decision == "hold":
        bounded_followup = "held_operational_followup"
        followup_status = "operationally_pending"
        continuity_signal = "followup_pending_review"
    else:
        bounded_followup = "deferred_operational_followup"
        followup_status = "operationally_deferred"
        continuity_signal = "followup_deferred"

    return {
        "contract_id": f"gate-outcome-operational-followup-{request_id}",
        "contract_version": "v1.0-slice-b",
        "request_id": request_id,
        "run_id": run_id,
        "followup_scope": "gate_outcome_operational_followup_only",
        "finalization_closure_record_ref": {
            "contract_id": finalization_closure_record_contract_id,
            "record_scope": str(finalization_closure_record_contract.get("record_scope", "")),
            "bounded_path": bounded_path,
            "final_status": final_status,
        },
        "review_approval_gate_ref": {
            "contract_id": review_approval_gate_contract_id,
            "gate_scope": str(review_approval_gate_contract.get("gate_scope", "")),
            "gate_decision": gate_decision,
            "gate_status": gate_status,
            "resulting_direction": resulting_direction,
        },
        "gate_outcome_or_operational_followup": {
            "followup_stage": "post_gate_operational_followup",
            "bounded_followup": bounded_followup,
            "followup_status": followup_status,
            "continuity_signal": continuity_signal,
            "close_or_continue": bounded_path,
        },
        "followup_rationale": {
            "validation_status": validation_status,
            "review_status": review_status,
            "approval_status": approval_status,
            "rationale_codes": [
                "gate_outcome_operational_followup_contract",
                "bounded_operational_followup_only",
                "followup_derived_from_gate_decision_and_finalization_record",
            ],
            "summary": "ATP is recording a bounded gate outcome or operational follow-up only.",
        },
        "traceability": {
            "review_approval_gate_contract_id": review_approval_gate_contract_id,
            "finalization_closure_record_contract_id": finalization_closure_record_contract_id,
            "review_decision_id": review_decision_id,
            "approval_id": approval_id,
            "close_or_continue": bounded_path,
        },
        "notes": [
            "This contract records a bounded gate outcome or operational follow-up only.",
            "It is distinct from approval UI, workflow engines, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }


def build_operational_continuity_gate_followup_state_contract(
    run_id: str,
    normalized_request: dict[str, Any],
    finalization_closure_record_contract: dict[str, Any],
    review_approval_gate_contract: dict[str, Any],
    gate_outcome_operational_followup_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build the explicit v1.0 Slice C operational continuity / gate follow-up state contract."""

    request_id = str(normalized_request.get("request_id", "")).strip()
    if not request_id:
        raise ValueError("request_id is required for the operational continuity / gate follow-up state contract.")

    if not str(run_id).strip():
        raise ValueError("run_id is required for the operational continuity / gate follow-up state contract.")

    finalization_closure_record_contract_id = str(finalization_closure_record_contract.get("contract_id", "")).strip()
    review_approval_gate_contract_id = str(review_approval_gate_contract.get("contract_id", "")).strip()
    gate_outcome_operational_followup_contract_id = str(
        gate_outcome_operational_followup_contract.get("contract_id", "")
    ).strip()
    if (
        not finalization_closure_record_contract_id
        or not review_approval_gate_contract_id
        or not gate_outcome_operational_followup_contract_id
    ):
        raise ValueError(
            "v0.7 Slice A, v1.0 Slice A, and v1.0 Slice B contracts are required for the operational continuity / gate follow-up state contract."
        )

    bounded_path = str(
        gate_outcome_operational_followup_contract.get("gate_outcome_or_operational_followup", {}).get(
            "close_or_continue", ""
        )
    ).strip()
    bounded_followup = str(
        gate_outcome_operational_followup_contract.get("gate_outcome_or_operational_followup", {}).get(
            "bounded_followup", "unknown"
        )
    ).strip() or "unknown"
    followup_status = str(
        gate_outcome_operational_followup_contract.get("gate_outcome_or_operational_followup", {}).get(
            "followup_status", "unknown"
        )
    ).strip() or "unknown"
    continuity_signal = str(
        gate_outcome_operational_followup_contract.get("gate_outcome_or_operational_followup", {}).get(
            "continuity_signal", "unknown"
        )
    ).strip() or "unknown"
    validation_status = str(
        gate_outcome_operational_followup_contract.get("followup_rationale", {}).get("validation_status", "unknown")
    ).strip() or "unknown"
    review_status = str(
        gate_outcome_operational_followup_contract.get("followup_rationale", {}).get("review_status", "unknown")
    ).strip() or "unknown"
    approval_status = str(
        gate_outcome_operational_followup_contract.get("followup_rationale", {}).get("approval_status", "unknown")
    ).strip() or "unknown"
    review_decision_id = str(
        gate_outcome_operational_followup_contract.get("traceability", {}).get("review_decision_id", "")
    ).strip()
    approval_id = str(
        gate_outcome_operational_followup_contract.get("traceability", {}).get("approval_id", "")
    ).strip()
    if not bounded_path:
        raise ValueError(
            "follow-up close_or_continue value is required for the operational continuity / gate follow-up state contract."
        )

    if bounded_followup == "approved_operational_followup":
        continuity_state = "approved_continuity_ready"
        state_status = "continuity_ready"
    elif bounded_followup == "rejected_operational_followup":
        continuity_state = "rejected_continuity_closed"
        state_status = "continuity_closed"
    elif bounded_followup == "held_operational_followup":
        continuity_state = "held_continuity_pending"
        state_status = "continuity_pending"
    else:
        continuity_state = "deferred_continuity_deferred"
        state_status = "continuity_deferred"

    return {
        "contract_id": f"operational-continuity-gate-followup-state-{request_id}",
        "contract_version": "v1.0-slice-c",
        "request_id": request_id,
        "run_id": run_id,
        "state_scope": "operational_continuity_gate_followup_state_only",
        "finalization_closure_record_ref": {
            "contract_id": finalization_closure_record_contract_id,
            "record_scope": str(finalization_closure_record_contract.get("record_scope", "")),
            "bounded_path": str(
                finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("bounded_path", "")
            ),
            "final_status": str(
                finalization_closure_record_contract.get("finalization_or_closure_record", {}).get("final_status", "")
            ),
        },
        "review_approval_gate_ref": {
            "contract_id": review_approval_gate_contract_id,
            "gate_scope": str(review_approval_gate_contract.get("gate_scope", "")),
            "gate_decision": str(
                review_approval_gate_contract.get("review_or_approval_gate", {}).get("gate_decision", "")
            ),
            "gate_status": str(
                review_approval_gate_contract.get("review_or_approval_gate", {}).get("gate_status", "")
            ),
        },
        "gate_outcome_operational_followup_ref": {
            "contract_id": gate_outcome_operational_followup_contract_id,
            "followup_scope": str(gate_outcome_operational_followup_contract.get("followup_scope", "")),
            "bounded_followup": bounded_followup,
            "followup_status": followup_status,
        },
        "operational_continuity_state": {
            "state_stage": "post_gate_operational_continuity",
            "continuity_state": continuity_state,
            "state_status": state_status,
            "continuity_signal": continuity_signal,
            "close_or_continue": bounded_path,
        },
        "state_rationale": {
            "validation_status": validation_status,
            "review_status": review_status,
            "approval_status": approval_status,
            "rationale_codes": [
                "operational_continuity_gate_followup_state_contract",
                "bounded_operational_continuity_state_only",
                "state_derived_from_gate_followup_and_gate_traceability",
            ],
            "summary": "ATP is recording a bounded operational continuity or gate follow-up state only.",
        },
        "traceability": {
            "gate_outcome_operational_followup_contract_id": gate_outcome_operational_followup_contract_id,
            "review_approval_gate_contract_id": review_approval_gate_contract_id,
            "finalization_closure_record_contract_id": finalization_closure_record_contract_id,
            "review_decision_id": review_decision_id,
            "approval_id": approval_id,
            "close_or_continue": bounded_path,
        },
        "notes": [
            "This contract records a bounded operational continuity or gate follow-up state only.",
            "It is distinct from approval UI, workflow engines, recovery execution, routing, provider selection, and broader orchestration.",
        ],
    }
