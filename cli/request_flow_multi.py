"""ATP v1.2 CLI for bounded multi-request Slice 02 flow preparation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import RequestLoadError, load_request
from core.intake.multi_request_flow import build_multi_request_flow_summary
from core.intake.request_flow import RequestFlowError, prepare_single_ai_request_flow
from core.resolution.product_resolver import ProductResolutionError
from output_contract import (
    build_multi_request_error_envelope,
    build_multi_request_success_envelope,
    render_output,
)

CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"
CANONICAL_SECONDARY_REQUEST = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class _MultiRequestCliParser(argparse.ArgumentParser):
    """Parser with bounded guidance for multi-request flow input shape."""

    def error(self, message: str) -> None:
        example = (
            f"./atp request-flow-multi {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}"
        )
        if "request_files" in message:
            self.print_usage(sys.stderr)
            self.exit(
                2,
                (
                    f"{self.prog}: error: {message}\n"
                    "Next step: run the multi-request command from repo root with at least two request files.\n"
                    f"Example: {example}\n"
                ),
            )
        super().error(message)


def _build_parser() -> argparse.ArgumentParser:
    return _MultiRequestCliParser(
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


def _describe_error(exc: Exception) -> tuple[str, str, str]:
    message = str(exc)

    if isinstance(exc, RequestLoadError):
        if "Request file not found:" in message:
            return (
                "request_loading",
                "request_file_not_found",
                "Confirm the failing request_file path exists relative to repo root, or rerun with "
                f"`./atp request-flow-multi {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}`.",
            )
        if "Unsupported YAML structure" in message:
            return (
                "request_loading",
                "invalid_yaml",
                "Fix the YAML structure near the reported line, or compare the request against the canonical pair "
                f"`{CANONICAL_SAMPLE_REQUEST}` and `{CANONICAL_SECONDARY_REQUEST}`.",
            )
        if "Invalid JSON request:" in message:
            return (
                "request_loading",
                "invalid_json",
                "Fix the JSON syntax, or rerun with the canonical multi-request pair "
                f"`./atp request-flow-multi {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}`.",
            )
        return (
            "request_loading",
            "invalid_request_file",
            "Ensure each request file is a top-level JSON/YAML object shaped like the canonical request fixtures.",
        )

    if isinstance(exc, ProductResolutionError):
        return (
            "request_flow_preparation",
            "product_resolution_error",
            "Keep every request within the bounded ATP repo-local flow and compare them against the canonical fixtures.",
        )

    if " is required." in message:
        return (
            "request_flow_preparation",
            "missing_required_field",
            "Add the missing field shown in `error`, then rerun with the same command or start from the canonical fixture pair.",
        )

    if "supports ATP requests only" in message:
        return (
            "request_flow_preparation",
            "unsupported_request_shape",
            "Use ATP requests bounded to the current single-AI flow, or rerun with the canonical multi-request pair.",
        )

    return (
        "request_flow_preparation",
        "validation_error",
        "Review the error, keep the requests within the bounded Slice 02 flow, and rerun the same explicit multi-request command.",
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
    if len(args.request_files) < 2:
        parser.error("request_files must contain at least 2 repo-root request file paths")

    prepared_request_flows: list[dict[str, object]] = []
    for index, request_file in enumerate(args.request_files, start=1):
        try:
            raw_request = load_request(request_file)
            item_run_id = f"{args.run_id}-item-{index:02d}"
            summary = prepare_single_ai_request_flow(raw_request, run_id=item_run_id)
            prepared_request_flows.append(
                {
                    "request_file": request_file,
                    "run_id": item_run_id,
                    "summary": summary,
                }
            )
        except (RequestLoadError, RequestFlowError, ProductResolutionError, ValueError) as exc:
            error_stage, error_kind, next_step = _describe_error(exc)
            print(
                render_output(
                    build_multi_request_error_envelope(
                        command="request-flow-multi",
                        request_files=list(args.request_files),
                        run_id=args.run_id,
                        error=str(exc),
                        error_stage=error_stage,
                        error_kind=error_kind,
                        failed_request_file=request_file,
                        failed_request_index=index,
                        processed_request_count=len(prepared_request_flows),
                        next_step=next_step,
                    )
                )
            )
            return 1

    multi_request_summary = build_multi_request_flow_summary(
        prepared_request_flows,
        run_id=args.run_id,
    )

    print(
        render_output(
            build_multi_request_success_envelope(
                command="request-flow-multi",
                request_files=list(args.request_files),
                run_id=args.run_id,
                multi_request_summary=multi_request_summary,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
