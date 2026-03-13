"""ATP M1-M3 run preview CLI."""

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
from core.intake.loader import RequestLoadError, load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import ProductResolutionError, resolve_product
from core.state.decision_state import initial_decision_state
from core.state.run_state import RunState, build_run_record
from core.state.transitions import advance_run_state


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the ATP M1-M3 run flow.")
    parser.add_argument("request_file", help="Path to a JSON or YAML request file.")
    parser.add_argument(
        "--run-id",
        default="run-preview-0001",
        help="Optional preview run identifier.",
    )
    return parser


def preview_run(request_file: str, run_id: str) -> dict[str, Any]:
    """Load, normalize, classify, and resolve a request, then build early state transitions."""

    raw_request = load_request(request_file)
    normalized_request = normalize_request(raw_request)
    classification = classify_request(normalized_request)
    resolution = resolve_product(normalized_request, classification)

    run_record = build_run_record(run_id=run_id, request_id=normalized_request["request_id"])
    run_record = advance_run_state(run_record, RunState.NORMALIZED, "request normalized")
    run_record = advance_run_state(run_record, RunState.CLASSIFIED, "request classified")
    run_record = advance_run_state(run_record, RunState.RESOLVED, "product resolved")
    run_record["product"] = resolution["product"]
    run_record["resolution"] = {
        "repo_boundary": resolution["repo_boundary"],
        "profile_ref": resolution["profile_ref"],
        "policy_names": [policy["policy_name"] for policy in resolution["policies"]],
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
        "run": run_record,
        "decision_state": initial_decision_state(),
        "message": "Execution is intentionally not implemented in ATP M1-M3.",
    }


def main(argv: list[str] | None = None) -> int:
    """Run the ATP M1-M3 preview flow."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        preview = preview_run(args.request_file, args.run_id)
    except (RequestLoadError, ProductResolutionError, ValueError) as exc:
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
