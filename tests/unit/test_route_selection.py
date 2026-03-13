"""Placeholder unit tests for ATP route selection beyond M3."""

from __future__ import annotations

import unittest

from core.classification.classifier import classify_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import resolve_product


class TestRouteSelection(unittest.TestCase):
    """Keep route selection out of scope while checking stable inputs."""

    def test_m3_exposes_resolution_keys_needed_by_future_routing(self) -> None:
        normalized = normalize_request(
            {
                "request_id": "req-1",
                "product": "ATP",
                "payload": {"input_text": "Run tests for ATP"},
            }
        )
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)

        self.assertIn("repo_boundary", resolution)
        self.assertIn("policies", resolution)

    @unittest.skip("ATP M4+ route selection is intentionally out of scope in M3.")
    def test_route_selection_policy_todo(self) -> None:
        self.fail("TODO: enable when route selection is implemented.")


if __name__ == "__main__":
    unittest.main()
