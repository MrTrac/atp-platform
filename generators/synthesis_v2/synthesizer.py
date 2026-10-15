"""Port of AOKP `src/runtime/synthesis/synthesizer.ts` (`synthesizeAnswer`): structured, grounded answers with a quality guard and retry.

Flow (identical to AOKP): number the context -> ask the model for a JSON answer (sections + suggestions + kb_gap) -> quality-check it (retry once by default) -> top up the follow-up
suggestions from the domain engine -> collect the `[n]` actually used -> verify each against its chunk.

The model is injected as `chat(messages) -> str` (roles `system` / `user`), so the logic runs the same against AOKP's golden vectors, against a fake in tests and against ATP's
`call_llm` in `generators/stubs/report_v2.py`. Nothing here talks to the network.
"""

from __future__ import annotations

from typing import Any, Callable

from generators.prompts.synthesis_bank import SYNTHESIS_SYSTEM_PROMPT, SYNTHESIS_USER_PROMPT, render_prompt

from .citation_grounding import verify_citation_grounding
from .citation_linker import extract_used_citations, format_context_with_citations
from .jsrt import js_trim, utf16_len
from .parser import build_fallback, clean_llm_output, parse_structured_response, sections_to_plain_text
from .quality_guard import check_answer_quality
from .suggestion_engine import generate_suggestions

ChatFn = Callable[[list[dict[str, str]]], str]
DEFAULT_SYNTHESIS_CONFIG: dict[str, Any] = {"maxRetries": 1, "qualityCheckEnabled": True}

_NO_INFO = {
    "vi": "Không tìm thấy thông tin liên quan trong cơ sở tri thức. Vui lòng thử lại với câu hỏi khác hoặc cung cấp thêm chi tiết.",
    "en": "No relevant information found in the knowledge base. Please try a different question or provide more details.",
}
_NO_CONTEXT_GAP = {
    "vi": "KB không có tài liệu nào khớp với câu hỏi này. Cần bổ sung tài liệu liên quan.",
    "en": "No matching documents found in KB. Relevant documents need to be added.",
}
_THIN_HINT = {
    "vi": "\n\n⚠️ BỐI CẢNH MỎNG: Tài liệu tìm được nhưng nội dung rất ít (<400 ký tự). Có thể bảng/hình bị mất khi chuyển đổi PDF. Nếu không đủ bằng chứng → nêu rõ kb_gap thay vì bịa đặt.",
    "en": "\n\n⚠️ THIN CONTEXT: Documents found but content is very sparse (<400 chars). Tables/figures may have been lost during PDF conversion. If evidence is insufficient → state the kb_gap explicitly instead of fabricating.",
}
_THIN_GAP = {
    "vi": "Nội dung tài liệu mỏng — có thể bảng bị mất khi OCR PDF.",
    "en": "Document content is thin — tables may have been lost during PDF OCR.",
}
_RETRY_HINT = {
    "vi": "\n\n⚠️ Lần trả lời trước bị từ chối. Hãy diễn đạt lại hoàn toàn bằng lời của bạn, tự nhiên hơn, bám sát nguồn dữ liệu.",
    "en": "\n\n⚠️ Previous answer was rejected. Rephrase entirely in your own words, more natural, grounded in source data.",
}
_NO_HISTORY = {"vi": "(không có)", "en": "(none)"}


def synthesize_answer(request: dict[str, Any], chat: ChatFn, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = DEFAULT_SYNTHESIS_CONFIG if config is None else config
    query = request["query"]
    locale = request["locale"]
    chunks: list[dict[str, Any]] = request["contextChunks"]
    history = request.get("conversationHistory")

    if len(chunks) == 0:
        no_info = _NO_INFO[locale] if locale == "vi" else _NO_INFO["en"]
        return {
            "answer": no_info,
            "sections": [{"heading": "Tóm tắt" if locale == "vi" else "Summary", "content": no_info}],
            "citations": [],
            "suggestions": generate_suggestions(query, chunks),
            "locale": locale,
            "qualityScore": None,
            "synthesisRetries": 0,
            "totalLlmCalls": 0,
            "externalRefUsed": False,
            "grounding": {"overall": "grounded", "averageScore": 0, "perCitation": [], "unsupportedCount": 0},
            "kbGap": _NO_CONTEXT_GAP[locale] if locale == "vi" else _NO_CONTEXT_GAP["en"],
        }

    lang = "vi" if locale == "vi" else "en"
    total_content_chars = sum(utf16_len(c.get("content") or "") for c in chunks)
    thin_hint = _THIN_HINT[lang] if total_content_chars < 400 else ""

    formatted_context, citation_map = format_context_with_citations(chunks)
    total_llm_calls = 0
    synthesis_retries = 0
    sections: list[dict[str, str]] = []
    suggestions: list[dict[str, Any]] = []
    external_ref_used = False
    answer = ""
    quality_score: dict[str, Any] | None = None
    kb_gap: str | None = None

    max_attempts = 1 + config["maxRetries"] if config["qualityCheckEnabled"] else 1

    attempt = 0
    while attempt < max_attempts:
        system_prompt = render_prompt(SYNTHESIS_SYSTEM_PROMPT, locale)
        retry_hint = _RETRY_HINT[lang] if attempt > 0 else ""
        user_prompt = render_prompt(SYNTHESIS_USER_PROMPT, locale, {
            "context": formatted_context,
            "query": query,
            "history": history or _NO_HISTORY[lang],
        }) + retry_hint + thin_hint

        try:
            raw = chat([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
            total_llm_calls += 1

            raw_content = clean_llm_output(js_trim(raw))
            if not raw_content:
                fb = build_fallback(chunks, locale)
                answer, sections, suggestions, external_ref_used = fb["answer"], fb["sections"], fb["suggestions"], fb["externalRefUsed"]
                break

            parsed = parse_structured_response(raw_content, locale)
            sections = parsed["sections"]
            suggestions = parsed["suggestions"]
            external_ref_used = parsed["externalRefUsed"]
            kb_gap = parsed["kbGap"]
            answer = sections_to_plain_text(sections)

            if config["qualityCheckEnabled"] and attempt < max_attempts - 1:
                quality_score = check_answer_quality(query, answer, locale, config, chat)
                total_llm_calls += 1
                if quality_score is not None and quality_score["verdict"] == "pass":
                    break
                synthesis_retries += 1
                attempt += 1
                continue
            if config["qualityCheckEnabled"]:
                quality_score = check_answer_quality(query, answer, locale, config, chat)
                total_llm_calls += 1
            break
        except Exception:  # noqa: BLE001 — AOKP: any failure in an attempt degrades to the chunk-based fallback
            fb = build_fallback(chunks, locale)
            answer, sections, suggestions, external_ref_used = fb["answer"], fb["sections"], fb["suggestions"], fb["externalRefUsed"]
            break

    if len(suggestions) < 2:
        existing = {s["question"] for s in suggestions}
        for ds in generate_suggestions(query, chunks):
            if ds["question"] not in existing and len(suggestions) < 3:
                suggestions.append(ds)

    citations = extract_used_citations(answer, citation_map)
    grounding = verify_citation_grounding(answer, citations, chunks)

    return {
        "answer": answer,
        "sections": sections,
        "citations": citations,
        "suggestions": suggestions,
        "locale": locale,
        "qualityScore": quality_score,
        "synthesisRetries": synthesis_retries,
        "totalLlmCalls": total_llm_calls,
        "externalRefUsed": external_ref_used,
        "grounding": grounding,
        "kbGap": kb_gap if kb_gap is not None else (_THIN_GAP[lang] if thin_hint else None),
    }
