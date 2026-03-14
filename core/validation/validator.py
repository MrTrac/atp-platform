"""Rule-based validation helpers for ATP M7."""

from __future__ import annotations

from typing import Any

from core.validation.validation_result import build_validation_result


REQUIRED_EXECUTION_KEYS = {
    "execution_id",
    "request_id",
    "product",
    "selected_provider",
    "selected_node",
    "command",
    "exit_code",
    "stdout",
    "stderr",
    "status",
}


def validate_artifacts(
    execution_result: dict[str, Any],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate normalized execution output and related artifacts."""

    missing_keys = sorted(REQUIRED_EXECUTION_KEYS - set(execution_result.keys()))
    exit_code = execution_result.get("exit_code")
    execution_status = execution_result.get("status")

    if missing_keys or exit_code is None or not execution_status:
        validation_status = "incomplete"
        notes = ["Execution result is missing required keys or status fields."]
    elif exit_code == 0:
        validation_status = "passed"
        notes = ["Execution completed with exit_code 0."]
    else:
        validation_status = "failed"
        notes = [f"Execution completed with non-zero exit_code {exit_code}."]

    return build_validation_result(
        request_id=str(execution_result.get("request_id", "")),
        validation_status=validation_status,
        exit_code=exit_code,
        execution_status=str(execution_status or ""),
        stdout_preview=str(execution_result.get("stdout", ""))[:120],
        stderr_preview=str(execution_result.get("stderr", ""))[:120],
        checked_keys=sorted(REQUIRED_EXECUTION_KEYS),
        artifact_ids=[artifact.get("artifact_id", "artifact-unknown") for artifact in artifacts],
        notes=notes,
    )
