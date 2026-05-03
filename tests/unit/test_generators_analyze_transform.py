"""Unit tests for ATP generators: analyze (D5.3) + transform (D5.4)."""

from __future__ import annotations

import unittest

import generators


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


if __name__ == "__main__":
    unittest.main()
