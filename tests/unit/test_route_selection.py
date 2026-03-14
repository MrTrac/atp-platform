"""Unit tests for ATP M5-M6 route preparation and route selection."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.classification.classifier import classify_request
from core.context.bundle_materializer import materialize_bundle
from core.context.evidence_selector import select_evidence
from core.context.product_context import build_product_context
from core.context.task_manifest import build_task_manifest
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request
from core.resolution.product_resolver import resolve_product
from core.routing.route_prepare import prepare_route
from core.routing.route_select import RouteSelectionError, select_route


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


def _build_evidence(normalized_request: dict, product: str, task_manifest: dict) -> dict:
    manifest_reference = task_manifest["manifest_id"]
    selection = select_evidence(
        [
            {"artifact_id": f"raw-request-{normalized_request['request_id']}", "artifact_type": "request_raw", "manifest_reference": manifest_reference},
            {"artifact_id": f"normalized-request-{normalized_request['request_id']}", "artifact_type": "request_normalized", "manifest_reference": manifest_reference, "authoritative": True},
            {"artifact_id": f"classification-{normalized_request['request_id']}", "artifact_type": "classification", "manifest_reference": manifest_reference, "authoritative": True},
            {"artifact_id": task_manifest["manifest_id"], "artifact_type": "task_manifest", "manifest_reference": manifest_reference, "authoritative": True},
        ]
    )
    return materialize_bundle(normalized_request["request_id"], product, selection, manifest_reference)


class TestRouteSelection(unittest.TestCase):
    """Cover the deterministic M5-M6 routing flow."""

    def test_route_preparation_derives_expected_required_capability(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)
        product_context = build_product_context(resolution)
        evidence_bundle = _build_evidence(normalized, resolution["product"], task_manifest)

        prepared_route = prepare_route(normalized, classification, resolution, task_manifest, product_context, evidence_bundle)

        self.assertEqual(prepared_route["required_capabilities"], ["shell_execution"])

    def test_route_selection_picks_non_llm_execution_and_local_mac_for_supported_requests(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_exec_echo.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)
        product_context = build_product_context(resolution)
        evidence_bundle = _build_evidence(normalized, resolution["product"], task_manifest)
        prepared_route = prepare_route(normalized, classification, resolution, task_manifest, product_context, evidence_bundle)

        routing_result = select_route(prepared_route)

        self.assertEqual(routing_result["selected_provider"], "non_llm_execution")
        self.assertEqual(routing_result["selected_node"], "local_mac")
        self.assertEqual(routing_result["execution_path"], "local_subprocess")

    def test_unsupported_capability_raises_clear_error(self) -> None:
        prepared_route = {
            "request_id": "req-1",
            "product": "ATP",
            "required_capabilities": ["unknown_capability"],
            "candidate_providers": [{"provider": "non_llm_execution", "status": "active", "supported_capabilities": ["shell_execution"], "provider_type": "execution"}],
            "candidate_nodes": [{"node": "local_mac", "status": "active", "supported_provider_types": ["execution"]}],
        }

        with self.assertRaisesRegex(RouteSelectionError, "No provider supports capability"):
            select_route(prepared_route)

    def test_incompatible_node_provider_combination_raises_clear_error(self) -> None:
        prepared_route = {
            "request_id": "req-1",
            "product": "ATP",
            "required_capabilities": ["shell_execution"],
            "candidate_providers": [{"provider": "non_llm_execution", "status": "active", "supported_capabilities": ["shell_execution"], "provider_type": "execution", "supported_nodes": ["remote_only"], "cost_profile": "low"}],
            "candidate_nodes": [{"node": "local_mac", "status": "active", "supported_provider_types": ["execution"]}],
        }

        with self.assertRaisesRegex(RouteSelectionError, "No compatible node for provider"):
            select_route(prepared_route)

    def test_routing_result_has_stable_required_keys(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_tdf.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        task_manifest = build_task_manifest(normalized, classification, resolution)
        product_context = build_product_context(resolution)
        evidence_bundle = _build_evidence(normalized, resolution["product"], task_manifest)
        prepared_route = prepare_route(normalized, classification, resolution, task_manifest, product_context, evidence_bundle)
        routing_result = select_route(prepared_route)

        self.assertEqual(
            set(routing_result.keys()),
            {
                "route_id",
                "request_id",
                "product",
                "required_capabilities",
                "candidate_providers",
                "candidate_nodes",
                "selected_provider",
                "selected_node",
                "reason_codes",
                "cost_summary",
                "execution_path",
                "status",
            },
        )


if __name__ == "__main__":
    unittest.main()
