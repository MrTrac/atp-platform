"""Golden-vector parity: the Python port of AOKP's synthesis code must give, case by case, the answer the real TypeScript gave (KD-ATP-006, Phase 2a/2b).

`tests/fixtures/synthesis_v2/golden.json.gz` was produced by `run_golden.sh`, which runs AOKP's own `src/runtime/synthesis/*.ts` (with the LLM replaced by a scripted stand-in) on
the inputs of `make_inputs.py`: hand-picked cases for the places where JavaScript and Python disagree, plus a seeded fuzz. This test needs NO AOKP checkout (CI has none).

What a failure means: either the port drifted from AOKP, or AOKP changed and the fixture must be regenerated (`AOKP_DIR=... tests/fixtures/synthesis_v2/run_golden.sh`, then
`gen_python_data.py`) — never "fix" the expectation by hand.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from generators.prompts import synthesis_bank as bank
from generators.synthesis_v2 import _data
from generators.synthesis_v2.citation_grounding import verify_citation_grounding
from generators.synthesis_v2.citation_linker import extract_used_citations, format_context_with_citations
from generators.synthesis_v2.parser import parse_structured_response
from generators.synthesis_v2.quality_guard import check_answer_quality
from generators.synthesis_v2.suggestion_engine import generate_suggestions
from generators.synthesis_v2.synthesizer import synthesize_answer

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthesis_v2" / "golden.json.gz"
GOLDEN: dict[str, Any] = json.load(gzip.open(_FIXTURE, "rt", encoding="utf-8"))


class Scripted:
    """The Python twin of `llm_chat_stub.ts`: answers from a script, records every call."""

    def __init__(self, script: list[dict[str, str]]) -> None:
        self.script = list(script)
        self.calls: list[list[dict[str, str]]] = []

    def __call__(self, messages: list[dict[str, str]]) -> str:
        self.calls.append([{"role": m["role"], "content": m["content"]} for m in messages])
        if not self.script:
            raise RuntimeError("scripted LLM exhausted")
        step = self.script.pop(0)
        if "throw" in step:
            raise RuntimeError(step["throw"])
        return step["text"]


def _first_diffs(bad: list[tuple[str, Any, Any]], limit: int = 4) -> str:
    return "\n".join(f"  {name}:\n    port : {json.dumps(got, ensure_ascii=False)[:400]}\n    AOKP : {json.dumps(want, ensure_ascii=False)[:400]}" for name, got, want in bad[:limit])


def _check(section: str, compute) -> None:
    bad = []
    for case in GOLDEN[section]:
        assert "ok" in case["out"], f"{section}/{case.get('name')}: AOKP itself threw: {case['out']}"
        got = compute(case)
        if got != case["out"]["ok"]:
            bad.append((case.get("name", ""), got, case["out"]["ok"]))
    assert not bad, f"{len(bad)}/{len(GOLDEN[section])} {section} cases differ from AOKP:\n{_first_diffs(bad)}"


class TestFixtureIsWhatItClaims(unittest.TestCase):
    def test_it_came_from_real_aokp_and_has_every_section(self) -> None:
        self.assertRegex(GOLDEN["aokp_commit"], r"^[0-9a-f]{40}$")
        for section, minimum in (("grounding", 250), ("format_extract", 50), ("suggestions", 150), ("parse", 300), ("quality", 70), ("scenarios", 30), ("render", 15)):
            self.assertGreaterEqual(len(GOLDEN[section]), minimum, f"golden section {section} shrank")

    def test_aokp_never_threw_on_these_inputs(self) -> None:
        for section in ("grounding", "format_extract", "suggestions", "parse", "quality", "scenarios", "render"):
            self.assertEqual([c.get("name") for c in GOLDEN[section] if "error" in c["out"]], [], section)


class TestPromptsAndConstants(unittest.TestCase):
    def test_prompts_are_byte_identical_to_aokp(self) -> None:
        for name, tpl in GOLDEN["prompts"].items():
            for loc in ("vi", "en"):
                text = getattr(bank, name)[loc]
                self.assertEqual(text, tpl[loc], f"{name}/{loc} differs from AOKP's text")
                self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), GOLDEN["prompt_sha256"][name][loc])

    def test_constants_are_the_ones_read_out_of_the_typescript(self) -> None:
        c = GOLDEN["constants"]
        self.assertEqual(_data.TOPIC_SUGGESTIONS, c["topic_suggestions"])
        self.assertEqual(_data.GENERIC_SUGGESTIONS, c["generic_suggestions"])
        self.assertEqual(set(_data.STOPWORDS), set(c["stopwords"]))
        self.assertEqual([{"topic": t, "source": s, "flags": f} for t, s, f in _data.TOPIC_PATTERN_SOURCES], c["topic_patterns"])
        self.assertEqual({"grounded": _data.GROUNDED_AT, "weak": _data.WEAK_AT}, c["thresholds"])


class TestPureFunctionsMatchAokp(unittest.TestCase):
    def test_render_prompt(self) -> None:
        _check("render", lambda c: bank.render_prompt(getattr(bank, c["template"]), c["locale"], c["vars"]))

    def test_citation_linker(self) -> None:
        def compute(c):
            text, cmap = format_context_with_citations(c["chunks"])
            return {"formattedContext": text, "citationMap": [[i, v] for i, v in cmap.items()], "used": extract_used_citations(c["answer"], cmap)}
        _check("format_extract", compute)

    def test_citation_grounding(self) -> None:
        def compute(c):
            if c["mode"] == "explicit":
                return {"report": verify_citation_grounding(c["answer"], c["citations"], c["chunks"])}
            _, cmap = format_context_with_citations(c["chunks"])
            used = extract_used_citations(c["answer"], cmap)
            return {"used": used, "report": verify_citation_grounding(c["answer"], used, c["chunks"])}
        _check("grounding", compute)

    def test_suggestion_engine(self) -> None:
        _check("suggestions", lambda c: generate_suggestions(c["query"], c["chunks"]))

    def test_structured_response_parser(self) -> None:
        _check("parse", lambda c: parse_structured_response(c["raw"], c["locale"]))

    def test_quality_guard(self) -> None:
        bad = []
        for c in GOLDEN["quality"]:
            chat = Scripted([{"text": c["raw"]}])
            got = check_answer_quality(c["query"], c["answer"], c["locale"], {"maxRetries": 1, "qualityCheckEnabled": True}, chat)
            if got != c["out"]["ok"] or chat.calls != c["calls"]:
                bad.append((c["name"], {"result": got, "calls": chat.calls}, {"result": c["out"]["ok"], "calls": c["calls"]}))
        self.assertEqual(bad, [], f"{len(bad)} quality cases differ:\n{_first_diffs(bad)}")


class TestEndToEndScenariosMatchAokp(unittest.TestCase):
    """The whole `synthesizeAnswer` loop against a scripted model: same prompts sent in the same order, same retries, same result."""

    def test_every_scenario(self) -> None:
        bad = []
        for c in GOLDEN["scenarios"]:
            chat = Scripted(c["script"])
            got = synthesize_answer(c["request"], chat, c["config"]) if c["config"] else synthesize_answer(c["request"], chat)
            if got != c["out"]["ok"] or chat.calls != c["calls"]:
                bad.append((c["name"], {"result": got, "calls": chat.calls}, {"result": c["out"]["ok"], "calls": c["calls"]}))
        self.assertEqual(bad, [], f"{len(bad)}/{len(GOLDEN['scenarios'])} scenarios differ:\n{_first_diffs(bad)}")

    def test_scenarios_cover_the_branches_that_matter(self) -> None:
        results = [c["out"]["ok"] for c in GOLDEN["scenarios"]]
        self.assertTrue(any(r["synthesisRetries"] == 1 for r in results), "no scenario exercises one retry")
        self.assertTrue(any(r["synthesisRetries"] >= 2 for r in results), "no scenario exhausts retries")
        self.assertTrue(any(r["totalLlmCalls"] == 0 for r in results), "no scenario without LLM calls (no context)")
        self.assertTrue(any(r["qualityScore"] is None and r["totalLlmCalls"] > 0 for r in results), "no scenario with a missing quality score")
        self.assertTrue(any(r["kbGap"] for r in results), "no scenario with a KB gap")
        self.assertTrue({"grounded", "weak", "unsupported"} <= {r["grounding"]["overall"] for r in results}, "grounding verdicts not all exercised")


if __name__ == "__main__":
    unittest.main()
