"""Unit tests for v1.2 registry-driven executor dispatch and route discovery."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.execution.executor import (
    EXECUTOR_MAP,
    ExecutionError,
    invoke_executor,
    register_executor,
)
from core.routing.route_prepare import (
    REGISTRY_ROOT,
    RoutePreparationError,
    _discover_active_nodes,
    _discover_active_providers,
)


class TestExecutorDispatchMap(unittest.TestCase):
    """Verify executor uses EXECUTOR_MAP for provider dispatch."""

    def test_executor_map_contains_known_providers(self) -> None:
        self.assertIn("non_llm_execution", EXECUTOR_MAP)
        self.assertIn("ollama", EXECUTOR_MAP)
        self.assertIn("anthropic", EXECUTOR_MAP)

    def test_executor_map_handlers_are_callable(self) -> None:
        for provider, handler in EXECUTOR_MAP.items():
            self.assertTrue(callable(handler), f"Handler for {provider} is not callable")

    def test_unknown_provider_with_node_falls_back_to_remote(self) -> None:
        result = invoke_executor(
            {"payload": {}},
            {"selected_provider": "unknown_provider", "selected_node": "some_node"},
        )
        self.assertEqual(result["status"], "deferred")

    def test_empty_provider_and_node_raises_execution_error(self) -> None:
        with self.assertRaisesRegex(ExecutionError, "Unsupported execution route"):
            invoke_executor({}, {"selected_provider": "", "selected_node": ""})

    def test_register_executor_adds_new_provider(self) -> None:
        def _mock_handler(
            normalized_request: dict[str, Any],
            routing_result: dict[str, Any],
        ) -> dict[str, Any]:
            return {"status": "mock_ok"}

        register_executor("test_provider", _mock_handler)
        try:
            self.assertIn("test_provider", EXECUTOR_MAP)
            result = invoke_executor(
                {},
                {"selected_provider": "test_provider", "selected_node": "any"},
            )
            self.assertEqual(result["status"], "mock_ok")
        finally:
            EXECUTOR_MAP.pop("test_provider", None)

    def test_non_llm_execution_dispatches_through_map(self) -> None:
        result = invoke_executor(
            {"payload": {"command_argv": ["echo", "dispatch_test"]}},
            {"selected_provider": "non_llm_execution", "selected_node": "local_mac"},
        )
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("dispatch_test", result["stdout"])


class TestRegistryDiscovery(unittest.TestCase):
    """Verify route_prepare discovers providers and nodes from registry."""

    def test_discover_active_providers_finds_all_three(self) -> None:
        providers = _discover_active_providers()
        provider_names = [p.get("provider") for p in providers]
        self.assertIn("non_llm_execution", provider_names)
        self.assertIn("ollama", provider_names)
        self.assertIn("anthropic", provider_names)

    def test_discover_active_providers_only_returns_active(self) -> None:
        providers = _discover_active_providers()
        for p in providers:
            self.assertEqual(p.get("status"), "active")

    def test_discover_active_nodes_finds_local_mac(self) -> None:
        nodes = _discover_active_nodes()
        node_names = [n.get("node") for n in nodes]
        self.assertIn("local_mac", node_names)

    def test_discover_active_nodes_only_returns_active(self) -> None:
        nodes = _discover_active_nodes()
        for n in nodes:
            self.assertEqual(n.get("status"), "active")

    def test_registry_root_points_to_registry_directory(self) -> None:
        self.assertTrue(REGISTRY_ROOT.is_dir())
        self.assertTrue((REGISTRY_ROOT / "providers").is_dir())
        self.assertTrue((REGISTRY_ROOT / "nodes").is_dir())

    def test_new_registry_yaml_files_are_loadable(self) -> None:
        from core.intake.loader import load_request

        ollama = load_request(REGISTRY_ROOT / "providers" / "ollama_local.yaml")
        self.assertEqual(ollama["provider"], "ollama")
        self.assertEqual(ollama["provider_type"], "llm")

        anthropic = load_request(REGISTRY_ROOT / "providers" / "anthropic_cloud.yaml")
        self.assertEqual(anthropic["provider"], "anthropic")
        self.assertEqual(anthropic["provider_type"], "llm")

    def test_llm_capabilities_are_loadable(self) -> None:
        from core.intake.loader import load_request

        chat = load_request(REGISTRY_ROOT / "capabilities" / "llm_chat.yaml")
        self.assertEqual(chat["capability"], "llm_chat")
        self.assertEqual(chat["category"], "llm")

        completion = load_request(REGISTRY_ROOT / "capabilities" / "llm_completion.yaml")
        self.assertEqual(completion["capability"], "llm_completion")


class TestSchemaMetadata(unittest.TestCase):
    """Verify all schemas have required metadata fields."""

    SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"

    def test_all_schemas_have_dollar_schema(self) -> None:
        from core.intake.loader import load_request

        for schema_file in self.SCHEMA_ROOT.rglob("*.schema.yaml"):
            data = load_request(schema_file)
            self.assertIn(
                "$schema", data,
                f"Missing $schema in {schema_file.relative_to(self.SCHEMA_ROOT)}",
            )

    def test_all_schemas_have_title(self) -> None:
        from core.intake.loader import load_request

        for schema_file in self.SCHEMA_ROOT.rglob("*.schema.yaml"):
            data = load_request(schema_file)
            self.assertIn(
                "title", data,
                f"Missing title in {schema_file.relative_to(self.SCHEMA_ROOT)}",
            )

    def test_all_schemas_have_version(self) -> None:
        from core.intake.loader import load_request

        for schema_file in self.SCHEMA_ROOT.rglob("*.schema.yaml"):
            data = load_request(schema_file)
            self.assertIn(
                "x-schema-version", data,
                f"Missing x-schema-version in {schema_file.relative_to(self.SCHEMA_ROOT)}",
            )

    def test_all_schema_subdirs_have_readme(self) -> None:
        for subdir in self.SCHEMA_ROOT.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                readme = subdir / "README.md"
                self.assertTrue(
                    readme.is_file(),
                    f"Missing README.md in schemas/{subdir.name}/",
                )


class TestAokpRegistryEntries(unittest.TestCase):
    """Verify AOKP-related registry entries are loadable."""

    def test_aokp_provider_yaml_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(REGISTRY_ROOT / "providers" / "aokp_knowledge.yaml")
        self.assertEqual(entry["provider"], "aokp")
        self.assertEqual(entry["provider_type"], "knowledge")
        self.assertEqual(entry["status"], "active")

    def test_knowledge_retrieval_capability_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(REGISTRY_ROOT / "capabilities" / "knowledge_retrieval.yaml")
        self.assertEqual(entry["capability"], "knowledge_retrieval")
        self.assertEqual(entry["category"], "knowledge")

    def test_graph_query_capability_loadable(self) -> None:
        from core.intake.loader import load_request
        entry = load_request(REGISTRY_ROOT / "capabilities" / "graph_query.yaml")
        self.assertEqual(entry["capability"], "graph_query")

    def test_local_mac_supports_knowledge_provider_type(self) -> None:
        from core.intake.loader import load_request
        node = load_request(REGISTRY_ROOT / "nodes" / "local_mac.yaml")
        self.assertIn("knowledge", node["supported_provider_types"])

    def test_discover_providers_includes_aokp(self) -> None:
        providers = _discover_active_providers()
        provider_names = [p.get("provider") for p in providers]
        self.assertIn("aokp", provider_names)


if __name__ == "__main__":
    unittest.main()
