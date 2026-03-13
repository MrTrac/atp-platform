"""Placeholder unit tests for ATP route selection beyond M4."""

from __future__ import annotations

import unittest

from core.classification.classifier import classify_request
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import resolve_product


class TestRouteSelection(unittest.TestCase):
    """Keep route selection out of scope while checking stable M4 inputs."""

    def test_m4_exposes_manifest_and_context_for_future_routing(self) -> None:
        normalized = normalize_request(
            {
                "request_id": "req-1",
                "product": "ATP",
                "payload": {"input_text": "Run tests for ATP"},
            }
        )
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)
        product_context = build_product_context(resolution)

        self.assertIn("required_capabilities", task_manifest)
        self.assertIn("policy_names", product_context)

    @unittest.skip("ATP M5+ route selection is intentionally out of scope in M4.")
    def test_route_selection_policy_todo(self) -> None:
        self.fail("TODO: enable when route selection is implemented.")


if __name__ == "__main__":
    unittest.main()
