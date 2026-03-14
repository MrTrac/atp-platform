"""Unit tests for ATP M1-M6 request, context, routing, and execution flow."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.classification.classifier import classify_request
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.execution.orchestrator import execute_run
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import resolve_product
from core.routing.route_prepare import prepare_route
from core.routing.route_select import select_route


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


class TestRequestModel(unittest.TestCase):
    """Cover the M1-M6 request seed flow."""

    def test_loader_reads_sample_request_fixture(self) -> None:
        loaded = load_request(FIXTURE_DIR / "sample_request.yaml")

        self.assertEqual(loaded["request_id"], "req-atp-m6-0001")
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

    def test_task_manifest_is_built_with_stable_required_keys(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)

        self.assertIn("required_capabilities", task_manifest)
        self.assertEqual(task_manifest["required_capabilities"], ["shell_execution"])

    def test_product_context_is_built_from_valid_resolution(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_tdf.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        product_context = build_product_context(resolution)

        self.assertEqual(product_context["product"], "TDF")
        self.assertEqual(product_context["profile_ref"], "profiles/TDF/profile.yaml")

    def test_request_flow_can_execute_supported_local_route(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_exec_echo.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)
        product_context = build_product_context(resolution)
        evidence_bundle = {
            "bundle_id": "evidence-bundle-test",
            "request_id": normalized["request_id"],
            "product": resolution["product"],
        }
        prepared_route = prepare_route(normalized, classification, resolution, task_manifest, product_context, evidence_bundle)
        routing_result = select_route(prepared_route)

        execution_result = execute_run(
            normalized_request=normalized,
            resolution=resolution,
            task_manifest=task_manifest,
            product_context=product_context,
            evidence_bundle=evidence_bundle,
            routing_result=routing_result,
        )

        self.assertEqual(execution_result["exit_code"], 0)
        self.assertEqual(execution_result["selected_provider"], "non_llm_execution")


if __name__ == "__main__":
    unittest.main()
