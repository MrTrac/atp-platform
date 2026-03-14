"""Build ATP M7 validation summary payloads."""

from __future__ import annotations

from typing import Any


def build_validation_result(
    request_id: str,
    validation_status: str,
    exit_code: int | None,
    execution_status: str,
    stdout_preview: str,
    stderr_preview: str,
    checked_keys: list[str],
    artifact_ids: list[str],
    notes: list[str],
) -> dict[str, Any]:
    """Build a stable validation summary structure."""

    return {
        "validation_id": f"validation-{request_id}",
        "request_id": request_id,
        "validation_status": validation_status,
        "exit_code": exit_code,
        "execution_status": execution_status,
        "stdout_preview": stdout_preview,
        "stderr_preview": stderr_preview,
        "checked_keys": list(checked_keys),
        "artifact_ids": list(artifact_ids),
        "notes": list(notes),
    }
