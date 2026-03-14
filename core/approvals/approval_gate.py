"""Minimal approval gate helpers for ATP M8."""

from __future__ import annotations

from typing import Any


def require_approval(
    validation_summary: dict[str, Any],
    review_decision: dict[str, Any],
    artifact_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a manual-first approval gate summary."""

    request_id = str(validation_summary.get("request_id", review_decision.get("request_id", "request-unknown")))
    validation_status = str(validation_summary.get("validation_status", "incomplete"))
    review_status = str(review_decision.get("review_status", "revise"))

    if review_status == "accept" and validation_status == "passed":
        approval_status = "approved"
        continue_recommended = False
        approval_notes = ["Validation and review are aligned for approval."]
    elif review_status == "reject" or validation_status == "failed":
        approval_status = "rejected"
        continue_recommended = False
        approval_notes = ["Validation or review requires rejection in ATP v0."]
    else:
        approval_status = "needs_attention"
        continue_recommended = True
        approval_notes = ["Manual attention is still recommended before continuing."]

    return {
        "approval_id": f"approval-{request_id}",
        "request_id": request_id,
        "approval_status": approval_status,
        "approval_mode": "manual_first_rule_based",
        "approval_notes": approval_notes,
        "based_on_review_status": review_status,
        "based_on_validation_status": validation_status,
        "based_on_artifacts": list(artifact_summary.get("artifact_ids", [])),
        "continue_recommended": continue_recommended,
    }
