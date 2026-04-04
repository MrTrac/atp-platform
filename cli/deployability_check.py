"""ATP CLI for bounded deployability-readiness assessment."""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.artifact_export import build_export_manifest, write_artifact, write_manifest
from core.deployability_readiness import (
    build_deployability_operator_scan_summary,
    build_deployability_readiness,
)
from output_contract import render_output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./atp deployability-check",
        description=(
            "Emit one bounded, read-only deployability-readiness assessment for ATP.\n"
            "This command is descriptive only and does not deploy, install, or provision anything."
        ),
        epilog=(
            "Example:\n"
            "  ./atp deployability-check\n"
            "  ./atp deployability-check --export-dir /tmp/atp-deploy-check\n"
            "This command remains repo-local, human-gated, and assessment-only."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--run-id",
        default="deployability-check-0001",
        help="Optional bounded run identifier for the exported readiness artifact.",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help=(
            "Optional directory to write the readiness JSON and export manifest.\n"
            "Stdout remains canonical primary. Export is additive opt-in secondary.\n"
            "Files written: <export-dir>/<run-id>/deployability_readiness.json and export_manifest.json"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    readiness = build_deployability_readiness(ROOT_DIR)
    envelope = OrderedDict(
        [
            ("command", "deployability-check"),
            ("status", "ok"),
            (
                "operator_scan_summary",
                build_deployability_operator_scan_summary(readiness),
            ),
            ("deployability_readiness", readiness),
        ]
    )
    print(render_output(envelope))

    if args.export_dir:
        artifact_path = write_artifact(
            args.export_dir, args.run_id, "deployability_readiness", envelope
        )
        manifest = build_export_manifest(
            run_id=args.run_id,
            command="deployability-check",
            request_file=None,
            artifact_type="deployability_readiness",
            artifact_path=artifact_path,
        )
        write_manifest(args.export_dir, args.run_id, manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
