"""ATP inspect CLI for preview summaries and read-only current-task state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.intake.loader import RequestLoadError, load_request

CANONICAL_WORKSPACE_ROOT = "/Users/nguyenthanhthu/SOURCE_DEV/workspace"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./atp inspect",
        description="Inspect bounded ATP preview summaries or read-only current-task state only.",
        epilog=(
            "Examples:\n"
            "  ./atp inspect preview-summary.json\n"
            f"  ./atp inspect --workspace-root {CANONICAL_WORKSPACE_ROOT} --run-id run-preview-0001\n"
            "This command is read-only. It does not resume execution, mutate pointers, or trigger background behavior."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", nargs="?", help="Optional JSON or YAML summary file to inspect read-only.")
    parser.add_argument("--workspace-root", help="Optional SOURCE_DEV/workspace root for read-only current-task inspection.")
    parser.add_argument("--run-id", help="Optional run id for read-only current-task inspection.")
    return parser


def _summarize(payload: dict) -> dict:
    summary = payload.get("summary", payload)
    return {
        "request_id": summary.get("request", {}).get("request_id") or summary.get("request_id", "unknown"),
        "product": summary.get("request", {}).get("product") or summary.get("product", "unknown"),
        "selected_provider": summary.get("routing", {}).get("routing_result", {}).get("selected_provider", "unknown"),
        "selected_node": summary.get("routing", {}).get("routing_result", {}).get("selected_node", "unknown"),
        "validation_status": summary.get("validation", {}).get("validation_status", "unknown"),
        "review_status": summary.get("review", {}).get("review_status", "unknown"),
        "approval_status": summary.get("approval", {}).get("approval_status", "unknown"),
        "final_status": summary.get("finalization", {}).get("final_status", "unknown"),
        "close_or_continue": summary.get("close_or_continue", "unknown"),
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _inspect_current_task(workspace_root: Path, run_id: str) -> dict:
    current_task_root = workspace_root / "exchange" / "current-task"
    exchange_root = current_task_root / run_id
    if not exchange_root.is_dir():
        raise ValueError(f"Current-task root does not exist for run_id={run_id}: {exchange_root}")

    current_task_state = _load_json(exchange_root / "current-task-state.json")
    recovery_contract_path = exchange_root / "continue-pending-recovery.json"
    current_reference = _load_json(exchange_root / "current.json")
    active_pointer = _load_json(current_task_root / "active-pointer.json")

    recovery_contract = _load_json(recovery_contract_path) if recovery_contract_path.is_file() else {}
    supersede_trace_path = exchange_root / "supersede-trace.json"
    supersede_trace = _load_json(supersede_trace_path) if supersede_trace_path.is_file() else {}

    return {
        "inspect_mode": "current_task",
        "run_id": run_id,
        "workspace_root": str(workspace_root),
        "exchange_root": str(exchange_root),
        "current_task_id": current_task_state.get("current_task_id", ""),
        "close_or_continue": current_task_state.get("close_or_continue", ""),
        "current_task_persistence_state_path": str(exchange_root / "current-task-state.json"),
        "current_reference_path": current_task_state.get("current_reference_path", ""),
        "recovery_contract_path": recovery_contract.get("recovery_contract_path", str(recovery_contract_path) if recovery_contract_path.is_file() else ""),
        "continuation_state_path": current_task_state.get("continuation_state_path", ""),
        "reference_index_path": current_task_state.get("reference_index_path", ""),
        "active_pointer": {
            "path": str(current_task_root / "active-pointer.json"),
            "run_id": active_pointer.get("run_id", ""),
            "current_task_id": active_pointer.get("current_task_id", ""),
            "superseded_previous": active_pointer.get("superseded_previous", False),
            "supersede_trace_path": active_pointer.get("supersede_trace_path", ""),
        },
        "recovery_contract": {
            "recovery_ready": bool(recovery_contract),
            "recovery_contract_id": recovery_contract.get("recovery_contract_id", ""),
            "recovery_entry_mode": recovery_contract.get("recovery_entry_mode", ""),
            "recovery_scope": recovery_contract.get("recovery_scope", ""),
        },
        "supersede_trace": {
            "present": bool(supersede_trace),
            "path": str(supersede_trace_path) if supersede_trace else "",
            "previous_run_id": supersede_trace.get("previous_run_id", ""),
            "previous_current_task_id": supersede_trace.get("previous_current_task_id", ""),
        },
        "notes": [
            "Read-only inspect surface only.",
            "No mutation, resume execution, or pointer management behavior is performed.",
        ],
        "current_reference": {
            "exchange_boundary_mode": current_reference.get("exchange_boundary_mode", ""),
            "manifest_reference": current_reference.get("manifest_reference", ""),
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Inspect ATP summary data when supplied, or describe inspect expectations."""

    args = _build_parser().parse_args(argv)
    if not args.input_file and not (args.workspace_root and args.run_id):
        print("ATP inspect expects either a JSON/YAML summary file or --workspace-root with --run-id for read-only current-task inspection.")
        return 0

    if args.workspace_root or args.run_id:
        if not (args.workspace_root and args.run_id):
            print(
                json.dumps(
                    {
                        "status": "error",
                        "error": "--workspace-root and --run-id must be provided together for current-task inspection.",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
        try:
            summary = _inspect_current_task(Path(args.workspace_root), args.run_id)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc), "run_id": args.run_id}, indent=2, sort_keys=True))
            return 1
        print(json.dumps({"status": "ok", "summary": summary}, indent=2, sort_keys=True))
        return 0

    try:
        payload = load_request(args.input_file)
    except (RequestLoadError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc), "input_file": args.input_file}, indent=2, sort_keys=True))
        return 1

    print(json.dumps({"status": "ok", "summary": _summarize(payload)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
