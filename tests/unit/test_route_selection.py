"""Placeholder unit tests for ATP route selection beyond M2."""

from __future__ import annotations

import unittest

from core.classification.classifier import classify_request
from core.intake.normalizer import normalize_request


class TestRouteSelection(unittest.TestCase):
    """Keep route selection out of scope while checking stable inputs."""

    def test_m1_m2_exposes_classification_keys_needed_by_future_routing(self) -> None:
        classification = classify_request(
            normalize_request(
                {
                    "request_id": "req-1",
                    "product": "ATP",
                    "payload": {"input_text": "Run tests for ATP"},
                }
            )
        )

        self.assertIn("domain", classification)
        self.assertIn("execution_intent", classification)

    @unittest.skip("ATP M3-M5 route selection is intentionally out of scope in M1-M2.")
    def test_route_selection_policy_todo(self) -> None:
        self.fail("TODO: enable when route selection is implemented.")


if __name__ == "__main__":
    unittest.main()
