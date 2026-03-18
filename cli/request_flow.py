"""ATP Slice 02 CLI for the first usable request intake flow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.artifact_export import build_export_manifest, write_artifact, write_manifest
from core.intake.loader import RequestLoadError, load_request
from core.intake.request_flow import RequestFlowError, prepare_single_ai_request_flow
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
        prog="./atp request-flow",
        description=(
            "Prepare the ATP Slice 02 thin request flow: intake one bounded request, "
            "normalize it deterministically, and emit a single-AI execution package."
        ),
        epilog=(
            "Example:\n"
            f"  ./atp request-flow {CANONICAL_SAMPLE_REQUEST}\n"
            "This command is bounded to the current ATP single-AI request path only."
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
        default="slice-02-preview-0001",
        help="Optional bounded run identifier for the prepared request flow.",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help=(
            "Optional directory to write the artifact JSON and export manifest.\n"
            "Stdout remains canonical primary. Export is additive opt-in secondary.\n"
            "Files written: <export-dir>/<run-id>/request_flow.json and export_manifest.json"
        ),
    )
    return parser


def _describe_error(exc: Exception) -> tuple[str, str, str]:
    message = str(exc)

    if isinstance(exc, RequestLoadError):
        if "Request file not found:" in message:
            return (
                "request_loading",
                "request_file_not_found",
                "Confirm the request_file path exists relative to repo root, or rerun with "
                f"`./atp request-flow {CANONICAL_SAMPLE_REQUEST}`.",
            )
        if "Unsupported YAML structure" in message:
            return (
                "request_loading",
                "invalid_yaml",
                "Fix the YAML structure near the reported line, or compare against "
                f"`{CANONICAL_SAMPLE_REQUEST}` and rerun.",
            )
        if "Invalid JSON request:" in message:
            return (
                "request_loading",
                "invalid_json",
                "Fix the JSON syntax, or rerun with the canonical sample "
                f"`./atp request-flow {CANONICAL_SAMPLE_REQUEST}`.",
            )
        return (
            "request_loading",
            "invalid_request_file",
            "Ensure the request file is a top-level JSON/YAML object shaped like the canonical sample "
            f"`{CANONICAL_SAMPLE_REQUEST}`.",
        )

    if isinstance(exc, ProductResolutionError):
        return (
            "request_flow_preparation",
            "product_resolution_error",
            "Keep the request within the bounded ATP repo-local flow and compare it against "
            f"`{CANONICAL_SAMPLE_REQUEST}`.",
        )

    if " is required." in message:
        return (
            "request_flow_preparation",
            "missing_required_field",
            "Add the missing field shown in `error`, then rerun with the same command. "
            f"For a known-good shape, start from `{CANONICAL_SAMPLE_REQUEST}`.",
        )

    if "supports ATP requests only" in message:
        return (
            "request_flow_preparation",
            "unsupported_request_shape",
            "Use an ATP request bounded to the current single-AI flow, or rerun with "
                f"`./atp request-flow {CANONICAL_SAMPLE_REQUEST}`.",
        )

    return (
        "request_flow_preparation",
        "validation_error",
        "Review the error, keep the request within the bounded Slice 02 flow, and compare it against "
        f"`{CANONICAL_SAMPLE_REQUEST}`.",
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        raw_request = load_request(args.request_file)
        summary = prepare_single_ai_request_flow(raw_request, run_id=args.run_id)
    except (RequestLoadError, RequestFlowError, ProductResolutionError, ValueError) as exc:
        error_stage, error_kind, next_step = _describe_error(exc)
        print(
            render_output(
                build_error_envelope(
                    command="request-flow",
                    request_file=args.request_file,
                    run_id=args.run_id,
                    error=str(exc),
                    error_stage=error_stage,
                    error_kind=error_kind,
                    next_step=next_step,
                )
            )
        )
        return 1

    envelope = build_success_envelope(
        command="request-flow",
        request_file=args.request_file,
        run_id=args.run_id,
        summary=summary,
    )
    print(render_output(envelope))

    if args.export_dir:
        artifact_path = write_artifact(args.export_dir, args.run_id, "request_flow", envelope)
        manifest = build_export_manifest(
            run_id=args.run_id,
            command="request-flow",
            request_file=args.request_file,
            artifact_type="request_flow",
            artifact_path=artifact_path,
        )
        write_manifest(args.export_dir, args.run_id, manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
