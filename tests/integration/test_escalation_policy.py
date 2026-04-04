"""Tests for ATP escalation policy."""

from __future__ import annotations

import unittest

from core.routing.escalation_policy import should_escalate


class TestEscalateOnFailedLocal(unittest.TestCase):
    """1. Local result failed → should_escalate=True."""

    def test_failed_status(self):
        result, reason = should_escalate(
            request={},
            local_result={"status": "failed"},
        )
        self.assertTrue(result)
        self.assertIn("failed", reason)

    def test_completion_not_validated(self):
        result, reason = should_escalate(
            request={},
            local_result={
                "status": "success",
                "manifest": {"completion_validated": False},
            },
        )
        self.assertTrue(result)
        self.assertIn("completion", reason)


class TestEscalateOnForceCloud(unittest.TestCase):
    """2. force_cloud=True → should_escalate=True."""

    def test_force_cloud(self):
        result, reason = should_escalate(
            request={"force_cloud": True},
        )
        self.assertTrue(result)
        self.assertIn("force_cloud", reason)

    def test_force_cloud_overrides_success(self):
        result, reason = should_escalate(
            request={"force_cloud": True},
            local_result={
                "status": "success",
                "manifest": {"completion_validated": True},
            },
        )
        self.assertTrue(result)


class TestNoEscalateOnSuccess(unittest.TestCase):
    """3. Local result success → should_escalate=False."""

    def test_successful_local(self):
        result, reason = should_escalate(
            request={},
            local_result={
                "status": "success",
                "manifest": {"completion_validated": True},
            },
        )
        self.assertFalse(result)
        self.assertEqual(reason, "")

    def test_no_local_result_no_triggers(self):
        result, reason = should_escalate(request={})
        self.assertFalse(result)
        self.assertEqual(reason, "")


class TestEscalationTriggers(unittest.TestCase):
    """4. Named escalation triggers return non-empty reason."""

    def test_hard_reasoning(self):
        result, reason = should_escalate(
            request={"escalation_trigger": "hard_reasoning"},
        )
        self.assertTrue(result)
        self.assertIn("hard_reasoning", reason)
        self.assertGreater(len(reason), 0)

    def test_final_artifact(self):
        result, reason = should_escalate(
            request={"escalation_trigger": "final_artifact"},
        )
        self.assertTrue(result)
        self.assertIn("final_artifact", reason)

    def test_current_facts(self):
        result, reason = should_escalate(
            request={"escalation_trigger": "current_facts"},
        )
        self.assertTrue(result)
        self.assertIn("current_facts", reason)

    def test_low_confidence(self):
        result, reason = should_escalate(
            request={"escalation_trigger": "low_confidence"},
        )
        self.assertTrue(result)
        self.assertIn("low_confidence", reason)

    def test_unknown_trigger_no_escalate(self):
        result, reason = should_escalate(
            request={"escalation_trigger": "unknown_trigger"},
        )
        self.assertFalse(result)
        self.assertEqual(reason, "")


class TestNoEscalateOnContractViolation(unittest.TestCase):
    """5. Contract violations should not escalate — would fail on cloud too."""

    def test_contract_violation_no_escalate(self):
        result, reason = should_escalate(
            request={},
            local_result={
                "status": "failed",
                "error": "Execution contract violated: 'model' is required.",
            },
        )
        self.assertFalse(result)
        self.assertEqual(reason, "")

    def test_non_contract_failure_still_escalates(self):
        result, reason = should_escalate(
            request={},
            local_result={
                "status": "failed",
                "error": "Ollama request failed: Connection refused",
            },
        )
        self.assertTrue(result)
        self.assertIn("failed", reason)


if __name__ == "__main__":
    unittest.main()
