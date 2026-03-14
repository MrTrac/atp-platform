"""Minimal review decision model for ATP M7."""

from __future__ import annotations

from typing import Any


def build_decision(validation_summary: dict[str, Any]) -> dict[str, Any]:
    """Build a minimal review decision summary from validation status."""

    validation_status = str(validation_summary.get("validation_status", "incomplete"))
    if validation_status == "passed":
        review_status = "accept"
        review_notes = ["Validation passed. Accept for the next phase preview."]
    elif validation_status == "failed":
        review_status = "reject"
        review_notes = ["Validation failed. Reject until execution issues are fixed."]
    else:
        review_status = "revise"
        review_notes = ["Validation is incomplete. Revise before moving forward."]

    request_id = str(validation_summary.get("request_id", "request-unknown"))
    return {
        "decision_id": f"review-{request_id}",
        "request_id": request_id,
        "review_status": review_status,
        "review_notes": review_notes,
        "validation_status": validation_status,
        "based_on_artifacts": list(validation_summary.get("artifact_ids", [])),
    }
