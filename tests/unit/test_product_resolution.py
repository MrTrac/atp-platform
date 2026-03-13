"""Placeholder unit tests for ATP product resolution beyond M2."""

from __future__ import annotations

import unittest

from core.classification.classifier import classify_request
from core.intake.normalizer import normalize_request


class TestProductResolution(unittest.TestCase):
    """Keep M3 resolution explicitly deferred while asserting current boundaries."""

    def test_m1_m2_stops_before_product_resolution(self) -> None:
        normalized = normalize_request({"request_id": "req-1", "product": "ATP"})
        classification = classify_request(normalized)

        self.assertEqual(classification["product_type"], "platform")

    @unittest.skip("ATP M3 product resolution is intentionally out of scope in M1-M2.")
    def test_product_resolution_registry_lookup_todo(self) -> None:
        self.fail("TODO: enable when product resolution is implemented.")


if __name__ == "__main__":
    unittest.main()
