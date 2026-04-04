"""ATP F-202 CLI — synchronous bounded 3-stage composition command.

Executes request-flow → request-bundle → request-prompt in sequence on one
request file. Fail-stop at each stage. No retry, no async, no background.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.artifact_export import build_export_manifest, write_artifact, write_manifest
from core.composition_contract import (
    COMPOSITION_STATUS_FAIL,
    COMPOSITION_STATUS_OK,
    build_composition_envelope,
    build_stage_result,
)
from core.intake.execution_prompt import (
    ExecutionPromptError,
    prepare_one_shot_ai_ready_execution_prompt,
)
from core.intake.loader import RequestLoadError, load_request
from core.intake.request_flow import RequestFlowError, prepare_single_ai_request_flow
from core.intake.review_bundle import (
    ReviewBundleError,
    prepare_reviewable_single_ai_output_bundle,
)
from core.resolution.product_resolver import ProductResolutionError
from core.session_tracking import (
    build_artifact_continuity_anchors,
    build_artifact_record_from_primary_artifact,
)
from output_contract import build_success_envelope, render_output

CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"

_STAGE_RUN_IDS = {
    "request_flow": "compose-chain-flow-0001",
    "request_bundle": "compose-chain-bundle-0001",
    "request_prompt": "compose-chain-prompt-0001",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./atp compose-chain",
        description=(
            "Run the bounded 3-stage composition: "
            "request-flow → request-bundle → request-prompt.\n"
            "Synchronous, fail-stop at each stage. No retry, no async, no background."
        ),
        epilog=(
            "Example:\n"
            f"  ./atp compose-chain {CANONICAL_SAMPLE_REQUEST}\n"
            "Fails fast at first stage failure. Individual commands remain unchanged."
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
        default="compose-chain-0001",
        help="Optional bounded run identifier for the composition run.",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help=(
            "Optional directory to write composed artifact and manifest.\n"
            "Stdout remains canonical primary. Export is additive opt-in secondary."
        ),
    )
    return parser


def _run_request_flow(request_file: str, run_id: str) -> tuple[str, dict]:
    """Run stage 1: request_flow. Returns (status, output_dict)."""
    try:
        raw = load_request(request_file)
        summary = prepare_single_ai_request_flow(raw, run_id=run_id)
        envelope = build_success_envelope(
            command="request-flow",
            request_file=request_file,
            run_id=run_id,
            summary=summary,
        )
        return "ok", dict(envelope)
    except (RequestLoadError, RequestFlowError, ProductResolutionError, ValueError) as exc:
        return "error", {"status": "error", "command": "request-flow", "error": str(exc)}


def _run_request_bundle(request_file: str, run_id: str) -> tuple[str, dict]:
    """Run stage 2: request_bundle. Returns (status, output_dict)."""
    try:
        raw = load_request(request_file)
        summary = prepare_reviewable_single_ai_output_bundle(raw, run_id=run_id)
        envelope = build_success_envelope(
            command="request-bundle",
            request_file=request_file,
            run_id=run_id,
            summary=summary,
        )
        return "ok", dict(envelope)
    except (
        RequestLoadError,
        RequestFlowError,
        ReviewBundleError,
        ProductResolutionError,
        ValueError,
    ) as exc:
        return "error", {"status": "error", "command": "request-bundle", "error": str(exc)}


def _run_request_prompt(request_file: str, run_id: str) -> tuple[str, dict]:
    """Run stage 3: request_prompt. Returns (status, output_dict)."""
    try:
        raw = load_request(request_file)
        summary = prepare_one_shot_ai_ready_execution_prompt(raw, run_id=run_id)
        envelope = build_success_envelope(
            command="request-prompt",
            request_file=request_file,
            run_id=run_id,
            summary=summary,
        )
        return "ok", dict(envelope)
    except (
        RequestLoadError,
        RequestFlowError,
        ReviewBundleError,
        ExecutionPromptError,
        ProductResolutionError,
        ValueError,
    ) as exc:
        return "error", {"status": "error", "command": "request-prompt", "error": str(exc)}


_STAGE_RUNNERS = [
    ("request_flow", _run_request_flow),
    ("request_bundle", _run_request_bundle),
    ("request_prompt", _run_request_prompt),
]


def _extract_stage_artifact_record(stage_output: dict, creation_order: int) -> OrderedDict[str, object] | None:
    review_summary = stage_output.get("review_summary")
    if not isinstance(review_summary, dict):
        return None
    primary_artifact = review_summary.get("primary_artifact")
    if not isinstance(primary_artifact, dict):
        return None
    return build_artifact_record_from_primary_artifact(
        primary_artifact=primary_artifact,
        creation_order=creation_order,
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    stages_executed: list[dict] = []
    fail_stage: str | None = None
    fail_reason: str | None = None
    session_id: str | None = None
    request_ids: list[str] = []
    artifact_records: list[OrderedDict[str, object]] = []

    for stage_name, runner in _STAGE_RUNNERS:
        run_id = _STAGE_RUN_IDS[stage_name]
        status, output = runner(args.request_file, run_id)
        stage_result = dict(build_stage_result(stage=stage_name, status=status, output=output))
        stages_executed.append(stage_result)
        if status == "ok":
            review_summary = output.get("review_summary")
            if isinstance(review_summary, dict):
                stage_session_summary = review_summary.get("session_summary")
                if isinstance(stage_session_summary, dict):
                    if session_id is None:
                        raw_session_id = stage_session_summary.get("session_id")
                        if isinstance(raw_session_id, str):
                            session_id = raw_session_id
                    if not request_ids:
                        raw_request_ids = stage_session_summary.get("request_ids")
                        if isinstance(raw_request_ids, list):
                            request_ids = [str(request_id) for request_id in raw_request_ids]
                artifact_record = _extract_stage_artifact_record(output, len(artifact_records) + 1)
                if artifact_record is not None:
                    artifact_records.append(artifact_record)
        if status != "ok":
            fail_stage = stage_name
            fail_reason = output.get("error", "Stage returned error status.")
            break

    if fail_stage is None:
        composition_status = COMPOSITION_STATUS_OK
    else:
        composition_status = COMPOSITION_STATUS_FAIL

    artifact_continuity_anchors = None
    if session_id is not None and request_ids:
        artifact_continuity_anchors = build_artifact_continuity_anchors(
            session_id=session_id,
            request_ids=request_ids,
            artifact_records=artifact_records,
        )

    envelope = build_composition_envelope(
        request_file=args.request_file,
        run_id=args.run_id,
        composition_status=composition_status,
        stages=stages_executed,
        artifact_continuity_anchors=artifact_continuity_anchors,
        fail_stage=fail_stage,
        fail_reason=fail_reason,
    )

    print(json.dumps(envelope, indent=2))

    if args.export_dir:
        artifact_path = write_artifact(
            args.export_dir, args.run_id, "request_prompt", envelope
        )
        manifest_continuity_anchors = None
        if session_id is not None and request_ids:
            prompt_artifact_record = None
            if artifact_records:
                prompt_artifact_record = OrderedDict(artifact_records[-1])
                prompt_artifact_record["export_path"] = artifact_path
            manifest_continuity_anchors = build_artifact_continuity_anchors(
                session_id=session_id,
                request_ids=request_ids,
                artifact_records=[] if prompt_artifact_record is None else [prompt_artifact_record],
            )
        manifest = build_export_manifest(
            run_id=args.run_id,
            command="compose-chain",
            request_file=args.request_file,
            artifact_type="request_prompt",
            artifact_path=artifact_path,
            session_id=session_id,
            artifact_continuity_anchors=manifest_continuity_anchors,
        )
        write_manifest(args.export_dir, args.run_id, manifest)

    return 0 if fail_stage is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
