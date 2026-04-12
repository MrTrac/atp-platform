"""Unit tests for ATP AOKP knowledge adapter (mocked HTTP)."""

from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from adapters.aokp.aokp_adapter import (
    check_health,
    query_graph,
    query_knowledge,
)


def _mock_response(body: dict) -> MagicMock:
    """Build a mock urlopen response returning JSON."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestCheckHealth(unittest.TestCase):

    @patch("adapters.aokp.aokp_adapter.urlopen")
    def test_returns_ok_when_reachable(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"registeredSources": 5})
        result = check_health(base_url="http://localhost:3002")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "aokp")

    @patch("adapters.aokp.aokp_adapter.urlopen", side_effect=URLError("refused"))
    def test_returns_unavailable_when_down(self, mock_urlopen: MagicMock) -> None:
        result = check_health(base_url="http://localhost:3002")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["provider"], "aokp")


class TestQueryKnowledge(unittest.TestCase):

    @patch("adapters.aokp.aokp_adapter.urlopen")
    def test_success_returns_hits_and_context(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "hits": [
                {"title": "ASTERIX SIC", "snippet": "Installation guide...", "authoritySignal": "authoritative"},
                {"title": "Radar Config", "snippet": "PSR/SSR setup...", "authoritySignal": "reference"},
            ],
            "total": 2,
            "mode": "lexical-phase1",
        })
        result = query_knowledge({"query": "ASTERIX SIC installation"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["hits"]), 2)
        self.assertIn("ASTERIX SIC", result["context_text"])
        self.assertIsNone(result["error"])
        self.assertIn("response_time_ms", result["manifest"])

    def test_empty_query_returns_error(self) -> None:
        result = query_knowledge({"query": ""})
        self.assertEqual(result["status"], "failed")
        self.assertIn("required", result["error"])

    @patch("adapters.aokp.aokp_adapter.urlopen", side_effect=URLError("refused"))
    def test_aokp_down_returns_structured_error(self, mock_urlopen: MagicMock) -> None:
        result = query_knowledge({"query": "test query"})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["hits"], [])
        self.assertIn("failed", result["error"])

    @patch("adapters.aokp.aokp_adapter.urlopen")
    def test_no_hits_returns_empty_status(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"hits": [], "total": 0, "mode": "lexical-phase1"})
        result = query_knowledge({"query": "nonexistent topic"})
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["context_text"], "")


class TestQueryGraph(unittest.TestCase):

    @patch("adapters.aokp.aokp_adapter.urlopen")
    def test_success_returns_entities(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "entities": [{"entityId": "e1", "label": "FDP", "kind": "subsystem"}],
            "relations": [{"from": "e1", "to": "e2", "kind": "belongs_to"}],
        })
        result = query_graph({"term": "FDP"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["entities"]), 1)
        self.assertEqual(len(result["relations"]), 1)

    def test_empty_term_returns_error(self) -> None:
        result = query_graph({"term": ""})
        self.assertEqual(result["status"], "failed")
        self.assertIn("required", result["error"])

    @patch("adapters.aokp.aokp_adapter.urlopen", side_effect=URLError("refused"))
    def test_aokp_down_returns_structured_error(self, mock_urlopen: MagicMock) -> None:
        result = query_graph({"term": "FDP"})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["entities"], [])


if __name__ == "__main__":
    unittest.main()
