"""Guard: the `report_v2` generator (Python port of AOKP's synthesis) as ATP exposes it — registration, the two modes, the result shape, the HTTP surface (KD-ATP-006, Phase 2a/2b).

The logic itself is pinned to AOKP by golden vectors (test_synthesis_v2_golden.py); here the point is the glue: ATP chunks in, ATP result out, the model called through `call_llm` with a
separate system prompt, a failing model reported as `partial` and never as an exception, and nothing reaching a real model.
"""

from __future__ import annotations

import json
import unittest

import generators
from bridge.bridge_server import _handle_synthesis_generate, _synthesis_result_to_dict
from generators import llm
from generators.types import GeneratorRequest

CHUNKS = [
    {"artifact_id": "a1", "source_id": "doc1#p3", "title": "Radar chính", "snippet": "Radar chính mất kết nối thì hệ thống chuyển sang radar dự phòng trong vòng 5 giây. " * 4,
     "classification_path": ["atm", "radar"], "relevance_score": 0.9},
    {"artifact_id": "a2", "source_id": "doc2", "snippet": "Ghi nhật ký mọi lần chuyển đổi radar, kèm thời điểm và người xác nhận. " * 4},
]
GOOD = json.dumps({"sections": [{"heading": "Tóm tắt", "content": "Radar dự phòng tiếp quản trong 5 giây [1]."}, {"heading": "Chi tiết", "content": "Ghi nhật ký [2]."}],
                   "suggestions": [{"question": "Radar dự phòng kết nối thế nào?", "rationale": "luồng dữ liệu"}], "external_ref_used": False, "kb_gap": None}, ensure_ascii=False)
PASS = '{"naturalness": 0.9, "relevance": 0.9, "completeness": 0.8, "raw_extraction": false, "vn_clarity": true, "verdict": "pass"}'


def _run(params: dict, request_id: str = "req-0001-abcdef") -> generators.SynthesisResult:
    return generators.get_generator("report_v2").handler(GeneratorRequest(request_id=request_id, payload=params))


class _Scripted:
    """A provider that records (prompt, model, system) and answers from a script."""

    def __init__(self, script: list[str | Exception]) -> None:
        self.script = list(script)
        self.calls: list[tuple[str, str | None, str | None]] = []

    def __call__(self, prompt: str, model: str | None = None, system: str | None = None) -> str:
        self.calls.append((prompt, model, system))
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class _ProviderCase(unittest.TestCase):
    def tearDown(self) -> None:
        llm.reset_llm_provider()


class TestRegistration(unittest.TestCase):
    def test_registered_as_incubating_and_v1_is_untouched(self) -> None:
        d = generators.get_generator("report_v2").descriptor
        self.assertEqual((d.name, d.lifecycle, d.source_aokp_module), ("report_v2", "incubating", "src/runtime/synthesis/"))
        self.assertEqual(generators.get_generator("report").descriptor.version, "0.3.0")
        self.assertIn("query", d.params_schema["required"])
        self.assertEqual(d.params_schema["properties"]["llm_mode"]["default"], "skeleton")


class TestSkeletonMode(unittest.TestCase):
    def test_default_mode_never_calls_a_model_and_is_deterministic(self) -> None:
        llm.set_llm_provider(lambda *a, **k: (_ for _ in ()).throw(AssertionError("a model was called in skeleton mode")))
        try:
            r1, r2 = _run({"query": "Radar chính mất kết nối thì sao?", "context_chunks": CHUNKS}), _run({"query": "Radar chính mất kết nối thì sao?", "context_chunks": CHUNKS})
        finally:
            llm.reset_llm_provider()
        self.assertEqual(r1.status, "partial")
        self.assertEqual((r1.answer, r1.structured, [c.rank for c in r1.citations]), (r2.answer, r2.structured, [c.rank for c in r2.citations]))
        self.assertIn("llm_mode=skeleton", " ".join(r1.diagnostics))
        self.assertEqual(r1.structured["total_llm_calls"], 0)
        self.assertGreaterEqual(len(r1.structured["suggestions"]), 2, "domain suggestions top up the empty list")

    def test_no_context_is_aokps_no_info_answer_with_a_kb_gap(self) -> None:
        r = _run({"query": "Câu hỏi bất kỳ?", "context_chunks": []})
        self.assertEqual(r.status, "success")
        self.assertTrue(r.answer.startswith("Không tìm thấy thông tin liên quan"))
        self.assertEqual(r.citations, [])
        self.assertIn("KB không có tài liệu", r.structured["kb_gap"])
        en = _run({"query": "Anything?", "locale": "en"})
        self.assertTrue(en.answer.startswith("No relevant information found"))

    def test_invalid_input_is_a_failed_result_not_an_exception(self) -> None:
        self.assertEqual(_run({"query": "   "}).status, "failed")
        self.assertEqual(_run({}).status, "failed")
        self.assertEqual(_run({"query": "x", "context_chunks": "nope"}).status, "failed")
        self.assertEqual(_run({"query": "x", "locale": "fr", "context_chunks": []}).structured["locale"], "vi")


class TestRealMode(_ProviderCase):
    def test_model_is_called_with_a_separate_system_prompt_and_the_result_is_structured(self) -> None:
        p = _Scripted([GOOD, PASS])
        llm.set_llm_provider(p)
        r = _run({"query": "Radar chính mất kết nối thì sao?", "context_chunks": CHUNKS, "llm_mode": "real", "model": "anthropic/claude-haiku-4-5-20251001"})
        self.assertEqual(r.status, "success")
        self.assertEqual(len(p.calls), 2, "one synthesis call + one quality call")
        prompt, model, system = p.calls[0]
        self.assertEqual(model, "anthropic/claude-haiku-4-5-20251001")
        self.assertIn("QUY TẮC NGÔN NGỮ", system)       # AOKP's Vietnamese system prompt, verbatim, NOT mixed into the user text
        self.assertNotIn("QUY TẮC NGÔN NGỮ", prompt)
        self.assertIn("[1] Radar chính", prompt)         # numbered context
        self.assertIn("NGUỒN NỘI BỘ", prompt)
        q_prompt, _, q_system = p.calls[1]
        self.assertIsNone(q_system)                      # the quality check is a single user message, as in AOKP
        self.assertIn("Đánh giá chất lượng câu trả lời", q_prompt)
        self.assertEqual([s["heading"] for s in r.structured["sections"]], ["Tóm tắt", "Chi tiết"])
        self.assertEqual(r.structured["quality_score"]["verdict"], "pass")
        self.assertEqual(r.structured["total_llm_calls"], 2)
        self.assertEqual([(c.rank, c.artifact_id, c.source_id) for c in r.citations], [(1, "a1", "doc1#p3"), (2, "a2", "doc2")])
        self.assertEqual(r.citations[0].classification_path, ("atm", "radar"))
        self.assertIn(r.structured["grounding"]["overall"], {"grounded", "weak", "unsupported"})

    def test_a_rejected_answer_is_retried_once_with_the_retry_hint(self) -> None:
        retry = '{"naturalness": 0.3, "relevance": 0.9, "completeness": 0.8, "raw_extraction": true, "vn_clarity": true, "verdict": "retry"}'
        p = _Scripted([GOOD, retry, GOOD, PASS])
        llm.set_llm_provider(p)
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual((r.structured["synthesis_retries"], r.structured["total_llm_calls"], r.status), (1, 4, "success"))
        self.assertNotIn("Lần trả lời trước bị từ chối", p.calls[0][0])
        self.assertIn("Lần trả lời trước bị từ chối", p.calls[2][0])

    def test_quality_check_can_be_switched_off_and_retries_capped(self) -> None:
        p = _Scripted([GOOD])
        llm.set_llm_provider(p)
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real", "quality_check": False, "max_retries": 9})
        self.assertEqual((len(p.calls), r.structured["quality_score"]), (1, None))

    def test_a_failing_model_degrades_to_partial_and_never_raises(self) -> None:
        llm.set_llm_provider(_Scripted([llm.LlmError("bridge down")]))
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual(r.status, "partial")
        self.assertTrue(r.answer.startswith("Dựa trên thông tin tìm được:"))
        self.assertIn("llm_error=LlmError: bridge down", " ".join(r.diagnostics))

    def test_a_provider_bug_is_reported_the_same_way(self) -> None:
        llm.set_llm_provider(_Scripted([TypeError("provider bug")]))
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual(r.status, "partial")
        self.assertIn("TypeError", " ".join(r.diagnostics))

    def test_empty_model_output_is_partial(self) -> None:
        llm.set_llm_provider(_Scripted(["<think>hmm</think>\n  "]))
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual(r.status, "partial")
        self.assertIn("empty_model_output", " ".join(r.diagnostics))

    def test_a_quality_check_failure_is_not_a_degradation(self) -> None:
        llm.set_llm_provider(_Scripted([GOOD, llm.LlmError("quality down"), GOOD, llm.LlmError("quality down")]))
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual(r.status, "success")  # AOKP: a quality-check failure must not block the answer
        self.assertIsNone(r.structured["quality_score"])

    def test_a_provider_without_a_system_parameter_still_works(self) -> None:
        seen: list[str] = []

        def old_style(prompt: str, model: str | None = None) -> str:
            seen.append(prompt)
            return GOOD if len(seen) == 1 else PASS

        llm.set_llm_provider(old_style)
        r = _run({"query": "Radar?", "context_chunks": CHUNKS, "llm_mode": "real"})
        self.assertEqual(r.status, "success")
        self.assertTrue(seen[0].startswith("Bạn là chuyên gia hệ thống Quản lý Không lưu"), "system text goes in front of the prompt for a provider that cannot take it separately")


class TestCallLlmSystemParameter(_ProviderCase):
    def test_without_system_the_provider_is_called_exactly_as_before(self) -> None:
        seen: list[tuple] = []
        llm.set_llm_provider(lambda prompt, model=None: seen.append((prompt, model)) or "ok")
        self.assertEqual(llm.call_llm("p", "m"), "ok")
        self.assertEqual(seen, [("p", "m")])

    def test_system_reaches_a_provider_that_declares_it_or_takes_kwargs(self) -> None:
        got: list = []
        llm.set_llm_provider(lambda prompt, model=None, system=None: got.append(("declared", system)) or "ok")
        llm.call_llm("p", None, system="S")
        llm.set_llm_provider(lambda prompt, model=None, **kw: got.append(("kwargs", kw.get("system"))) or "ok")
        llm.call_llm("p", None, system="S")
        self.assertEqual(got, [("declared", "S"), ("kwargs", "S")])

    def test_the_default_provider_sends_system_as_the_requests_context(self) -> None:
        import bridge.openclaw_bridge as ob
        sent: dict = {}
        original = ob.bridge_request
        ob.bridge_request = lambda payload: sent.update(payload) or {"status": "succeeded", "stdout": "text"}
        try:
            self.assertEqual(llm._default_provider("user text", "anthropic/x", system="sys text"), "text")
        finally:
            ob.bridge_request = original
        self.assertEqual((sent["text"], sent["context"], sent["model"]), ("user text", "sys text", "anthropic/x"))
        sent.clear()
        ob.bridge_request = lambda payload: sent.update(payload) or {"status": "succeeded", "stdout": "text"}
        try:
            llm._default_provider("only user")
        finally:
            ob.bridge_request = original
        self.assertNotIn("context", sent)


class TestHttpSurface(_ProviderCase):
    def test_generate_route_returns_the_structured_block_and_leaves_other_generators_alone(self) -> None:
        status, body = _handle_synthesis_generate({"generator": "report_v2", "request_id": "req-0002-abcdef", "params": {"query": "Radar?", "context_chunks": CHUNKS}})
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertRegex(body["run_id"], r"^syn_[A-Za-z0-9_-]{16,}$")  # the Z2 contract pattern
        self.assertEqual(set(body["structured"]), {"locale", "sections", "suggestions", "quality_score", "grounding", "kb_gap", "external_ref_used", "synthesis_retries", "total_llm_calls"})
        json.dumps(body)  # serialisable as is
        status, v1 = _handle_synthesis_generate({"generator": "report", "params": {"query": "Radar?", "context_chunks": CHUNKS}})
        self.assertEqual(status, 200)
        self.assertNotIn("structured", v1, "a generator with no structured payload keeps the response it always had")

    def test_serializer_omits_an_empty_structured_block(self) -> None:
        r = generators.SynthesisResult(run_id="syn_x", generator="report", status="success", answer="hi")
        self.assertNotIn("structured", _synthesis_result_to_dict(r))
        r.structured = {"k": 1}
        self.assertEqual(_synthesis_result_to_dict(r)["structured"], {"k": 1})

    def test_run_id_is_deterministic_without_a_request_id(self) -> None:
        a = _run({"query": "Radar?", "context_chunks": CHUNKS}, request_id="")
        b = _run({"query": "Radar?", "context_chunks": CHUNKS}, request_id="")
        self.assertEqual(a.run_id, b.run_id)
        self.assertRegex(a.run_id, r"^syn_report_v2_[0-9a-f]{16}$")


if __name__ == "__main__":
    unittest.main()
