"""Unit tests for ATP generator: report (D5.2).

Covers the registry dispatch + the two branches of report.run() that
shipped in D5.2 phase 1 (no-context fallback + context-concat skeleton).
The LLM-driven branch lands in W17-W18 phase 2 and gets its own tests
then.
"""

from __future__ import annotations

import unittest

import generators


class TestReportRegistration(unittest.TestCase):
    def test_descriptor_in_registry(self) -> None:
        names = {d.name for d in generators.list_generators()}
        self.assertIn("report", names)
        d = generators.get_generator("report").descriptor
        self.assertEqual(d.lifecycle, "incubating")
        self.assertEqual(d.source_aokp_module, "src/runtime/synthesis/")
        self.assertEqual(d.params_schema["required"], ["query"])

    def test_registry_version_stable_across_calls(self) -> None:
        v1 = generators.registry_version()
        v2 = generators.registry_version()
        self.assertEqual(v1, v2)
        self.assertEqual(len(v1), 64)  # SHA256 hex


class TestReportNoContextFallback(unittest.TestCase):
    def _run(self, **payload):
        entry = generators.get_generator("report")
        req = generators.GeneratorRequest(
            request_id="test-no-ctx",
            payload=payload,
            consumer="internal",
        )
        return entry.handler(req)

    def test_vi_locale_no_context_returns_vn_fallback(self) -> None:
        r = self._run(query="Hỏi gì đó", locale="vi")
        self.assertEqual(r.status, "success")
        self.assertIn("Không tìm thấy", r.answer)
        self.assertEqual(r.citations, [])
        self.assertEqual(r.run_id, "syn_report_test-no-ctx")

    def test_en_locale_no_context_returns_en_fallback(self) -> None:
        r = self._run(query="any question", locale="en")
        self.assertEqual(r.status, "success")
        self.assertIn("No relevant information", r.answer)

    def test_unknown_locale_falls_back_to_vi(self) -> None:
        r = self._run(query="any", locale="zz")
        self.assertIn("Không tìm thấy", r.answer)

    def test_empty_query_fails(self) -> None:
        r = self._run(query="")
        self.assertEqual(r.status, "failed")
        self.assertIn("query is required", r.diagnostics)


class TestReportContextSynthesis(unittest.TestCase):
    def _run_with_chunks(self):
        entry = generators.get_generator("report")
        req = generators.GeneratorRequest(
            request_id="test-with-ctx",
            payload={
                "query": "What is HCMOPS?",
                "locale": "en",
                "context_chunks": [
                    {
                        "artifact_id": "art-1",
                        "source_id": "src-managair",
                        "title": "ManagAIR overview",
                        "snippet": "HCMOPS is the operational namespace.",
                        "classification_path": ["ecosystem", "platform", "aokp"],
                        "relevance_score": 0.91,
                    },
                    {
                        "artifact_id": "art-2",
                        "source_id": "src-aftn",
                        "title": "AFTN routing",
                        "snippet": "AFTN messages flow through gateway.",
                        "relevance_score": 0.74,
                    },
                ],
            },
            consumer="AIOS-OC",
        )
        return entry.handler(req)

    def test_returns_partial_status(self) -> None:
        r = self._run_with_chunks()
        self.assertEqual(r.status, "partial")  # placeholder, not full LLM synthesis
        self.assertEqual(r.generator, "report")

    def test_answer_contains_query_and_chunk_titles(self) -> None:
        r = self._run_with_chunks()
        self.assertIn("What is HCMOPS?", r.answer)
        self.assertIn("ManagAIR overview", r.answer)
        self.assertIn("AFTN routing", r.answer)
        self.assertIn("Synthesis stub", r.answer)

    def test_citations_preserve_chunk_metadata(self) -> None:
        r = self._run_with_chunks()
        self.assertEqual(len(r.citations), 2)
        c1, c2 = r.citations
        self.assertEqual(c1.artifact_id, "art-1")
        self.assertEqual(c1.classification_path, ("ecosystem", "platform", "aokp"))
        self.assertAlmostEqual(c1.relevance_score, 0.91)
        self.assertEqual(c1.rank, 1)
        self.assertEqual(c2.rank, 2)

    def test_usage_tracks_output_tokens(self) -> None:
        r = self._run_with_chunks()
        self.assertGreater(r.usage["output_tokens"], 0)

    def test_diagnostics_flag_skeletal_mode(self) -> None:
        r = self._run_with_chunks()
        self.assertTrue(any("skeletal synthesis" in d for d in r.diagnostics))
        self.assertTrue(any("chunk_count=2" in d for d in r.diagnostics))


if __name__ == "__main__":
    unittest.main()
