"""Unit tests for ATP bridge context enrichment (mocked AOKP)."""

from __future__ import annotations

import unittest
from unittest.mock import patch


class TestContextEnrichment(unittest.TestCase):

    @patch("bridge.context_enrichment.AOKP_ENABLED", False)
    def test_disabled_returns_unchanged(self) -> None:
        from bridge.context_enrichment import enrich_context
        incoming = {"text": "test query", "model": "ollama/qwen3:14b"}
        result = enrich_context(incoming)
        self.assertIs(result, incoming)
        self.assertNotIn("aokp_context", result)

    @patch("bridge.context_enrichment.AOKP_ENABLED", True)
    @patch("bridge.context_enrichment.check_health", return_value={"status": "unavailable"})
    def test_aokp_unavailable_returns_unchanged(self, mock_health: object) -> None:
        from bridge.context_enrichment import enrich_context
        incoming = {"text": "test query"}
        result = enrich_context(incoming)
        self.assertNotIn("aokp_context", result)

    @patch("bridge.context_enrichment.AOKP_ENABLED", True)
    @patch("bridge.context_enrichment.check_health", return_value={"status": "ok"})
    @patch("bridge.context_enrichment.query_knowledge", return_value={
        "status": "success",
        "hits": [{"title": "Doc1", "snippet": "content..."}],
        "context_text": "[1] Doc1 (authority: authoritative)\n    content...",
        "manifest": {"response_time_ms": 50, "hit_count": 1},
    })
    def test_enrichment_adds_aokp_context(self, mock_query: object, mock_health: object) -> None:
        from bridge.context_enrichment import enrich_context
        incoming = {"text": "test query", "model": "ollama/qwen3:14b"}
        result = enrich_context(incoming)
        self.assertIn("aokp_context", result)
        self.assertIn("context_text", result["aokp_context"])
        self.assertEqual(result["aokp_context"]["hit_count"], 1)

    @patch("bridge.context_enrichment.AOKP_ENABLED", True)
    @patch("bridge.context_enrichment.check_health", return_value={"status": "ok"})
    @patch("bridge.context_enrichment.query_knowledge", return_value={
        "status": "success",
        "hits": [{"title": "Doc1"}],
        "context_text": "knowledge text",
        "manifest": {},
    })
    def test_enrichment_preserves_original_fields(self, mock_query: object, mock_health: object) -> None:
        from bridge.context_enrichment import enrich_context
        incoming = {"text": "my query", "model": "ollama/qwen3:14b", "context": "system prompt"}
        result = enrich_context(incoming)
        self.assertEqual(result["text"], "my query")
        self.assertEqual(result["model"], "ollama/qwen3:14b")
        self.assertEqual(result["context"], "system prompt")

    @patch("bridge.context_enrichment.AOKP_ENABLED", True)
    @patch("bridge.context_enrichment.check_health", return_value={"status": "ok"})
    @patch("bridge.context_enrichment.query_knowledge", return_value={
        "status": "empty", "hits": [], "context_text": "", "manifest": {},
    })
    def test_no_hits_returns_unchanged(self, mock_query: object, mock_health: object) -> None:
        from bridge.context_enrichment import enrich_context
        incoming = {"text": "obscure query"}
        result = enrich_context(incoming)
        self.assertNotIn("aokp_context", result)


if __name__ == "__main__":
    unittest.main()
