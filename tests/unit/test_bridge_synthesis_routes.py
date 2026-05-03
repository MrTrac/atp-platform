"""Unit tests for ATP bridge synthesis routes (D5.x phase 1).

These exercise the pure-function dispatch helpers in bridge_server.py
without spinning up an HTTPServer — the HTTP-layer wiring is a thin
adapter around `_handle_synthesis_generate(body)` and
`_build_synthesis_generators_response()`, so testing those functions
covers the route logic deterministically.
"""

from __future__ import annotations

import unittest

from bridge.bridge_server import (
    _build_synthesis_generators_response,
    _citation_to_dict,
    _descriptor_to_dict,
    _handle_synthesis_generate,
    _synthesis_result_to_dict,
)
import generators


class TestGeneratorsListRoute(unittest.TestCase):
    def test_response_includes_all_8_generators(self) -> None:
        resp = _build_synthesis_generators_response()
        self.assertIn("generators", resp)
        self.assertIn("registry_version", resp)
        names = {g["name"] for g in resp["generators"]}
        self.assertEqual(
            names,
            {
                "react",
                "tot",
                "graphrag_synth",
                "federation",
                "temporal",
                "report",
                "analyze",
                "transform",
            },
        )

    def test_descriptor_keys_match_z2_contract(self) -> None:
        resp = _build_synthesis_generators_response()
        first = resp["generators"][0]
        self.assertEqual(
            set(first.keys()),
            {"name", "version", "lifecycle", "description", "source_aokp_module", "params_schema"},
        )

    def test_registry_version_is_sha256(self) -> None:
        resp = _build_synthesis_generators_response()
        self.assertEqual(len(resp["registry_version"]), 64)


class TestGenerateRoute(unittest.TestCase):
    def test_missing_generator_returns_400(self) -> None:
        status, payload = _handle_synthesis_generate({})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "missing_generator")

    def test_unknown_generator_returns_404_with_available_list(self) -> None:
        status, payload = _handle_synthesis_generate({"generator": "nonexistent"})
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "generator_not_found")
        self.assertIn("report", payload["available"])
        self.assertEqual(len(payload["available"]), 8)

    def test_params_must_be_object(self) -> None:
        status, payload = _handle_synthesis_generate({"generator": "report", "params": "string"})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "params_not_object")

    def test_unported_stub_returns_501(self) -> None:
        # `react` is still NotImplementedError-only (D5.x deferred)
        status, payload = _handle_synthesis_generate(
            {"generator": "react", "params": {"query": "anything"}},
        )
        self.assertEqual(status, 501)
        self.assertEqual(payload["error"], "not_implemented")
        self.assertEqual(payload["generator"], "react")

    def test_report_no_context_dispatches_successfully(self) -> None:
        status, payload = _handle_synthesis_generate(
            {
                "generator": "report",
                "params": {"query": "hi", "locale": "en"},
                "consumer": "AIOS-OC",
                "request_id": "test-route-1",
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["generator"], "report")
        self.assertEqual(payload["run_id"], "syn_report_test-route-1")
        self.assertIn("No relevant information", payload["answer"])

    def test_report_with_chunks_returns_partial_with_citations(self) -> None:
        status, payload = _handle_synthesis_generate(
            {
                "generator": "report",
                "params": {
                    "query": "What is HCMOPS?",
                    "locale": "en",
                    "context_chunks": [
                        {
                            "artifact_id": "art-1",
                            "source_id": "src-1",
                            "title": "ManagAIR",
                            "snippet": "HCMOPS is a namespace.",
                            "classification_path": ["ecosystem", "platform", "aokp"],
                            "relevance_score": 0.9,
                        },
                    ],
                },
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(len(payload["citations"]), 1)
        cit = payload["citations"][0]
        self.assertEqual(cit["artifact_id"], "art-1")
        self.assertEqual(cit["classification_path"], ["ecosystem", "platform", "aokp"])
        self.assertEqual(cit["rank"], 1)

    def test_analyze_subset_metric_dispatches(self) -> None:
        status, payload = _handle_synthesis_generate(
            {
                "generator": "analyze",
                "params": {
                    "query": "eval-1",
                    "metrics": ["faithfulness"],
                    "pairs": [{"question": "q", "answer": "x", "contexts": ["x"]}],
                },
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(set(payload["usage"]["metric_means"].keys()), {"faithfulness"})

    def test_transform_decompose_mode_returns_intent(self) -> None:
        status, payload = _handle_synthesis_generate(
            {
                "generator": "transform",
                "params": {"query": "What is X and Y?", "mode": "decompose"},
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["usage"]["intent"], "multi-hop")

    def test_transform_invalid_mode_returns_failed_status(self) -> None:
        # Generator returns status=failed (HTTP 200, error in body) — keeps
        # 4xx for transport-level errors (missing generator / bad json) and
        # generator-level errors land in the SynthesisResult's status field.
        status, payload = _handle_synthesis_generate(
            {"generator": "transform", "params": {"query": "ok", "mode": "warp"}},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "failed")


class TestSerializers(unittest.TestCase):
    def test_descriptor_serializer_round_trip(self) -> None:
        d = generators.list_generators()[0]
        out = _descriptor_to_dict(d)
        self.assertEqual(out["name"], d.name)
        self.assertEqual(out["version"], d.version)

    def test_citation_serializer_handles_tuple_path(self) -> None:
        c = generators.Citation(
            artifact_id="a",
            source_id="s",
            snippet="text",
            classification_path=("a", "b"),
            relevance_score=0.5,
            rank=1,
        )
        out = _citation_to_dict(c)
        self.assertEqual(out["classification_path"], ["a", "b"])

    def test_synthesis_result_serializer_drops_internal_fields(self) -> None:
        r = generators.SynthesisResult(
            run_id="syn_x", generator="report", status="success", answer="hi",
        )
        out = _synthesis_result_to_dict(r)
        self.assertNotIn("__class__", out)
        self.assertEqual(out["citations"], [])
        self.assertEqual(out["diagnostics"], [])


if __name__ == "__main__":
    unittest.main()
