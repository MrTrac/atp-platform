"""ATP Slice 04 CLI for one-shot AI-ready execution prompt artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.execution_prompt import (
    ExecutionPromptError,
    prepare_one_shot_ai_ready_execution_prompt,
)
from core.intake.loader import RequestLoadError, load_request
from core.intake.request_flow import RequestFlowError
from core.intake.review_bundle import ReviewBundleError
from core.resolution.product_resolver import ProductResolutionError
from output_contract import build_error_envelope, build_success_envelope, render_output

CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


class _RequestCliParser(argparse.ArgumentParser):
    """Parser with bounded operator guidance for missing request files."""

    def error(self, message: str) -> None:
        if "request_file" in message:
            self.print_usage(sys.stderr)
            self.exit(
                2,
                (
                    f"{self.prog}: error: {message}\n"
                    "Next step: run the command from repo root with the canonical sample request.\n"
                    f"Example: {self.prog} {CANONICAL_SAMPLE_REQUEST}\n"
                ),
            )
        super().error(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _RequestCliParser(
        prog="./cli/atp request-prompt",
        description=(
            "Prepare the ATP Slice 04 one-shot AI-ready prompt artifact from the bounded "
            "request-flow chain for manual one-AI handoff."
        ),
        epilog=(
            "Example:\n"
            f"  ./cli/atp request-prompt {CANONICAL_SAMPLE_REQUEST}\n"
            "This command renders a deterministic manual-use artifact; it does not execute an AI."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "request_file",
        help=(
            "Path to a JSON or YAML request file.\n"
            f"Canonical repo-root sample: {CANONICAL_SAMPLE_REQUEST}"
        ),
    )
    parser.add_argument(
        "--run-id",
        default="slice-04-preview-0001",
        help="Optional bounded run identifier for the prepared AI-ready artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        raw_request = load_request(args.request_file)
        summary = prepare_one_shot_ai_ready_execution_prompt(raw_request, run_id=args.run_id)
    except (
        RequestLoadError,
        RequestFlowError,
        ReviewBundleError,
        ExecutionPromptError,
        ProductResolutionError,
        ValueError,
    ) as exc:
        print(
            render_output(
                build_error_envelope(
                    command="request-prompt",
                    request_file=args.request_file,
                    run_id=args.run_id,
                    error=str(exc),
                )
            )
        )
        return 1

    print(
        render_output(
            build_success_envelope(
                command="request-prompt",
                request_file=args.request_file,
                run_id=args.run_id,
                summary=summary,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
