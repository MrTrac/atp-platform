"""Unit tests for ATP bridge introspection endpoint helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure project root is on path
_project_root = str(Path(__file__).resolve().parents[2])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bridge.bridge_server import (
    _build_capabilities_response,
    _build_providers_response,
    _build_status_response,
)


class TestBridgeIntrospection(unittest.TestCase):

    def test_status_response_has_required_keys(self) -> None:
        resp = _build_status_response()
        self.assertEqual(resp["status"], "ok")
        self.assertIn("version", resp)
        self.assertIn("providers", resp)
        self.assertIn("provider_count", resp)
        self.assertIn("nodes", resp)
        self.assertIn("aokp", resp)
        self.assertIn("timestamp", resp)

    def test_status_providers_match_registry(self) -> None:
        resp = _build_status_response()
        self.assertIn("non_llm_execution", resp["providers"])
        self.assertIn("ollama", resp["providers"])
        self.assertIn("anthropic", resp["providers"])
        self.assertIn("aokp", resp["providers"])
        self.assertEqual(resp["provider_count"], len(resp["providers"]))

    def test_providers_response_has_details(self) -> None:
        resp = _build_providers_response()
        self.assertIn("providers", resp)
        self.assertIn("count", resp)
        self.assertGreaterEqual(resp["count"], 4)
        for p in resp["providers"]:
            self.assertIn("provider", p)
            self.assertIn("provider_type", p)
            self.assertIn("capabilities", p)

    def test_capabilities_response_lists_all(self) -> None:
        resp = _build_capabilities_response()
        self.assertIn("capabilities", resp)
        self.assertIn("count", resp)
        cap_names = [c["capability"] for c in resp["capabilities"]]
        self.assertIn("shell_execution", cap_names)
        self.assertIn("llm_chat", cap_names)
        self.assertIn("knowledge_retrieval", cap_names)
        self.assertIn("graph_query", cap_names)

    def test_capabilities_have_description(self) -> None:
        resp = _build_capabilities_response()
        for cap in resp["capabilities"]:
            self.assertIn("capability", cap)
            self.assertIn("category", cap)
            self.assertIn("description", cap)


if __name__ == "__main__":
    unittest.main()
