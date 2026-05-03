"""Unit tests for ATP generators: federation + temporal (D5.5 stretch).

Covers phase-1 skeleton branches AND phase-2 LLM-mode dispatch with
mocked providers (set_llm_provider so CI stays deterministic).
"""

from __future__ import annotations

import unittest

import generators
from generators import llm as gen_llm


# ─── Federation ──────────────────────────────────────────────────────────


class TestFederationRegistration(unittest.TestCase):
    def test_descriptor(self) -> None:
        d = generators.get_generator("federation").descriptor
        self.assertEqual(d.name, "federation")
        self.assertEqual(d.lifecycle, "incubating")
        self.assertEqual(d.version, "0.3.0")
        self.assertEqual(d.source_aokp_module, "src/runtime/federation/coordinator.ts")


class TestFederationBranches(unittest.TestCase):
    def _run(self, **payload):
        return generators.get_generator("federation").handler(
            generators.GeneratorRequest(
                request_id="t-fed", payload=payload, consumer="internal"
            ),
        )

    def test_empty_query_fails(self) -> None:
        r = self._run(query="")
        self.assertEqual(r.status, "failed")
        self.assertEqual(r.answer, "")

    def test_unknown_strategy_fails(self) -> None:
        r = self._run(query="q", merge_strategy="bogus")
        self.assertEqual(r.status, "failed")
        self.assertTrue(any("unknown merge_strategy" in d for d in r.diagnostics))

    def test_empty_node_answers_returns_skipped(self) -> None:
        r = self._run(query="q", node_answers=[])
        self.assertEqual(r.status, "success")
        self.assertIn("merge skipped", r.answer)
        self.assertEqual(r.usage["nodes_queried"], 0)

    def test_rank_fusion_skeleton_two_nodes(self) -> None:
        r = self._run(
            query="who builds what",
            node_answers=[
                {"node_id": "a", "node_name": "NodeA", "answer": "Alice builds rockets"},
                {"node_id": "b", "node_name": "NodeB", "answer": "Bob builds drones"},
            ],
        )
        self.assertEqual(r.status, "partial")
        self.assertIn("[NodeA]: Alice builds rockets", r.answer)
        self.assertIn("[NodeB]: Bob builds drones", r.answer)
        self.assertIn("answer_source=rank_fusion", r.diagnostics)

    def test_rank_fusion_single_node_passthrough(self) -> None:
        r = self._run(
            query="q",
            node_answers=[{"node_name": "NodeA", "answer": "lone answer"}],
        )
        self.assertEqual(r.answer, "lone answer")

    def test_rank_fusion_filters_error_nodes(self) -> None:
        r = self._run(
            query="q",
            node_answers=[
                {"node_name": "NodeA", "status": "error", "answer": ""},
                {"node_name": "NodeB", "answer": "ok answer"},
            ],
        )
        self.assertEqual(r.usage["nodes_queried"], 2)
        self.assertEqual(r.usage["nodes_responded"], 1)
        # Single success short-circuits to that node's answer
        self.assertEqual(r.answer, "ok answer")

    def test_concatenate_strategy_uses_separator(self) -> None:
        r = self._run(
            query="q",
            merge_strategy="concatenate",
            node_answers=[
                {"node_name": "A", "answer": "first"},
                {"node_name": "B", "answer": "second"},
            ],
        )
        self.assertIn("first", r.answer)
        self.assertIn("---", r.answer)
        self.assertIn("second", r.answer)

    def test_evidence_ids_deduplicated(self) -> None:
        r = self._run(
            query="q",
            node_answers=[
                {"node_name": "A", "answer": "ans1", "evidence_ids": ["x", "y"]},
                {"node_name": "B", "answer": "ans2", "evidence_ids": ["y", "z"]},
            ],
        )
        ids = [c.artifact_id for c in r.citations]
        self.assertEqual(sorted(ids), ["x", "y", "z"])

    def test_llm_synthesize_skeleton_degrades_to_rank_fusion(self) -> None:
        # llm_synthesize requested but skeleton mode → no LLM call
        r = self._run(
            query="q",
            merge_strategy="llm_synthesize",
            llm_mode="skeleton",
            node_answers=[
                {"node_name": "A", "answer": "a"},
                {"node_name": "B", "answer": "b"},
            ],
        )
        self.assertIn("rank_fusion_skeleton_degrade", " ".join(r.diagnostics))


class TestFederationLlmMode(unittest.TestCase):
    def setUp(self) -> None:
        self._calls: list[tuple[str, str | None]] = []

    def tearDown(self) -> None:
        gen_llm.reset_llm_provider()

    def _install(self, response: str | None, *, raise_error: bool = False) -> None:
        def fake(prompt: str, model: str | None = None) -> str:
            self._calls.append((prompt, model))
            if raise_error:
                raise gen_llm.LlmError("simulated failure")
            return response or ""

        gen_llm.set_llm_provider(fake)

    def _run(self, **payload):
        return generators.get_generator("federation").handler(
            generators.GeneratorRequest(
                request_id="t-fed-llm", payload=payload, consumer="internal"
            ),
        )

    def test_llm_real_synthesizes_when_strategy_matches(self) -> None:
        self._install("UNIFIED ANSWER from LLM")
        r = self._run(
            query="q",
            merge_strategy="llm_synthesize",
            llm_mode="real",
            node_answers=[
                {"node_name": "A", "answer": "first"},
                {"node_name": "B", "answer": "second"},
            ],
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.answer, "UNIFIED ANSWER from LLM")
        self.assertEqual(len(self._calls), 1)
        self.assertIn("answer_source=llm", r.diagnostics)

    def test_llm_real_falls_back_to_rank_fusion_on_error(self) -> None:
        self._install(None, raise_error=True)
        r = self._run(
            query="q",
            merge_strategy="llm_synthesize",
            llm_mode="real",
            node_answers=[
                {"node_name": "A", "answer": "alpha"},
                {"node_name": "B", "answer": "beta"},
            ],
        )
        self.assertEqual(r.status, "success")
        self.assertIn("[A]: alpha", r.answer)
        self.assertIn("rank_fusion_fallback_llm_error", " ".join(r.diagnostics))

    def test_llm_real_falls_back_on_short_output(self) -> None:
        self._install("hi")  # < 10 chars
        r = self._run(
            query="q",
            merge_strategy="llm_synthesize",
            llm_mode="real",
            node_answers=[
                {"node_name": "A", "answer": "alpha"},
                {"node_name": "B", "answer": "beta"},
            ],
        )
        self.assertIn("rank_fusion_fallback_short_output", " ".join(r.diagnostics))


# ─── Temporal ────────────────────────────────────────────────────────────


class TestTemporalRegistration(unittest.TestCase):
    def test_descriptor(self) -> None:
        d = generators.get_generator("temporal").descriptor
        self.assertEqual(d.name, "temporal")
        self.assertEqual(d.lifecycle, "incubating")
        self.assertEqual(d.version, "0.3.0")
        self.assertEqual(d.source_aokp_module, "src/runtime/graph/temporal/pipeline.ts")


class TestTemporalBranches(unittest.TestCase):
    def _run(self, **payload):
        return generators.get_generator("temporal").handler(
            generators.GeneratorRequest(
                request_id="t-tmp", payload=payload, consumer="internal"
            ),
        )

    def test_empty_query_fails(self) -> None:
        r = self._run(query="")
        self.assertEqual(r.status, "failed")

    def test_empty_context_returns_skipped(self) -> None:
        r = self._run(query="cascade failure")
        self.assertEqual(r.status, "success")
        self.assertIn("Temporal context is empty", r.answer)
        self.assertEqual(r.usage["entities"], 0)

    def test_skeleton_mode_emits_structural_summary(self) -> None:
        r = self._run(
            query="cascade failure cause",
            entities=[
                {
                    "entity_id": "e1",
                    "label": "PowerGrid",
                    "kind": "system",
                    "current_state": "degraded",
                    "timeline": [{"source_artifact_id": "art_x"}],
                },
            ],
            causal_relations=[
                {
                    "cause_entity_id": "e1",
                    "effect_entity_id": "e2",
                    "causal_type": "caused",
                    "evidence_artifact_ids": ["art_y"],
                },
            ],
            causal_chains=[{"description": "Power loss -> radar offline"}],
        )
        self.assertEqual(r.status, "partial")
        self.assertIn("Found 1 entities, 1 causal relations, 1 causal chains", r.answer)
        self.assertIn("PowerGrid", r.answer)
        self.assertIn("Power loss -> radar offline", r.answer)
        self.assertIn("answer_source=skeleton", r.diagnostics)

    def test_evidence_ids_collected_from_timeline_and_relations(self) -> None:
        r = self._run(
            query="q",
            entities=[
                {
                    "entity_id": "e1",
                    "label": "X",
                    "timeline": [
                        {"source_artifact_id": "art_a"},
                        {"source_artifact_id": "art_b"},
                    ],
                },
            ],
            causal_relations=[
                {"cause_entity_id": "e1", "effect_entity_id": "e2",
                 "evidence_artifact_ids": ["art_b", "art_c"]},
            ],
        )
        ids = sorted(c.artifact_id for c in r.citations)
        self.assertEqual(ids, ["art_a", "art_b", "art_c"])


class TestTemporalLlmMode(unittest.TestCase):
    def tearDown(self) -> None:
        gen_llm.reset_llm_provider()

    def _install(self, response: str | None, *, raise_error: bool = False) -> None:
        def fake(prompt: str, model: str | None = None) -> str:
            if raise_error:
                raise gen_llm.LlmError("boom")
            return response or ""

        gen_llm.set_llm_provider(fake)

    def _run(self, **payload):
        return generators.get_generator("temporal").handler(
            generators.GeneratorRequest(
                request_id="t-tmp-llm", payload=payload, consumer="internal"
            ),
        )

    def test_llm_real_returns_synthesized_answer(self) -> None:
        self._install("LLM synthesised causal narrative.")
        r = self._run(
            query="cascade failure",
            llm_mode="real",
            entities=[{"entity_id": "e1", "label": "X", "current_state": "ok"}],
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.answer, "LLM synthesised causal narrative.")
        self.assertIn("answer_source=llm", r.diagnostics)

    def test_llm_real_falls_back_to_skeleton_on_error(self) -> None:
        self._install(None, raise_error=True)
        r = self._run(
            query="cascade",
            llm_mode="real",
            entities=[{"entity_id": "e1", "label": "X"}],
            causal_relations=[
                {"cause_entity_id": "e1", "effect_entity_id": "e2"},
            ],
        )
        self.assertEqual(r.status, "success")
        self.assertIn("Found 1 entities, 1 causal relations", r.answer)
        self.assertIn("skeleton_fallback_llm_error", " ".join(r.diagnostics))

    def test_llm_real_falls_back_on_short_output(self) -> None:
        self._install("ok")  # < 10 chars
        r = self._run(
            query="q",
            llm_mode="real",
            entities=[{"entity_id": "e1", "label": "X"}],
        )
        self.assertIn("skeleton_fallback_short_output", " ".join(r.diagnostics))


if __name__ == "__main__":
    unittest.main()
