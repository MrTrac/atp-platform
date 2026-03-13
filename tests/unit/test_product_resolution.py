"""Unit tests for ATP M3-M4 product resolution and context guards."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from core.classification.classifier import classify_request
from core.context.product_context import build_product_context
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request
from core.resolution.policy_loader import load_policies
from core.resolution.product_resolver import ProductResolutionError, resolve_product


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


class TestProductResolution(unittest.TestCase):
    """Cover the M3-M4 file-based resolution flow."""

    def test_resolve_atp_from_explicit_product_field(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        resolution = resolve_product(normalized, classify_request(normalized))

        self.assertEqual(resolution["product"], "ATP")
        self.assertEqual(resolution["repo_boundary"], "SOURCE_DEV/platforms/ATP")

    def test_resolve_tdf_from_explicit_product_field(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_tdf.yaml"))
        resolution = resolve_product(normalized, classify_request(normalized))

        self.assertEqual(resolution["product"], "TDF")
        self.assertEqual(resolution["repo_boundary"], "SOURCE_DEV/products/TDF")

    def test_policy_loader_returns_minimal_policy_set(self) -> None:
        policies = load_policies(["approval_policy", "cost_policy"])

        self.assertEqual([policy["policy_name"] for policy in policies], ["approval_policy", "cost_policy"])

    def test_missing_product_raises_clear_error(self) -> None:
        normalized = normalize_request({"request_id": "req-1"})

        with self.assertRaisesRegex(ProductResolutionError, "Product could not be resolved"):
            resolve_product(normalized, classify_request(normalized))

    def test_missing_required_resolution_inputs_raise_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing required resolution inputs"):
            build_product_context({"product": "ATP"})

    def test_bad_profile_ref_raises_clear_error(self) -> None:
        normalized = normalize_request({"request_id": "req-1", "product": "ATP"})
        classification = classify_request(normalized)

        with patch(
            "core.resolution.product_resolver._load_registry_entry",
            return_value={
                "product": "ATP",
                "product_type": "platform",
                "repo_boundary": "SOURCE_DEV/platforms/ATP",
                "profile_ref": "profiles/ATP/missing.yaml",
                "policy_refs": ["approval_policy"],
                "status": "active",
            },
        ):
            with self.assertRaisesRegex(ProductResolutionError, "Profile ref not found"):
                resolve_product(normalized, classification)

    def test_bad_policy_ref_raises_clear_error(self) -> None:
        normalized = normalize_request({"request_id": "req-1", "product": "ATP"})
        classification = classify_request(normalized)

        with patch(
            "core.resolution.product_resolver._load_registry_entry",
            return_value={
                "product": "ATP",
                "product_type": "platform",
                "repo_boundary": "SOURCE_DEV/platforms/ATP",
                "profile_ref": "profiles/ATP/profile.yaml",
                "policy_refs": ["missing_policy"],
                "status": "active",
            },
        ):
            with self.assertRaisesRegex(ProductResolutionError, "Policy ref not found"):
                resolve_product(normalized, classification)


if __name__ == "__main__":
    unittest.main()
