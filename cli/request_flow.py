"""ATP Slice 02 CLI for the first usable request intake flow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import RequestLoadError, load_request
from core.intake.request_flow import RequestFlowError, prepare_single_ai_request_flow
from core.resolution.product_resolver import ProductResolutionError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare ATP Slice 02 first usable request intake to single-AI package flow."
    )
    parser.add_argument("request_file", help="Path to a JSON or YAML request file.")
    parser.add_argument(
        "--run-id",
        default="slice-02-preview-0001",
        help="Optional bounded run identifier for the prepared request flow.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        raw_request = load_request(args.request_file)
        summary = prepare_single_ai_request_flow(raw_request, run_id=args.run_id)
    except (RequestLoadError, RequestFlowError, ProductResolutionError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": str(exc),
                    "request_file": args.request_file,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    print(json.dumps({"status": "ok", "summary": summary}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
