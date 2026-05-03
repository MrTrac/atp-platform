"""Unit tests for ATP generators: analyze (D5.3) + transform (D5.4).

Covers phase-1 skeleton branches AND phase-2 LLM-mode dispatch with
mocked providers (set_llm_provider so CI stays deterministic).
"""

from __future__ import annotations

import unittest

import generators
from generators import llm as gen_llm


class TestAnalyzeRegistration(unittest.TestCase):
    def test_descriptor(self) -> None:
        d = generators.get_generator("analyze").descriptor
        self.assertEqual(d.lifecycle, "incubating")
        self.assertEqual(d.source_aokp_module, "src/runtime/eval/ragas/")


class TestAnalyzeBranches(unittest.TestCase):
    def _run(self, **payload):
        return generators.get_generator("analyze").handler(
            generators.GeneratorRequest(request_id="t-an", payload=payload, consumer="internal"),
        )

    def test_empty_query_fails(self) -> None:
        r = self._run(query="")
        self.assertEqual(r.status, "failed")

    def test_unknown_metric_fails(self) -> None:
        r = self._run(query="run-1", metrics=["bogus_metric"])
        self.assertEqual(r.status, "failed")
        self.assertTrue(any("unknown metrics" in d for d in r.diagnostics))

    def test_empty_pairs_returns_skipped(self) -> None:
        r = self._run(query="run-empty", pairs=[])
        self.assertEqual(r.status, "success")
        self.assertIn("RAGAS run skipped", r.answer)

    def test_pairs_compute_means_for_default_metrics(self) -> None:
        r = self._run(
            query="eval-batch-1",
            pairs=[
                {"question": "q1", "answer": "alpha", "contexts": ["alpha beta gamma"]},
                {"question": "q2", "answer": "delta", "contexts": ["epsilon zeta"]},
            ],
        )
        self.assertEqual(r.status, "partial")
        self.assertIn("RAGAS Eval", r.answer)
        # Heuristic: pair 1 has lexical overlap (1.0), pair 2 doesn't (0.5) → mean 0.75 across all metrics
        means = r.usage["metric_means"]
        for metric, score in means.items():
            self.assertAlmostEqual(score, 0.75, places=4)
        self.assertEqual(r.usage["pairs_evaluated"], 2)

    def test_metric_subset_respected(self) -> None:
        r = self._run(
            query="subset-test",
            pairs=[{"question": "q", "answer": "x", "contexts": ["x"]}],
            metrics=["faithfulness"],
        )
        self.assertEqual(set(r.usage["metric_means"].keys()), {"faithfulness"})


class TestTransformBranches(unittest.TestCase):
    def _run(self, **payload):
        return generators.get_generator("transform").handler(
            generators.GeneratorRequest(request_id="t-tf", payload=payload, consumer="internal"),
        )

    def test_empty_query_fails(self) -> None:
        r = self._run(query="")
        self.assertEqual(r.status, "failed")

    def test_invalid_mode_fails(self) -> None:
        r = self._run(query="hello", mode="warp")
        self.assertEqual(r.status, "failed")
        self.assertTrue(any("invalid" in d for d in r.diagnostics))

    def test_passthrough_keeps_query(self) -> None:
        r = self._run(query="What is HCMOPS?", mode="passthrough")
        self.assertEqual(r.status, "partial")
        self.assertEqual(r.usage["transformed_count"], 1)
        self.assertEqual(r.usage["intent"], "simple")
        self.assertIn("What is HCMOPS?", r.answer)

    def test_decompose_splits_compound_query(self) -> None:
        r = self._run(query="What is HCMOPS and where is the gateway?", mode="decompose")
        self.assertGreaterEqual(r.usage["transformed_count"], 2)
        self.assertEqual(r.usage["intent"], "multi-hop")

    def test_decompose_single_question_stays_simple(self) -> None:
        r = self._run(query="What is HCMOPS?", mode="decompose")
        self.assertEqual(r.usage["transformed_count"], 1)
        self.assertEqual(r.usage["intent"], "simple")

    def test_hyde_emits_hypothesis(self) -> None:
        r = self._run(query="What is HCMOPS?", mode="hyde")
        self.assertEqual(r.usage["transformed_count"], 2)
        self.assertEqual(r.usage["intent"], "ambiguous")
        self.assertTrue(any("hypothetical answer passage" in line for line in r.answer.splitlines()))


class TestAnalyzeLlmMode(unittest.TestCase):
    """Phase 2: real LLM judges with mock provider."""

    def setUp(self) -> None:
        self.captured: list[str] = []

        def fake_provider(prompt: str, model: str | None = None) -> str:
            self.captured.append(prompt)
            # Return a parseable score that varies by metric so we can verify
            # the metric-specific prompt is being used.
            if "faithfulness judge" in prompt:
                return "Score: 0.85"
            if "answer-relevancy judge" in prompt:
                return "Score: 0.7"
            if "context-precision judge" in prompt:
                return "Score: 0.9"
            if "context-recall judge" in prompt:
                return "Score: 0.6"
            return "Score: 0.5"

        gen_llm.set_llm_provider(fake_provider)

    def tearDown(self) -> None:
        gen_llm.reset_llm_provider()

    def _run_real(self, **extra):
        return generators.get_generator("analyze").handler(
            generators.GeneratorRequest(
                request_id="t-llm",
                payload={
                    "query": "eval-llm-1",
                    "llm_mode": "real",
                    "pairs": [
                        {"question": "What is X?", "answer": "X is foo.", "contexts": ["X is bar."]},
                    ],
                    **extra,
                },
                consumer="internal",
            ),
        )

    def test_real_mode_status_success(self) -> None:
        r = self._run_real()
        self.assertEqual(r.status, "success")

    def test_real_mode_invokes_provider_per_metric(self) -> None:
        self._run_real()
        # 4 metrics x 1 pair = 4 calls
        self.assertEqual(len(self.captured), 4)

    def test_real_mode_produces_metric_specific_means(self) -> None:
        r = self._run_real()
        means = r.usage["metric_means"]
        self.assertAlmostEqual(means["faithfulness"], 0.85)
        self.assertAlmostEqual(means["answer_relevancy"], 0.7)
        self.assertAlmostEqual(means["context_precision"], 0.9)
        self.assertAlmostEqual(means["context_recall"], 0.6)

    def test_real_mode_subset_metric_only_calls_relevant_judges(self) -> None:
        self._run_real(metrics=["faithfulness"])
        self.assertEqual(len(self.captured), 1)
        self.assertIn("faithfulness judge", self.captured[0])

    def test_unparseable_response_falls_back_to_heuristic(self) -> None:
        gen_llm.set_llm_provider(lambda p, m=None: "I cannot answer that.")
        r = self._run_real()
        # Heuristic for the test pair (answer 'X is foo.' vs context 'X is bar.')
        # = 0.5 (lexical no-match). Real LLM result would be 0.85; if we got 0.5
        # then fallback fired.
        self.assertAlmostEqual(r.usage["metric_means"]["faithfulness"], 0.5)
        self.assertTrue(any("heuristic_fallback_unparseable" in str(d) for d in r.diagnostics))

    def test_provider_error_falls_back_to_heuristic(self) -> None:
        def err(p, m=None):
            raise gen_llm.LlmError("upstream timeout")
        gen_llm.set_llm_provider(err)
        r = self._run_real()
        self.assertTrue(any("heuristic_fallback_llm_error" in str(d) for d in r.diagnostics))


class TestTransformLlmMode(unittest.TestCase):
    """Phase 2: real LLM CRAG/HyDE with mock provider."""

    def setUp(self) -> None:
        self.captured: list[str] = []

        def fake_provider(prompt: str, model: str | None = None) -> str:
            self.captured.append(prompt)
            if "query decomposer" in prompt:
                return "What is HCMOPS?\nWhere is the gateway?\nWho operates it?"
            if "HyDE retriever" in prompt:
                return "HCMOPS is the operational namespace at HCM City FIR. The gateway runs at the AFTN endpoint."
            return ""

        gen_llm.set_llm_provider(fake_provider)

    def tearDown(self) -> None:
        gen_llm.reset_llm_provider()

    def test_decompose_real_mode_produces_3_subqueries(self) -> None:
        r = generators.get_generator("transform").handler(
            generators.GeneratorRequest(
                request_id="t-decomp",
                payload={"query": "Tell me everything", "mode": "decompose", "llm_mode": "real"},
                consumer="internal",
            ),
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.usage["transformed_count"], 3)
        self.assertEqual(r.usage["intent"], "multi-hop")

    def test_hyde_real_mode_produces_passage(self) -> None:
        r = generators.get_generator("transform").handler(
            generators.GeneratorRequest(
                request_id="t-hyde",
                payload={"query": "What is HCMOPS?", "mode": "hyde", "llm_mode": "real"},
                consumer="internal",
            ),
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.usage["transformed_count"], 2)  # original + LLM passage
        self.assertTrue(any("operational namespace" in line for line in r.answer.splitlines()))

    def test_passthrough_skips_llm_even_in_real_mode(self) -> None:
        r = generators.get_generator("transform").handler(
            generators.GeneratorRequest(
                request_id="t-pt-real",
                payload={"query": "x", "mode": "passthrough", "llm_mode": "real"},
                consumer="internal",
            ),
        )
        self.assertEqual(self.captured, [])  # no LLM call for passthrough

    def test_decompose_llm_error_falls_back(self) -> None:
        def err(p, m=None):
            raise gen_llm.LlmError("upstream gone")
        gen_llm.set_llm_provider(err)
        r = generators.get_generator("transform").handler(
            generators.GeneratorRequest(
                request_id="t-decomp-err",
                payload={"query": "What is X and Y?", "mode": "decompose", "llm_mode": "real"},
                consumer="internal",
            ),
        )
        self.assertGreaterEqual(r.usage["transformed_count"], 2)  # heuristic split worked
        self.assertTrue(any("heuristic_fallback_llm_error" in d for d in r.diagnostics))


if __name__ == "__main__":
    unittest.main()
