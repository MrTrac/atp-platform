"""ATP repo-local execution session inspection CLI."""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import RequestLoadError, load_request
from core.integration_readiness import build_compact_integration_readiness_summary
from core.session_tracking import (
    build_artifact_continuity_anchors,
    build_execution_session_summary,
    build_session_operator_scan_summary,
)
from output_contract import render_output

CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"
CANONICAL_SECONDARY_REQUEST = "tests/fixtures/requests/sample_request_slice02_b.yaml"


class _ExecutionSessionParser(argparse.ArgumentParser):
    """Parser with bounded repo-root guidance for execution-session usage."""

    def error(self, message: str) -> None:
        if "request_files" in message:
            self.print_usage(sys.stderr)
            self.exit(
                2,
                (
                    f"{self.prog}: error: {message}\n"
                    "Next step: run the session command from repo root with one or more explicit request files.\n"
                    f"Example: {self.prog} {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}\n"
                ),
            )
        super().error(message)


def _build_parser() -> argparse.ArgumentParser:
    return _ExecutionSessionParser(
        prog="./atp execution-session",
        description=(
            "Inspect one bounded repo-local execution session derived from explicit request files only."
        ),
        epilog=(
            "Example:\n"
            f"  ./atp execution-session {CANONICAL_SAMPLE_REQUEST}\n"
            f"  ./atp execution-session {CANONICAL_SAMPLE_REQUEST} {CANONICAL_SECONDARY_REQUEST}\n"
            "This surface is derived-only. No runtime persistence, daemon, or background tracking is created."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )


def _describe_error(exc: Exception) -> tuple[str, str]:
    message = str(exc)
    if isinstance(exc, RequestLoadError) and "Request file not found:" in message:
        return (
            "request_file_not_found",
            "Confirm the request_file path exists relative to repo root, or rerun with "
            f"`./atp execution-session {CANONICAL_SAMPLE_REQUEST}`.",
        )
    if isinstance(exc, RequestLoadError) and "Unsupported YAML structure" in message:
        return (
            "invalid_yaml",
            "Fix the YAML structure near the reported line, or compare against "
            f"`{CANONICAL_SAMPLE_REQUEST}` and rerun.",
        )
    if isinstance(exc, RequestLoadError) and "Invalid JSON request:" in message:
        return (
            "invalid_json",
            "Fix the JSON syntax, or rerun with the canonical sample "
            f"`./atp execution-session {CANONICAL_SAMPLE_REQUEST}`.",
        )
    return (
        "invalid_request_file",
        "Ensure each request file is a top-level JSON/YAML object with a valid `request_id`, then rerun.",
    )


def _extract_request_id(raw_request: dict[str, object], request_file: str) -> str:
    request_id = raw_request.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError(f"request_id is required for execution session tracking: {request_file}")
    return request_id


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    parser.add_argument(
        "request_files",
        nargs="+",
        help=(
            "One or more JSON/YAML request files to derive a repo-local execution session from.\n"
            f"Canonical repo-root sample: {CANONICAL_SAMPLE_REQUEST}"
        ),
    )
    args = parser.parse_args(argv)

    request_ids: list[str] = []
    try:
        for request_file in args.request_files:
            raw_request = load_request(request_file)
            request_ids.append(_extract_request_id(raw_request, request_file))
    except (RequestLoadError, ValueError) as exc:
        error_kind, next_step = _describe_error(exc)
        print(
            render_output(
                OrderedDict(
                    [
                        ("command", "execution-session"),
                        ("status", "error"),
                        ("request_files", args.request_files),
                        ("error_kind", error_kind),
                        ("error", str(exc)),
                        ("next_step", next_step),
                    ]
                )
            )
        )
        return 1

    session_summary = build_execution_session_summary(
        request_files=args.request_files,
        request_ids=request_ids,
    )
    print(
        render_output(
            OrderedDict(
                [
                    ("command", "execution-session"),
                    ("status", "ok"),
                    ("request_files", args.request_files),
                    ("operator_scan_summary", build_session_operator_scan_summary(session_summary)),
                    ("session_summary", session_summary),
                    (
                        "artifact_continuity_anchors",
                        build_artifact_continuity_anchors(
                            session_id=str(session_summary["session_id"]),
                            request_ids=[str(request_id) for request_id in request_ids],
                            artifact_records=[],
                        ),
                    ),
                    ("integration_readiness_summary", build_compact_integration_readiness_summary()),
                ]
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
