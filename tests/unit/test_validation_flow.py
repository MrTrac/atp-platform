"""Unit tests for ATP M7-M8 validation, review, and approval flow."""

from __future__ import annotations

import unittest

from adapters.filesystem.artifact_store import create_filtered_artifact, create_raw_artifact
from core.approvals.approval_gate import require_approval
from core.approvals.decision_model import build_decision
from core.validation.validator import validate_artifacts


class TestValidationFlow(unittest.TestCase):
    """Cover minimal validation, review, and approval rules."""

    def test_validator_returns_passed_summary_for_exit_code_zero(self) -> None:
        execution_result = {
            "execution_id": "execution-req-1",
            "request_id": "req-1",
            "product": "ATP",
            "selected_provider": "non_llm_execution",
            "selected_node": "local_mac",
            "command": ["echo", "hello"],
            "exit_code": 0,
            "stdout": "hello\n",
            "stderr": "",
            "status": "succeeded",
        }
        artifacts = [create_filtered_artifact(create_raw_artifact(execution_result))]

        summary = validate_artifacts(execution_result, artifacts)

        self.assertEqual(summary["validation_status"], "passed")

    def test_validator_returns_failed_summary_for_non_zero_exit_code(self) -> None:
        execution_result = {
            "execution_id": "execution-req-1",
            "request_id": "req-1",
            "product": "ATP",
            "selected_provider": "non_llm_execution",
            "selected_node": "local_mac",
            "command": ["false"],
            "exit_code": 1,
            "stdout": "",
            "stderr": "error",
            "status": "failed",
        }
        artifacts = [create_filtered_artifact(create_raw_artifact(execution_result))]

        summary = validate_artifacts(execution_result, artifacts)

        self.assertEqual(summary["validation_status"], "failed")

    def test_review_decision_becomes_accept_reject_revise(self) -> None:
        accept = build_decision({"request_id": "req-1", "validation_status": "passed", "artifact_ids": ["a1"]})
        reject = build_decision({"request_id": "req-1", "validation_status": "failed", "artifact_ids": ["a1"]})
        revise = build_decision({"request_id": "req-1", "validation_status": "incomplete", "artifact_ids": ["a1"]})

        self.assertEqual(accept["review_status"], "accept")
        self.assertEqual(reject["review_status"], "reject")
        self.assertEqual(revise["review_status"], "revise")

    def test_approval_gate_follows_minimal_rules(self) -> None:
        approved = require_approval(
            {"request_id": "req-1", "validation_status": "passed"},
            {"request_id": "req-1", "review_status": "accept"},
            {"artifact_ids": ["a1"]},
        )
        rejected = require_approval(
            {"request_id": "req-1", "validation_status": "failed"},
            {"request_id": "req-1", "review_status": "reject"},
            {"artifact_ids": ["a1"]},
        )
        attention = require_approval(
            {"request_id": "req-1", "validation_status": "incomplete"},
            {"request_id": "req-1", "review_status": "revise"},
            {"artifact_ids": ["a1"]},
        )

        self.assertEqual(approved["approval_status"], "approved")
        self.assertEqual(rejected["approval_status"], "rejected")
        self.assertEqual(attention["approval_status"], "needs_attention")


if __name__ == "__main__":
    unittest.main()
