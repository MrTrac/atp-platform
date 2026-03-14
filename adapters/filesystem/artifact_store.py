"""Artifact shaping helpers for ATP M7."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _artifact_base(
    artifact_id: str,
    request_id: str,
    product: str,
    artifact_type: str,
    artifact_state: str,
    source_stage: str,
    source_ref: str,
    payload_summary: dict[str, Any],
    authoritative: bool = False,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "request_id": request_id,
        "product": product,
        "artifact_type": artifact_type,
        "artifact_state": artifact_state,
        "source_stage": source_stage,
        "source_ref": source_ref,
        "authoritative": authoritative,
        "artifact_freshness": "current",
        "payload_summary": payload_summary,
        "notes": [],
    }


def create_raw_artifact(execution_result: dict[str, Any]) -> dict[str, Any]:
    """Create a raw artifact from normalized execution output."""

    request_id = str(execution_result.get("request_id", "request-unknown"))
    payload_summary = {
        "command": execution_result.get("command", []),
        "exit_code": execution_result.get("exit_code"),
        "status": execution_result.get("status"),
        "stdout": execution_result.get("stdout", ""),
        "stderr": execution_result.get("stderr", ""),
    }
    artifact = _artifact_base(
        artifact_id=f"artifact-raw-{request_id}",
        request_id=request_id,
        product=str(execution_result.get("product", "unknown")),
        artifact_type="execution_output",
        artifact_state="raw",
        source_stage="execution",
        source_ref=str(execution_result.get("execution_id", "execution-unknown")),
        payload_summary=payload_summary,
    )
    artifact["notes"].append("Captured raw execution output in ATP M7.")
    return artifact


def create_filtered_artifact(raw_artifact: dict[str, Any]) -> dict[str, Any]:
    """Create a filtered artifact with trimmed payload summary."""

    filtered = _artifact_base(
        artifact_id=raw_artifact["artifact_id"].replace("artifact-raw-", "artifact-filtered-"),
        request_id=raw_artifact["request_id"],
        product=raw_artifact["product"],
        artifact_type=raw_artifact["artifact_type"],
        artifact_state="filtered",
        source_stage=raw_artifact["source_stage"],
        source_ref=raw_artifact["artifact_id"],
        payload_summary={
            "command": raw_artifact.get("payload_summary", {}).get("command", []),
            "exit_code": raw_artifact.get("payload_summary", {}).get("exit_code"),
            "status": raw_artifact.get("payload_summary", {}).get("status"),
            "stdout_preview": str(raw_artifact.get("payload_summary", {}).get("stdout", ""))[:120],
            "stderr_preview": str(raw_artifact.get("payload_summary", {}).get("stderr", ""))[:120],
        },
    )
    filtered["notes"].append("Filtered execution output for validation and review summaries.")
    return filtered


def mark_selected(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return a selected artifact derivative."""

    selected = deepcopy(artifact)
    selected["artifact_id"] = artifact["artifact_id"].replace("artifact-filtered-", "artifact-selected-")
    selected["artifact_state"] = "selected"
    selected["source_ref"] = artifact["artifact_id"]
    selected["notes"] = list(artifact.get("notes", [])) + ["Marked as selected for ATP continuity."]
    return selected


def mark_authoritative(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return an authoritative artifact derivative."""

    authoritative = deepcopy(artifact)
    authoritative["artifact_id"] = artifact["artifact_id"].replace("artifact-selected-", "artifact-authoritative-")
    authoritative["artifact_state"] = "authoritative"
    authoritative["authoritative"] = True
    authoritative["source_ref"] = artifact["artifact_id"]
    authoritative["notes"] = list(artifact.get("notes", [])) + ["Marked as authoritative for the current run."]
    return authoritative


def mark_deprecated(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return a deprecated artifact derivative."""

    deprecated = deepcopy(artifact)
    deprecated["artifact_id"] = artifact["artifact_id"].replace("artifact-", "artifact-deprecated-")
    deprecated["artifact_state"] = "deprecated"
    deprecated["authoritative"] = False
    deprecated["source_ref"] = artifact["artifact_id"]
    deprecated["notes"] = list(artifact.get("notes", [])) + ["Deprecated artifact retained for model completeness."]
    return deprecated


def summarize_artifacts(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize artifact ids and authoritative selections."""

    return {
        "artifact_ids": [artifact["artifact_id"] for artifact in artifacts],
        "artifact_states": [artifact["artifact_state"] for artifact in artifacts],
        "authoritative_artifacts": [
            {
                "artifact_id": artifact["artifact_id"],
                "artifact_type": artifact["artifact_type"],
            }
            for artifact in artifacts
            if artifact.get("authoritative")
        ],
    }


def store_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Shape an artifact-like payload without persistence."""

    return {
        "artifact_id": artifact.get("artifact_id", "artifact-unknown"),
        "artifact_type": artifact.get("artifact_type", "execution_output"),
        "stored": False,
        "notes": ["Artifact persistence is deferred in M7."],
    }
