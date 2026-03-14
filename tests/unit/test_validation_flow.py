"""Unit tests for ATP M7 validation and review flow."""

from __future__ import annotations

import unittest

from adapters.filesystem.artifact_store import create_filtered_artifact, create_raw_artifact
from core.approvals.decision_model import build_decision
from core.validation.validator import validate_artifacts


class TestValidationFlow(unittest.TestCase):
    """Cover minimal validation and review decision rules."""

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


if __name__ == "__main__":
    unittest.main()
