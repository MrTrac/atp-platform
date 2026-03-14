"""ATP M8 inspect CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import RequestLoadError, load_request


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect ATP v0 preview summary data.")
    parser.add_argument("input_file", nargs="?", help="Optional JSON or YAML summary file to inspect.")
    return parser


def _summarize(payload: dict) -> dict:
    summary = payload.get("summary", payload)
    return {
        "request_id": summary.get("request", {}).get("request_id") or summary.get("request_id", "unknown"),
        "product": summary.get("request", {}).get("product") or summary.get("product", "unknown"),
        "selected_provider": summary.get("routing", {}).get("routing_result", {}).get("selected_provider", "unknown"),
        "selected_node": summary.get("routing", {}).get("routing_result", {}).get("selected_node", "unknown"),
        "validation_status": summary.get("validation", {}).get("validation_status", "unknown"),
        "review_status": summary.get("review", {}).get("review_status", "unknown"),
        "approval_status": summary.get("approval", {}).get("approval_status", "unknown"),
        "final_status": summary.get("finalization", {}).get("final_status", "unknown"),
        "close_or_continue": summary.get("close_or_continue", "unknown"),
    }


def main(argv: list[str] | None = None) -> int:
    """Inspect ATP summary data when supplied, or describe inspect expectations."""

    args = _build_parser().parse_args(argv)
    if not args.input_file:
        print("ATP inspect expects a JSON/YAML summary file from a test-safe ATP run output. Persistence-backed inspect is out of scope in v0.")
        return 0

    try:
        payload = load_request(args.input_file)
    except (RequestLoadError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc), "input_file": args.input_file}, indent=2, sort_keys=True))
        return 1

    print(json.dumps({"status": "ok", "summary": _summarize(payload)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
