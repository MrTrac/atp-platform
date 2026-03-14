"""Unit tests for ATP v0.4 runtime slices plus v0.5 Slice A-D materialization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import json

from adapters.filesystem.workspace_writer import (
    RUN_TREE_ZONES,
    materialize_run_outputs,
    materialize_run_tree,
    resolve_artifact_projection_root,
    resolve_workspace_root,
)


def _build_fake_repo_root(base_dir: Path) -> Path:
    repo_root = base_dir / "SOURCE_DEV" / "platforms" / "ATP"
    repo_root.mkdir(parents=True, exist_ok=True)
    return repo_root


def _sample_payloads(run_id: str) -> dict[str, object]:
    return {
        "raw_request": {"request_id": "req-1", "product": "ATP"},
        "normalized_request": {"request_id": "req-1", "product": "ATP"},
        "classification": {"request_type": "execute", "execution_intent": "run_command"},
        "resolution": {"product": "ATP", "repo_boundary": "SOURCE_DEV/platforms/ATP"},
        "request_to_product_resolution": {
            "contract_id": "request-to-product-resolution-req-1",
            "contract_version": "v0.5-slice-a",
            "request_id": "req-1",
            "run_id": run_id,
            "resolution_scope": "request_to_product_only",
            "product_target": {
                "product": "ATP",
                "product_type": "platform",
                "repo_boundary": "SOURCE_DEV/platforms/ATP",
                "status": "active",
            },
            "capability_target": {
                "capability": "product_resolution",
                "source": "profile.component_scope",
            },
            "resolution_rationale": {
                "product_source": "normalized_request.product",
                "requested_product": "ATP",
                "classified_product": "ATP",
                "profile_ref": "profiles/ATP/profile.yaml",
                "registry_entry_ref": "registry/products/ATP.yaml",
                "policy_refs": ["approval_policy", "routing_policy"],
                "rationale_codes": [
                    "request_to_product_resolution_contract",
                    "product_target_resolved_from_registry",
                    "capability_target_selected_without_routing",
                ],
            },
            "traceability": {
                "manifest_id": "task-manifest-req-1",
                "classification_request_type": "execute",
                "classification_execution_intent": "run_command",
                "classification_capability": "unspecified",
                "profile_ref": "profiles/ATP/profile.yaml",
                "repo_boundary": "SOURCE_DEV/platforms/ATP",
            },
            "notes": [
                "This contract resolves request intent to a product target and capability target only.",
                "It is distinct from classification, routing, provider selection, and broader orchestration.",
            ],
        },
        "resolution_to_handoff_intent": {
            "contract_id": "resolution-to-handoff-intent-req-1",
            "contract_version": "v0.5-slice-b",
            "request_id": "req-1",
            "run_id": run_id,
            "handoff_scope": "resolution_to_handoff_only",
            "request_to_product_resolution_ref": {
                "contract_id": "request-to-product-resolution-req-1",
                "contract_version": "v0.5-slice-a",
                "resolution_scope": "request_to_product_only",
                "product_target": "ATP",
                "capability_target": "product_resolution",
            },
            "handoff_intent": {
                "intent": "prepare_structured_product_handoff",
                "intent_stage": "pre_routing",
                "target_product": "ATP",
                "target_capability": "product_resolution",
                "execution_intent": "run_command",
            },
            "handoff_rationale": {
                "request_type": "execute",
                "execution_intent": "run_command",
                "rationale_codes": [
                    "resolution_to_handoff_intent_contract",
                    "handoff_preparation_without_routing_selection",
                    "handoff_target_inherited_from_resolution_contract",
                ],
                "summary": "ATP is preparing a bounded handoff intent toward the resolved product/capability target.",
            },
            "traceability": {
                "manifest_id": "task-manifest-req-1",
                "request_to_product_resolution_contract_id": "request-to-product-resolution-req-1",
                "classification_request_type": "execute",
                "classification_execution_intent": "run_command",
            },
            "notes": [
                "This contract prepares handoff intent only.",
                "It is distinct from classification, routing, provider selection, and broader orchestration.",
            ],
        },
        "product_execution_preparation": {
            "contract_id": "product-execution-preparation-req-1",
            "contract_version": "v0.5-slice-c",
            "request_id": "req-1",
            "run_id": run_id,
            "preparation_scope": "product_execution_preparation_only",
            "request_to_product_resolution_ref": {
                "contract_id": "request-to-product-resolution-req-1",
                "resolution_scope": "request_to_product_only",
                "product_target": "ATP",
                "capability_target": "product_resolution",
            },
            "resolution_to_handoff_intent_ref": {
                "contract_id": "resolution-to-handoff-intent-req-1",
                "handoff_scope": "resolution_to_handoff_only",
                "handoff_intent": "prepare_structured_product_handoff",
            },
            "execution_preparation": {
                "preparation_mode": "pre_routing_pre_provider",
                "target_product": "ATP",
                "target_capability": "product_resolution",
                "task_manifest_id": "task-manifest-req-1",
                "product_context_profile": "profiles/ATP/profile.yaml",
                "evidence_bundle_id": "evidence-bundle-req-1",
                "required_capabilities": [],
            },
            "preparation_rationale": {
                "rationale_codes": [
                    "product_execution_preparation_contract",
                    "pre_routing_pre_provider_preparation_only",
                    "preparation_package_composed_from_manifest_context_evidence",
                ],
                "summary": "ATP is preparing a bounded execution package before routing, provider selection, and execution.",
                "module_scope_count": 1,
                "selected_evidence_count": 2,
            },
            "traceability": {
                "task_manifest_id": "task-manifest-req-1",
                "product_context_profile": "profiles/ATP/profile.yaml",
                "evidence_bundle_id": "evidence-bundle-req-1",
                "request_to_product_resolution_contract_id": "request-to-product-resolution-req-1",
                "resolution_to_handoff_intent_contract_id": "resolution-to-handoff-intent-req-1",
            },
            "notes": [
                "This contract prepares a product execution package only.",
                "It is distinct from handoff intent, routing, provider selection, execution result, and broader orchestration.",
            ],
        },
        "product_execution_result": {
            "contract_id": "product-execution-result-req-1",
            "contract_version": "v0.5-slice-d",
            "request_id": "req-1",
            "run_id": run_id,
            "result_scope": "product_execution_result_only",
            "request_to_product_resolution_ref": {
                "contract_id": "request-to-product-resolution-req-1",
                "product_target": "ATP",
                "capability_target": "product_resolution",
            },
            "resolution_to_handoff_intent_ref": {
                "contract_id": "resolution-to-handoff-intent-req-1",
                "handoff_intent": "prepare_structured_product_handoff",
            },
            "product_execution_preparation_ref": {
                "contract_id": "product-execution-preparation-req-1",
                "preparation_mode": "pre_routing_pre_provider",
            },
            "execution_result": {
                "execution_id": "execution-req-1",
                "status": "succeeded",
                "exit_code": 0,
                "command": ["echo", "hello"],
                "stdout_preview": "hello\\n",
                "stderr_preview": "",
            },
            "result_summary": {
                "summary": "ATP is recording the bounded result of the prepared product execution step.",
                "rationale_codes": [
                    "product_execution_result_contract",
                    "bounded_result_recording_only",
                    "post_execution_preparation_pre_review_record",
                ],
                "artifact_count": 2,
            },
            "traceability": {
                "execution_id": "execution-req-1",
                "request_to_product_resolution_contract_id": "request-to-product-resolution-req-1",
                "resolution_to_handoff_intent_contract_id": "resolution-to-handoff-intent-req-1",
                "product_execution_preparation_contract_id": "product-execution-preparation-req-1",
                "artifact_ids": ["artifact-selected-req-1", "artifact-authoritative-req-1"],
            },
            "notes": [
                "This contract records a bounded execution result only.",
                "It is distinct from routing, provider selection, approval, recovery, and broader orchestration.",
            ],
        },
        "task_manifest": {"manifest_id": "task-manifest-req-1", "request_id": "req-1"},
        "product_context": {"product": "ATP", "profile_ref": "profiles/ATP/profile.yaml"},
        "manifest_reference": {"handoff_type": "manifest_reference", "manifest_reference": "task-manifest-req-1"},
        "run_record": {"run_id": run_id, "request_id": "req-1", "current_stage": "CLOSED"},
        "prepared_route": {"route_id": "route-req-1", "candidate_providers": ["non_llm_execution"]},
        "routing_result": {"route_id": "route-req-1", "status": "selected"},
        "execution_result": {
            "execution_id": "execution-req-1",
            "request_id": "req-1",
            "product": "ATP",
            "command": ["echo", "hello"],
            "exit_code": 0,
            "status": "succeeded",
            "stdout": "hello\n",
            "stderr": "",
        },
        "artifacts": {
            "items": [
                {
                    "artifact_id": "artifact-selected-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "selected",
                    "source_stage": "execution",
                    "source_ref": "artifact-filtered-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                },
                {
                    "artifact_id": "artifact-authoritative-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "authoritative",
                    "source_stage": "execution",
                    "source_ref": "artifact-selected-req-1",
                    "artifact_freshness": "current",
                    "authoritative": True,
                },
            ],
            "summary": {"artifact_ids": ["artifact-selected-req-1", "artifact-authoritative-req-1"]},
        },
        "validation_summary": {"validation_status": "passed"},
        "review_decision": {"review_status": "accept"},
        "approval_result": {"approval_status": "approved"},
        "close_or_continue": {"run_id": run_id, "decision": "close"},
        "decision_state": {"decision_status": "finalized"},
        "exchange_boundary_decision": {
            "decision_id": f"exchange-boundary-{run_id}",
            "run_id": run_id,
            "request_id": "req-1",
            "close_or_continue": "close",
            "boundary_mode": "run_local_handoff",
            "requires_exchange_boundary": False,
            "exchange_materialization_status": "deferred",
            "manifest_reference": "task-manifest-req-1",
            "evidence_bundle_id": "handoff-evidence-req-1",
            "reason_codes": ["closed_run_keeps_handoff_inside_current_run"],
        },
        "exchange_bundle": {
            "handoff_type": "exchange_bundle",
            "exchange_id": "exchange-req-1",
            "request_id": "req-1",
            "artifacts": ["artifact-authoritative-req-1"],
            "provider": "non_llm_execution",
            "adapter": "local_subprocess",
        },
        "handoff_outputs": {
            "inline_context": {"handoff_type": "inline_context", "summary": "done", "authoritative": True},
            "evidence_bundle": {"handoff_type": "evidence_bundle", "bundle_id": "handoff-evidence-req-1"},
            "manifest_reference": {
                "handoff_type": "manifest_reference",
                "manifest_reference": "task-manifest-req-1",
                "authoritative": True,
            },
        },
        "finalization_summary": {"final_status": "completed"},
    }


class TestWorkspaceMaterialization(unittest.TestCase):
    """Cover runtime root resolution plus v0.3-v0.4 traceability, persistence, recovery, and pointer semantics."""

    def test_workspace_root_resolves_from_repo_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            self.assertEqual(resolve_workspace_root(repo_root), (repo_root.parents[1] / "workspace").resolve())

    def test_workspace_root_rejects_non_atp_repo_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_repo_root = Path(temp_dir) / "tmp" / "ATP"
            invalid_repo_root.mkdir(parents=True, exist_ok=True)

            with self.assertRaises(ValueError):
                resolve_workspace_root(invalid_repo_root)

    def test_materialize_run_tree_creates_only_approved_run_tree_zones(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            tree = materialize_run_tree("run-slice1-1", repo_root=repo_root)

            self.assertEqual(set(tree["run_root"].iterdir()), {tree[zone] for zone in RUN_TREE_ZONES})
            self.assertFalse((tree["run_root"] / "planning").exists())
            self.assertFalse((tree["run_root"] / "exchange").exists())

    def test_materialize_run_outputs_writes_only_under_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            summary = materialize_run_outputs("run-slice1-2", _sample_payloads("run-slice1-2"), repo_root=repo_root)

            run_root = Path(summary["run_root"])
            self.assertTrue(run_root.is_dir())
            self.assertEqual(set(Path(path).name for path in run_root.iterdir()), set(RUN_TREE_ZONES))
            self.assertTrue((run_root / "request" / "request.raw.json").is_file())
            self.assertTrue((run_root / "manifests" / "manifest-reference.json").is_file())
            self.assertTrue((run_root / "manifests" / "request-to-product-resolution-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "resolution-to-handoff-intent-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-preparation-contract.json").is_file())
            self.assertTrue((run_root / "manifests" / "product-execution-result-contract.json").is_file())
            self.assertTrue((run_root / "decisions" / "exchange-boundary-decision.json").is_file())
            self.assertTrue((run_root / "handoff" / "inline-context.json").is_file())
            self.assertTrue((run_root / "handoff" / "evidence-bundle.json").is_file())
            self.assertTrue((run_root / "handoff" / "manifest-reference.json").is_file())
            self.assertTrue((run_root / "logs" / "materialization.log").is_file())
            self.assertTrue((run_root / "logs" / "cleanup.log").is_file())
            self.assertTrue((run_root / "final" / "retention-summary.json").is_file())
            self.assertTrue((run_root / "final" / "continuation-state.json").is_file())
            self.assertTrue((run_root / "final" / "reference-index.json").is_file())
            self.assertFalse(summary["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(summary["exchange_boundary"]["exchange_materialization_status"], "not_required")
            self.assertFalse(summary["exchange"]["materialized"])
            self.assertFalse(summary["current_task_persistence"]["persisted"])
            self.assertFalse(summary["recovery_contract"]["recovery_ready"])
            self.assertFalse(summary["current_task_pointer"]["active_pointer_written"])
            self.assertFalse(summary["continuation"]["continuation_required"])
            self.assertFalse(summary["reference_index"]["exchange_current_task"]["materialized"])
            self.assertEqual(summary["reference_index"]["continuation"]["current_source"], "none")
            self.assertEqual(
                summary["request_to_product_resolution"]["resolution_scope"],
                "request_to_product_only",
            )
            self.assertEqual(
                summary["request_to_product_resolution"]["product_target"],
                "ATP",
            )
            self.assertEqual(
                summary["request_to_product_resolution"]["capability_target"],
                "product_resolution",
            )
            self.assertEqual(
                summary["resolution_to_handoff_intent"]["handoff_scope"],
                "resolution_to_handoff_only",
            )
            self.assertEqual(
                summary["resolution_to_handoff_intent"]["handoff_intent"],
                "prepare_structured_product_handoff",
            )
            self.assertEqual(
                summary["resolution_to_handoff_intent"]["resolution_contract_id"],
                "request-to-product-resolution-req-1",
            )
            self.assertEqual(
                summary["product_execution_preparation"]["preparation_scope"],
                "product_execution_preparation_only",
            )
            self.assertEqual(
                summary["product_execution_preparation"]["preparation_mode"],
                "pre_routing_pre_provider",
            )
            self.assertEqual(
                summary["product_execution_preparation"]["handoff_intent_contract_id"],
                "resolution-to-handoff-intent-req-1",
            )
            self.assertEqual(
                summary["product_execution_result"]["result_scope"],
                "product_execution_result_only",
            )
            self.assertEqual(
                summary["product_execution_result"]["execution_id"],
                "execution-req-1",
            )
            self.assertEqual(
                summary["product_execution_result"]["execution_preparation_contract_id"],
                "product-execution-preparation-req-1",
            )
            self.assertEqual(summary["authoritative_projection"]["projected_count"], 1)
            projection_root = Path(summary["authoritative_projection"]["items"][0]["projection_root"])
            self.assertTrue((projection_root / "artifact.json").is_file())
            self.assertTrue((projection_root / "projection-metadata.json").is_file())
            self.assertEqual(summary["retention"]["cleanup_mode"], "manual_review_only")
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            self.assertFalse((run_root / "exchange").exists())
            self.assertFalse((Path(summary["workspace_root"]) / "exchange").exists())
            self.assertFalse((repo_root / "atp-runs").exists())
            self.assertFalse((repo_root / "request").exists())
            self.assertFalse((repo_root / "atp-artifacts").exists())

            contract = json.loads(
                (run_root / "manifests" / "request-to-product-resolution-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(contract["request_id"], "req-1")
            self.assertEqual(contract["run_id"], "run-slice1-2")
            self.assertEqual(contract["product_target"]["product"], "ATP")
            self.assertEqual(contract["capability_target"]["capability"], "product_resolution")
            self.assertEqual(contract["resolution_rationale"]["product_source"], "normalized_request.product")
            self.assertNotIn("selected_provider", contract)
            self.assertNotIn("selected_node", contract)
            self.assertNotIn("reason_codes", contract)
            handoff_intent_contract = json.loads(
                (run_root / "manifests" / "resolution-to-handoff-intent-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(handoff_intent_contract["request_id"], "req-1")
            self.assertEqual(handoff_intent_contract["run_id"], "run-slice1-2")
            self.assertEqual(handoff_intent_contract["handoff_scope"], "resolution_to_handoff_only")
            self.assertEqual(
                handoff_intent_contract["request_to_product_resolution_ref"]["contract_id"],
                "request-to-product-resolution-req-1",
            )
            self.assertEqual(
                handoff_intent_contract["handoff_intent"]["intent"],
                "prepare_structured_product_handoff",
            )
            self.assertNotIn("selected_provider", handoff_intent_contract)
            self.assertNotIn("selected_node", handoff_intent_contract)
            self.assertNotIn("reason_codes", handoff_intent_contract)
            execution_preparation_contract = json.loads(
                (run_root / "manifests" / "product-execution-preparation-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_preparation_contract["request_id"], "req-1")
            self.assertEqual(execution_preparation_contract["run_id"], "run-slice1-2")
            self.assertEqual(
                execution_preparation_contract["preparation_scope"],
                "product_execution_preparation_only",
            )
            self.assertEqual(
                execution_preparation_contract["request_to_product_resolution_ref"]["contract_id"],
                "request-to-product-resolution-req-1",
            )
            self.assertEqual(
                execution_preparation_contract["resolution_to_handoff_intent_ref"]["contract_id"],
                "resolution-to-handoff-intent-req-1",
            )
            self.assertEqual(
                execution_preparation_contract["execution_preparation"]["preparation_mode"],
                "pre_routing_pre_provider",
            )
            self.assertNotIn("selected_provider", execution_preparation_contract)
            self.assertNotIn("selected_node", execution_preparation_contract)
            self.assertNotIn("execution_id", execution_preparation_contract)
            execution_result_contract = json.loads(
                (run_root / "manifests" / "product-execution-result-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_result_contract["request_id"], "req-1")
            self.assertEqual(execution_result_contract["run_id"], "run-slice1-2")
            self.assertEqual(
                execution_result_contract["result_scope"],
                "product_execution_result_only",
            )
            self.assertEqual(
                execution_result_contract["product_execution_preparation_ref"]["contract_id"],
                "product-execution-preparation-req-1",
            )
            self.assertEqual(
                execution_result_contract["execution_result"]["execution_id"],
                "execution-req-1",
            )
            self.assertEqual(execution_result_contract["execution_result"]["status"], "succeeded")
            self.assertNotIn("selected_provider", execution_result_contract)
            self.assertNotIn("selected_node", execution_result_contract)
            self.assertNotIn("approval_status", execution_result_contract)

    def test_authoritative_projection_keeps_traceability_to_run_and_source_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            summary = materialize_run_outputs("run-slice3-1", _sample_payloads("run-slice3-1"), repo_root=repo_root)

            projection_root = resolve_artifact_projection_root(
                "artifact-authoritative-req-1",
                repo_root=repo_root,
            )
            metadata = json.loads((projection_root / "projection-metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(summary["authoritative_projection"]["projected_count"], 1)
            self.assertEqual(metadata["run_id"], "run-slice3-1")
            self.assertEqual(metadata["source_stage"], "execution")
            self.assertEqual(metadata["projection_scope"], "authoritative")
            self.assertFalse((projection_root.parent / "artifact-selected-req-1").exists())

    def test_reference_index_and_current_exchange_pointer_remain_coherent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-sliceD-1")
            payloads["close_or_continue"]["decision"] = "continue_pending"
            payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]

            summary = materialize_run_outputs("run-sliceD-1", payloads, repo_root=repo_root)

            run_root = Path(summary["run_root"])
            exchange_root = Path(summary["exchange"]["exchange_root"])
            reference_index = json.loads((run_root / "final" / "reference-index.json").read_text(encoding="utf-8"))
            current_pointer = json.loads((exchange_root / "current.json").read_text(encoding="utf-8"))
            current_task_state = json.loads(
                (exchange_root / "current-task-state.json").read_text(encoding="utf-8")
            )
            recovery_contract = json.loads(
                (exchange_root / "continue-pending-recovery.json").read_text(encoding="utf-8")
            )
            active_pointer = json.loads(
                (exchange_root.parent / "active-pointer.json").read_text(encoding="utf-8")
            )

            self.assertEqual(reference_index["run_id"], "run-sliceD-1")
            self.assertTrue(reference_index["exchange_current_task"]["materialized"])
            self.assertEqual(
                reference_index["exchange_current_task"]["current_reference_path"],
                str(exchange_root / "current.json"),
            )
            self.assertEqual(current_pointer["reference_index_path"], str(run_root / "final" / "reference-index.json"))
            self.assertEqual(current_pointer["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(
                reference_index["exchange_current_task"]["persistence_state_path"],
                str(exchange_root / "current-task-state.json"),
            )
            self.assertTrue(summary["current_task_persistence"]["persisted"])
            self.assertEqual(summary["current_task_persistence"]["current_task_id"], "current-task-run-sliceD-1")
            self.assertEqual(current_task_state["current_reference_path"], str(exchange_root / "current.json"))
            self.assertEqual(current_task_state["reference_index_path"], str(run_root / "final" / "reference-index.json"))
            self.assertEqual(current_task_state["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(current_task_state["persistence_scope"], "workspace_exchange_current_task")
            self.assertTrue(summary["recovery_contract"]["recovery_ready"])
            self.assertEqual(
                summary["recovery_contract"]["recovery_contract_path"],
                str(exchange_root / "continue-pending-recovery.json"),
            )
            self.assertEqual(
                reference_index["continuation"]["recovery_contract_path"],
                str(exchange_root / "continue-pending-recovery.json"),
            )
            self.assertEqual(recovery_contract["current_task_persistence_state_path"], str(exchange_root / "current-task-state.json"))
            self.assertEqual(recovery_contract["continuation_state_path"], str(run_root / "final" / "continuation-state.json"))
            self.assertEqual(recovery_contract["current_reference_path"], str(exchange_root / "current.json"))
            self.assertEqual(recovery_contract["recovery_scope"], "continue_pending_current_task")
            self.assertTrue(summary["current_task_pointer"]["active_pointer_written"])
            self.assertFalse(summary["current_task_pointer"]["superseded_previous"])
            self.assertEqual(
                reference_index["exchange_current_task"]["active_pointer_path"],
                str(exchange_root.parent / "active-pointer.json"),
            )
            self.assertEqual(reference_index["exchange_current_task"]["supersede_trace_path"], "")
            self.assertEqual(active_pointer["run_id"], "run-sliceD-1")
            self.assertEqual(active_pointer["current_task_persistence_state_path"], str(exchange_root / "current-task-state.json"))
            self.assertEqual(active_pointer["recovery_contract_path"], str(exchange_root / "continue-pending-recovery.json"))
            self.assertFalse(active_pointer["superseded_previous"])

    def test_active_pointer_supersede_trace_links_to_previous_current_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))

            first_payloads = _sample_payloads("run-sliceC-1")
            first_payloads["close_or_continue"]["decision"] = "continue_pending"
            first_payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            first_payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            first_payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            first_payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]
            first_summary = materialize_run_outputs("run-sliceC-1", first_payloads, repo_root=repo_root)

            second_payloads = _sample_payloads("run-sliceC-2")
            second_payloads["close_or_continue"]["decision"] = "continue_pending"
            second_payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            second_payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            second_payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            second_payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]
            second_summary = materialize_run_outputs("run-sliceC-2", second_payloads, repo_root=repo_root)

            second_exchange_root = Path(second_summary["exchange"]["exchange_root"])
            active_pointer = json.loads((second_exchange_root.parent / "active-pointer.json").read_text(encoding="utf-8"))
            supersede_trace = json.loads((second_exchange_root / "supersede-trace.json").read_text(encoding="utf-8"))

            self.assertTrue(second_summary["current_task_pointer"]["active_pointer_written"])
            self.assertTrue(second_summary["current_task_pointer"]["superseded_previous"])
            self.assertEqual(active_pointer["run_id"], "run-sliceC-2")
            self.assertTrue(active_pointer["superseded_previous"])
            self.assertEqual(active_pointer["supersede_trace_path"], str(second_exchange_root / "supersede-trace.json"))
            self.assertEqual(supersede_trace["previous_run_id"], "run-sliceC-1")
            self.assertEqual(
                supersede_trace["previous_current_task_state_path"],
                first_summary["current_task_persistence"]["persistence_state_path"],
            )
            self.assertEqual(
                supersede_trace["previous_recovery_contract_path"],
                first_summary["recovery_contract"]["recovery_contract_path"],
            )
            self.assertEqual(
                second_summary["reference_index"]["exchange_current_task"]["supersede_trace_path"],
                str(second_exchange_root / "supersede-trace.json"),
            )

    def test_retention_summary_marks_deprecated_artifacts_cleanup_eligible_after_close(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-slice4-1")
            payloads["artifacts"]["items"].append(
                {
                    "artifact_id": "artifact-deprecated-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "deprecated",
                    "source_stage": "execution",
                    "source_ref": "artifact-authoritative-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                }
            )
            payloads["close_or_continue"]["decision"] = "close_rejected"

            summary = materialize_run_outputs("run-slice4-1", payloads, repo_root=repo_root)

            self.assertEqual(summary["retention"]["close_or_continue"], "close_rejected")
            self.assertEqual(len(summary["retention"]["cleanup_eligible_artifacts"]), 1)
            self.assertEqual(
                summary["retention"]["cleanup_eligible_artifacts"][0]["artifact_id"],
                "artifact-deprecated-req-1",
            )
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            projection_root = Path(summary["authoritative_projection"]["items"][0]["projection_root"])
            self.assertTrue(projection_root.is_dir())

    def test_continue_pending_retains_deprecated_artifacts_without_cleanup_eligibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = _build_fake_repo_root(Path(temp_dir))
            payloads = _sample_payloads("run-slice4-2")
            payloads["artifacts"]["items"].append(
                {
                    "artifact_id": "artifact-deprecated-req-1",
                    "artifact_type": "execution_output",
                    "artifact_state": "deprecated",
                    "source_stage": "execution",
                    "source_ref": "artifact-authoritative-req-1",
                    "artifact_freshness": "current",
                    "authoritative": False,
                }
            )
            payloads["close_or_continue"]["decision"] = "continue_pending"
            payloads["exchange_boundary_decision"]["close_or_continue"] = "continue_pending"
            payloads["exchange_boundary_decision"]["boundary_mode"] = "external_exchange_candidate"
            payloads["exchange_boundary_decision"]["requires_exchange_boundary"] = True
            payloads["exchange_boundary_decision"]["reason_codes"] = [
                "continue_pending_requires_external_handoff_boundary"
            ]

            summary = materialize_run_outputs("run-slice4-2", payloads, repo_root=repo_root)

            self.assertEqual(summary["retention"]["retention_mode"], "retain_for_continuation")
            self.assertEqual(summary["retention"]["cleanup_eligible_artifacts"], [])
            self.assertEqual(summary["retention"]["cleanup_actions"], [])
            self.assertTrue(summary["exchange_boundary"]["requires_exchange_boundary"])
            self.assertEqual(summary["exchange_boundary"]["exchange_materialization_status"], "materialized_current_task")
            self.assertTrue(summary["exchange"]["materialized"])
            self.assertTrue(summary["continuation"]["continuation_required"])
            self.assertEqual(summary["continuation"]["current_source"], "exchange_current_task")
            self.assertEqual(summary["continuation"]["exchange_boundary_mode"], "external_exchange_candidate")
            self.assertTrue(summary["reference_index"]["exchange_current_task"]["materialized"])
            self.assertEqual(
                summary["reference_index"]["continuation"]["current_source"],
                "exchange_current_task",
            )
            exchange_root = Path(summary["exchange"]["exchange_root"])
            self.assertTrue((exchange_root / "exchange-bundle.json").is_file())
            self.assertTrue((exchange_root / "exchange-metadata.json").is_file())
            self.assertTrue((exchange_root / "current.json").is_file())
            self.assertTrue((exchange_root / "current-task-state.json").is_file())
            self.assertTrue((exchange_root / "continue-pending-recovery.json").is_file())
            self.assertTrue((exchange_root.parent / "active-pointer.json").is_file())
            self.assertFalse((repo_root / "exchange").exists())


if __name__ == "__main__":
    unittest.main()
