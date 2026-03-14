"""Unit tests for ATP M3-M4 resolution plus v0.5 Slice A-D contract hardening."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from core.classification.classifier import classify_request
from core.context.product_context import build_product_context
from core.intake.loader import load_request
from core.intake.normalizer import normalize_request
from core.resolution.policy_loader import load_policies
from core.resolution.product_resolver import (
    ProductResolutionError,
    build_product_execution_preparation_contract,
    build_product_execution_result_contract,
    build_request_to_product_resolution_contract,
    build_resolution_to_handoff_intent_contract,
    resolve_product,
)


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "requests"


class TestProductResolution(unittest.TestCase):
    """Cover file-based resolution flow plus the v0.5 Slice A-D contracts."""

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

    def test_request_to_product_resolution_contract_is_explicit_and_narrow(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)

        contract = build_request_to_product_resolution_contract(
            run_id="run-v0-5-slice-a-1",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-1",
        )

        self.assertEqual(contract["request_id"], normalized["request_id"])
        self.assertEqual(contract["run_id"], "run-v0-5-slice-a-1")
        self.assertEqual(contract["resolution_scope"], "request_to_product_only")
        self.assertEqual(contract["product_target"]["product"], "ATP")
        self.assertEqual(contract["capability_target"]["capability"], "shell_execution")
        self.assertEqual(contract["capability_target"]["source"], "classification.capability")
        self.assertEqual(
            contract["resolution_rationale"]["product_source"],
            "normalized_request.product",
        )
        self.assertEqual(contract["traceability"]["classification_capability"], "shell_execution")
        self.assertIn(
            "product_target_resolved_from_registry",
            contract["resolution_rationale"]["rationale_codes"],
        )
        self.assertEqual(contract["traceability"]["manifest_id"], "task-manifest-req-1")
        self.assertEqual(contract["traceability"]["classification_request_type"], "implementation")
        self.assertEqual(contract["traceability"]["classification_execution_intent"], "preview")
        self.assertNotIn("selected_provider", contract)
        self.assertNotIn("selected_node", contract)
        self.assertNotIn("reason_codes", contract)

    def test_request_to_product_resolution_contract_prefers_classification_capability_when_present(self) -> None:
        normalized = normalize_request({"request_id": "req-2", "product": "TDF", "metadata": {"capability": "product_surface_read"}})
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)

        contract = build_request_to_product_resolution_contract(
            run_id="run-v0-5-slice-a-2",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-2",
        )

        self.assertEqual(contract["product_target"]["product"], "TDF")
        self.assertEqual(contract["capability_target"]["capability"], "product_surface_read")
        self.assertEqual(contract["capability_target"]["source"], "classification.capability")
        self.assertEqual(contract["resolution_rationale"]["profile_ref"], "profiles/TDF/profile.yaml")

    def test_resolution_to_handoff_intent_contract_is_explicit_and_narrow(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        resolution_contract = build_request_to_product_resolution_contract(
            run_id="run-v0-5-slice-b-1",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-1",
        )

        contract = build_resolution_to_handoff_intent_contract(
            run_id="run-v0-5-slice-b-1",
            normalized_request=normalized,
            classification=classification,
            resolution_contract=resolution_contract,
            manifest_id="task-manifest-req-1",
        )

        self.assertEqual(contract["request_id"], normalized["request_id"])
        self.assertEqual(contract["run_id"], "run-v0-5-slice-b-1")
        self.assertEqual(contract["handoff_scope"], "resolution_to_handoff_only")
        self.assertEqual(
            contract["request_to_product_resolution_ref"]["contract_id"],
            resolution_contract["contract_id"],
        )
        self.assertEqual(contract["handoff_intent"]["intent"], "prepare_structured_product_handoff")
        self.assertEqual(contract["handoff_intent"]["intent_stage"], "pre_routing")
        self.assertEqual(contract["handoff_intent"]["target_product"], "ATP")
        self.assertEqual(contract["handoff_intent"]["target_capability"], "shell_execution")
        self.assertEqual(contract["handoff_intent"]["execution_intent"], "preview")
        self.assertEqual(contract["handoff_rationale"]["request_type"], "implementation")
        self.assertEqual(contract["traceability"]["manifest_id"], "task-manifest-req-1")
        self.assertEqual(
            contract["traceability"]["request_to_product_resolution_contract_id"],
            resolution_contract["contract_id"],
        )
        self.assertNotIn("selected_provider", contract)
        self.assertNotIn("selected_node", contract)
        self.assertNotIn("reason_codes", contract)

    def test_product_execution_preparation_contract_is_explicit_and_narrow(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        resolution_contract = build_request_to_product_resolution_contract(
            run_id="run-v0-5-slice-c-1",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-1",
        )
        handoff_contract = build_resolution_to_handoff_intent_contract(
            run_id="run-v0-5-slice-c-1",
            normalized_request=normalized,
            classification=classification,
            resolution_contract=resolution_contract,
            manifest_id="task-manifest-req-1",
        )
        task_manifest = {
            "manifest_id": "task-manifest-req-1",
            "required_capabilities": ["shell_execution"],
        }
        product_context = build_product_context(resolution)
        evidence_bundle = {
            "bundle_id": "evidence-bundle-req-1",
            "selected_artifacts": [
                {"artifact_id": "classification-req-1", "artifact_type": "classification"},
                {"artifact_id": "task-manifest-req-1", "artifact_type": "task_manifest"},
            ],
        }

        contract = build_product_execution_preparation_contract(
            run_id="run-v0-5-slice-c-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            task_manifest=task_manifest,
            product_context=product_context,
            evidence_bundle=evidence_bundle,
        )

        self.assertEqual(contract["request_id"], normalized["request_id"])
        self.assertEqual(contract["run_id"], "run-v0-5-slice-c-1")
        self.assertEqual(contract["preparation_scope"], "product_execution_preparation_only")
        self.assertEqual(
            contract["request_to_product_resolution_ref"]["contract_id"],
            resolution_contract["contract_id"],
        )
        self.assertEqual(
            contract["resolution_to_handoff_intent_ref"]["contract_id"],
            handoff_contract["contract_id"],
        )
        self.assertEqual(
            contract["execution_preparation"]["preparation_mode"],
            "pre_routing_pre_provider",
        )
        self.assertEqual(contract["execution_preparation"]["target_product"], "ATP")
        self.assertEqual(contract["execution_preparation"]["target_capability"], "shell_execution")
        self.assertEqual(contract["execution_preparation"]["task_manifest_id"], "task-manifest-req-1")
        self.assertEqual(contract["traceability"]["evidence_bundle_id"], "evidence-bundle-req-1")
        self.assertEqual(
            contract["traceability"]["resolution_to_handoff_intent_contract_id"],
            handoff_contract["contract_id"],
        )
        self.assertNotIn("selected_provider", contract)
        self.assertNotIn("selected_node", contract)
        self.assertNotIn("execution_id", contract)

    def test_product_execution_result_contract_is_explicit_and_narrow(self) -> None:
        normalized = normalize_request(load_request(FIXTURE_DIR / "sample_request_atp.yaml"))
        classification = classify_request(normalized)
        resolution = resolve_product(normalized, classification)
        resolution_contract = build_request_to_product_resolution_contract(
            run_id="run-v0-5-slice-d-1",
            normalized_request=normalized,
            classification=classification,
            resolution=resolution,
            manifest_id="task-manifest-req-1",
        )
        handoff_contract = build_resolution_to_handoff_intent_contract(
            run_id="run-v0-5-slice-d-1",
            normalized_request=normalized,
            classification=classification,
            resolution_contract=resolution_contract,
            manifest_id="task-manifest-req-1",
        )
        preparation_contract = build_product_execution_preparation_contract(
            run_id="run-v0-5-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            task_manifest={"manifest_id": "task-manifest-req-1", "required_capabilities": ["shell_execution"]},
            product_context=build_product_context(resolution),
            evidence_bundle={
                "bundle_id": "evidence-bundle-req-1",
                "selected_artifacts": [{"artifact_id": "classification-req-1", "artifact_type": "classification"}],
            },
        )
        execution_result = {
            "execution_id": "execution-req-1",
            "status": "succeeded",
            "exit_code": 0,
            "command": ["echo", "hello"],
            "stdout": "hello\n",
            "stderr": "",
        }

        contract = build_product_execution_result_contract(
            run_id="run-v0-5-slice-d-1",
            normalized_request=normalized,
            resolution_contract=resolution_contract,
            handoff_intent_contract=handoff_contract,
            execution_preparation_contract=preparation_contract,
            execution_result=execution_result,
            artifact_summary={"artifact_ids": ["artifact-selected-req-1", "artifact-authoritative-req-1"]},
        )

        self.assertEqual(contract["request_id"], normalized["request_id"])
        self.assertEqual(contract["run_id"], "run-v0-5-slice-d-1")
        self.assertEqual(contract["result_scope"], "product_execution_result_only")
        self.assertEqual(
            contract["request_to_product_resolution_ref"]["contract_id"],
            resolution_contract["contract_id"],
        )
        self.assertEqual(
            contract["resolution_to_handoff_intent_ref"]["contract_id"],
            handoff_contract["contract_id"],
        )
        self.assertEqual(
            contract["product_execution_preparation_ref"]["contract_id"],
            preparation_contract["contract_id"],
        )
        self.assertEqual(contract["execution_result"]["execution_id"], "execution-req-1")
        self.assertEqual(contract["execution_result"]["status"], "succeeded")
        self.assertEqual(contract["execution_result"]["exit_code"], 0)
        self.assertEqual(contract["result_summary"]["artifact_count"], 2)
        self.assertEqual(
            contract["traceability"]["product_execution_preparation_contract_id"],
            preparation_contract["contract_id"],
        )
        self.assertNotIn("selected_provider", contract)
        self.assertNotIn("selected_node", contract)
        self.assertNotIn("approval_status", contract)


if __name__ == "__main__":
    unittest.main()
