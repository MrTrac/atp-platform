"""ATP M1-M5 run preview CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.classification.classifier import classify_request
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.intake.loader import RequestLoadError, load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import ProductResolutionError, resolve_product
from core.routing.route_prepare import RoutePreparationError, prepare_route
from core.routing.route_select import RouteSelectionError, select_route
from core.state.decision_state import initial_decision_state
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the ATP M1-M5 run flow.")
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


def preview_run(request_file: str, run_id: str) -> dict[str, Any]:
    """Load, normalize, classify, resolve, package context, and select a route."""

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

    run_record = build_run_record(run_id=run_id, request_id=normalized_request["request_id"])
    run_record = advance_run_state(run_record, RunState.NORMALIZED, "request normalized")
    run_record = advance_run_state(run_record, RunState.CLASSIFIED, "request classified")
    run_record = advance_run_state(run_record, RunState.RESOLVED, "product resolved")
    run_record = advance_run_state(run_record, RunState.CONTEXT_PACKAGED, "context packaged")
    run_record = advance_run_state(run_record, RunState.ROUTED, "route selected")
    run_record["product"] = resolution["product"]
    run_record["resolution"] = {
        "repo_boundary": resolution["repo_boundary"],
        "profile_ref": resolution["profile_ref"],
        "policy_names": [policy["policy_name"] for policy in resolution["policies"]],
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
        "run": run_record,
        "decision_state": initial_decision_state(),
        "message": "Execution is intentionally not implemented in ATP M1-M5.",
    }


def main(argv: list[str] | None = None) -> int:
    """Run the ATP M1-M5 preview flow."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        preview = preview_run(args.request_file, args.run_id)
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

    print(json.dumps({"status": "preview", "summary": preview}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
