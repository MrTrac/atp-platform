"""ATP v1.2 CLI for bounded multi-request Slice 02 flow preparation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import load_request
from core.intake.multi_request_flow import prepare_multi_request_flow
from output_contract import order_for_operator_review, render_output

CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"
CANONICAL_SECONDARY_REQUEST = "tests/fixtures/requests/sample_request_slice02_b.yaml"


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="./atp request-flow-multi",
        description=(
            "Prepare multiple ATP Slice 02 request flows in explicit input order, "
            "without changing the bounded single-request behavior."
        ),
        epilog=(
            "Example:\n"
            f"  ./atp request-flow-multi {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}\n"
            "This command stays sequential, explicit, and operator-controlled."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    parser.add_argument(
        "request_files",
        nargs="+",
        help="Repo-root request files to prepare in explicit input order.",
    )
    parser.add_argument(
        "--run-id",
        default="multi-flow-preview-0001",
        help="Optional bounded run identifier for the multi-request flow preparation.",
    )
    args = parser.parse_args(argv)

    request_inputs = [(request_file, load_request(request_file)) for request_file in args.request_files]
    multi_request_summary = prepare_multi_request_flow(request_inputs, run_id=args.run_id)

    print(
        render_output(
            order_for_operator_review(
                {
                    "command": "request-flow-multi",
                    "status": "ok",
                    "request_files": list(args.request_files),
                    "run_id": args.run_id,
                    "multi_request_summary": multi_request_summary,
                }
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
