"""ATP M1-M8 validate CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.approvals.approval_gate import require_approval
from core.approvals.decision_model import build_decision
from core.classification.classifier import classify_request
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.finalization.close_or_continue import close_or_continue
from core.intake.loader import RequestLoadError, load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import ProductResolutionError, resolve_product
from core.routing.route_prepare import RoutePreparationError, prepare_route
from core.routing.route_select import RouteSelectionError, select_route
from core.validation.validation_result import build_validation_result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview ATP v0 validation readiness without executing the request.")
    parser.add_argument("request_file", help="Path to a JSON or YAML request file.")
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


def validate_request(request_file: str) -> dict[str, Any]:
    """Load, normalize, classify, resolve, package context, route, and preview approval readiness."""

    raw_request = load_request(request_file)
    normalized_request = normalize_request(raw_request)
    classification = classify_request(normalized_request)
    resolution = resolve_product(normalized_request, classification)
    task_manifest = build_task_manifest(normalized_request, classification, resolution)
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
    prepared_route = prepare_route(
        normalized_request,
        classification,
        resolution,
        task_manifest,
        product_context,
        evidence_bundle,
    )
    routing_result = select_route(prepared_route)
    validation_preview = build_validation_result(
        request_id=normalized_request["request_id"],
        validation_status="incomplete",
        exit_code=None,
        execution_status="not_executed",
        stdout_preview="",
        stderr_preview="",
        checked_keys=[],
        artifact_ids=[],
        notes=["Execution is not performed during validate."],
    )
    review_preview = build_decision(validation_preview)
    approval_preview = require_approval(validation_preview, review_preview, {"artifact_ids": []})

    return {
        "request_file": request_file,
        "request_id": normalized_request["request_id"],
        "product": resolution["product"],
        "required_capabilities": routing_result["required_capabilities"],
        "selected_provider": routing_result["selected_provider"],
        "selected_node": routing_result["selected_node"],
        "execution_path": routing_result["execution_path"],
        "validation_status": validation_preview["validation_status"],
        "review_status": review_preview["review_status"],
        "approval_status": approval_preview["approval_status"],
        "close_or_continue": close_or_continue(approval_preview),
        "reason_codes": routing_result["reason_codes"],
    }


def main(argv: list[str] | None = None) -> int:
    """Validate ATP seed request assets."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        summary = validate_request(args.request_file)
    except (
        RequestLoadError,
        ProductResolutionError,
        RoutePreparationError,
        RouteSelectionError,
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

    print(json.dumps({"status": "ok", "summary": summary}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
