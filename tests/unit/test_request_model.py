"""Unit tests for ATP M1-M3 request intake, classification, and resolution."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.classification.classifier import classify_request
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import resolve_product


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


class TestRequestModel(unittest.TestCase):
    """Cover the M1-M3 request seed flow."""

    def test_loader_reads_sample_request_fixture(self) -> None:
        loaded = load_request(FIXTURE_DIR / "sample_request.yaml")

        self.assertEqual(loaded["request_id"], "req-atp-m3-0001")
        self.assertEqual(loaded["product"], "ATP")

    def test_normalizer_fills_default_fields(self) -> None:
        normalized = normalize_request({"request_id": "req-1", "product_hint": "ATP"})

        self.assertEqual(normalized["product"], "ATP")
        self.assertEqual(normalized["request_type"], "unspecified")
        self.assertEqual(normalized["execution_intent"], "unspecified")
        self.assertEqual(normalized["payload"], {})
        self.assertEqual(normalized["metadata"], {})

    def test_classifier_returns_stable_keys(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request.yaml"))
        classification = classify_request(normalized)

        self.assertEqual(
            set(classification.keys()),
            {
                "product",
                "domain",
                "product_type",
                "request_type",
                "execution_intent",
                "capability",
                "rule_trace",
            },
        )
        self.assertEqual(classification["request_type"], "implementation")

    def test_request_flow_can_resolve_product_after_classification(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_tdf.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)

        self.assertEqual(resolution["product"], "TDF")
        self.assertEqual(resolution["profile"]["product"], "TDF")


if __name__ == "__main__":
    unittest.main()
