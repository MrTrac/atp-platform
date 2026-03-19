"""ATP CLI for bounded operator review summary."""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.artifact_export import build_export_manifest, write_artifact, write_manifest
from core.operator_review_summary import (
    build_operator_review_scan_summary,
    build_operator_review_summary,
)
from output_contract import render_output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./atp review-summary",
        description=(
            "Emit one bounded, operator-facing review summary for ATP.\n"
            "This command is descriptive only and does not create live status, control surfaces, or runtime coordination."
        ),
        epilog=(
            "Example:\n"
            "  ./atp review-summary\n"
            "  ./atp review-summary --export-dir /tmp/atp-review-summary\n"
            "This command remains repo-local, human-gated, and review-oriented."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--run-id",
        default="review-summary-0001",
        help="Optional bounded run identifier for the exported review summary artifact.",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help=(
            "Optional directory to write the review summary JSON and export manifest.\n"
            "Stdout remains canonical primary. Export is additive opt-in secondary.\n"
            "Files written: <export-dir>/<run-id>/operator_review_summary.json and export_manifest.json"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    review_summary = build_operator_review_summary()
    envelope = OrderedDict(
        [
            ("command", "review-summary"),
            ("status", "ok"),
            (
                "operator_scan_summary",
                build_operator_review_scan_summary(review_summary),
            ),
            ("operator_review_summary", review_summary),
        ]
    )
    print(render_output(envelope))

    if args.export_dir:
        artifact_path = write_artifact(
            args.export_dir, args.run_id, "operator_review_summary", envelope
        )
        manifest = build_export_manifest(
            run_id=args.run_id,
            command="review-summary",
            request_file=None,
            artifact_type="operator_review_summary",
            artifact_path=artifact_path,
        )
        write_manifest(args.export_dir, args.run_id, manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
