"""Integration tests for AOKP knowledge adapter (requires AOKP at localhost:3002)."""

from __future__ import annotations

import unittest
from urllib.error import URLError
from urllib.request import urlopen

from adapters.aokp.aokp_adapter import check_health, query_graph, query_knowledge


def _aokp_available() -> bool:
    """Check if AOKP is reachable at localhost:3002."""
    try:
        with urlopen("http://localhost:3002/api/phase1/status", timeout=3):
            return True
    except (URLError, OSError):
        return False


@unittest.skipUnless(_aokp_available(), "AOKP not reachable at localhost:3002")
class TestAokpIntegration(unittest.TestCase):

    def test_health_check_returns_ok(self) -> None:
        result = check_health()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "aokp")

    def test_search_returns_results(self) -> None:
        result = query_knowledge({"query": "ManagAIR", "top_k": 3})
        self.assertIn(result["status"], ("success", "empty"))
        self.assertIsInstance(result["hits"], list)
        self.assertIn("response_time_ms", result["manifest"])

    def test_graph_query_returns_entities(self) -> None:
        result = query_graph({"term": "FDP"})
        self.assertIn(result["status"], ("success", "empty"))
        self.assertIsInstance(result["entities"], list)

    def test_search_with_filters(self) -> None:
        result = query_knowledge({
            "query": "ASTERIX",
            "top_k": 5,
            "filters": {"authoritySignal": "authoritative"},
        })
        self.assertIn(result["status"], ("success", "empty"))


if __name__ == "__main__":
    unittest.main()
