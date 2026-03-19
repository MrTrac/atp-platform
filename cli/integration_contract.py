"""ATP CLI for bounded integration-contract projection."""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.artifact_export import build_export_manifest, write_artifact, write_manifest
from core.integration_contract import (
    build_integration_contract_operator_scan_summary,
    build_integration_contract_projection,
)
from output_contract import render_output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./atp integration-contract",
        description=(
            "Emit one bounded, derived integration-contract projection for ATP.\n"
            "This is a static contract document only. No live endpoint, provider runtime, or active integration is created."
        ),
        epilog=(
            "Example:\n"
            "  ./atp integration-contract\n"
            "  ./atp integration-contract --export-dir /tmp/atp-contract-test\n"
            "This command is repo-local, human-gated, and projection-only."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--run-id",
        default="integration-contract-0001",
        help="Optional bounded run identifier for the projected contract artifact.",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help=(
            "Optional directory to write the contract JSON and export manifest.\n"
            "Stdout remains canonical primary. Export is additive opt-in secondary.\n"
            "Files written: <export-dir>/<run-id>/integration_contract.json and export_manifest.json"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    projection = build_integration_contract_projection()
    envelope = OrderedDict(
        [
            ("command", "integration-contract"),
            ("status", "ok"),
            (
                "operator_scan_summary",
                build_integration_contract_operator_scan_summary(projection),
            ),
            ("integration_contract_projection", projection),
        ]
    )
    print(render_output(envelope))

    if args.export_dir:
        artifact_path = write_artifact(
            args.export_dir, args.run_id, "integration_contract", envelope
        )
        manifest = build_export_manifest(
            run_id=args.run_id,
            command="integration-contract",
            request_file=None,
            artifact_type="integration_contract",
            artifact_path=artifact_path,
        )
        write_manifest(args.export_dir, args.run_id, manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
