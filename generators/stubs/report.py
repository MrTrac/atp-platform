"""ATP generator: report — Doctrine v6.0 Step 4 W17-W18 (D5.2).

Ports the report-shape branch of AOKP `src/runtime/synthesis/synthesizer.ts`
(`synthesizeAnswer`) into ATP. This is the FIRST must-ship port of three
(D5.2 = report, D5.3 = analyze, D5.4 = transform).

Phase 1 + 2 status:
  ✅ no-context fallback branch (synthesizer.ts:43-60) — full parity
  ✅ context-concat skeleton when chunks supplied — placeholder synthesis
     so the dispatch path + citation surface works end-to-end without
     requiring Ollama/cloud-LLM availability in CI
  ✅ real LLM-driven synthesis (synthesizer.ts:62+) — wired via
     generators.llm.call_llm(), which by default delegates to ATP
     `bridge_request`. Caller opts in via `params.llm_mode = "real"`;
     default stays `"skeleton"` so test environments don't accidentally
     hit a live model.
  ⏸ quality-check loop + grounding verifier (AOKP retry-on-fail logic)
     — deferred to v6.1

The descriptor stays `lifecycle="incubating"` until the quality loop ships.
"""

from __future__ import annotations

from typing import Any

from generators.llm import LlmError, call_llm
from generators.registry import (
    Citation,
    GeneratorRequest,
    SynthesisResult,
    register_generator,
)


def _new_run_id(req: GeneratorRequest) -> str:
    # Deterministic when request_id provided; falls back to hash of payload.
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_report_{suffix}"


def _no_context_answer(locale: str) -> str:
    # Mirrors synthesizer.ts:44-46 verbatim (with locale gating).
    if locale == "vi":
        return (
            "Không tìm thấy thông tin liên quan trong cơ sở tri thức. "
            "Vui lòng thử lại với câu hỏi khác hoặc cung cấp thêm chi tiết."
        )
    return (
        "No relevant information found in the knowledge base. "
        "Please try a different question or provide more details."
    )


def _placeholder_synthesis(query: str, chunks: list[dict[str, Any]]) -> str:
    """Skeletal synthesis without LLM — concatenates chunk titles + snippets
    under section headings. Used when `params.llm_mode != "real"` (default).
    The LLM branch is opt-in to keep CI deterministic without an external
    service running."""
    lines = [f"# Report — {query}", ""]
    for i, chunk in enumerate(chunks, 1):
        title = str(chunk.get("title", f"Source {i}"))
        snippet = str(chunk.get("snippet", "")).strip()
        if snippet:
            lines.append(f"## [{i}] {title}")
            lines.append(snippet)
            lines.append("")
    lines.append("_Skeleton mode — pass `params.llm_mode='real'` for LLM synthesis._")
    return "\n".join(lines)


def _format_context(chunks: list[dict[str, Any]]) -> str:
    """Build the context block exactly the way AOKP synthesizer expects:
    each chunk numbered [n] with title + snippet. Mirrors
    `formatContextWithCitations` in AOKP `synthesis/citation-linker.ts`."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        title = str(chunk.get("title", f"Source {i}"))
        snippet = str(chunk.get("snippet", "")).strip()
        parts.append(f"[{i}] {title}\n{snippet}")
    return "\n\n".join(parts)


def _build_prompt(query: str, chunks: list[dict[str, Any]], locale: str) -> str:
    """Mirrors AOKP SYNTHESIS_SYSTEM_PROMPT shape (synthesizer.ts:74). The
    real prompt template lives in AOKP `synthesis/types.ts`; we paraphrase
    here. Phase 2 work to fully match the AOKP template (incl. retry hint
    + structured-section instructions) tracks under v6.1."""
    lang = "Vietnamese" if locale == "vi" else "English"
    return (
        f"You are a synthesis engine. Answer the user's question in {lang} "
        f"based ONLY on the numbered context items below. Cite sources "
        f"inline as [1], [2], etc. matching the item numbers.\n\n"
        f"CONTEXT:\n{_format_context(chunks)}\n\n"
        f"QUESTION: {query}\n\n"
        f"ANSWER:"
    )


def _llm_synthesis(query: str, chunks: list[dict[str, Any]], locale: str, model: str | None) -> str:
    """Real LLM call via the configured provider. Raises LlmError on
    upstream failure — caller decides whether to fall back to skeleton
    or surface the error."""
    prompt = _build_prompt(query, chunks, locale)
    return call_llm(prompt, model)


@register_generator(
    name="report",
    version="0.3.0",
    lifecycle="incubating",
    description="Report-shape answer synthesis (must-ship D5.2). Ports AOKP src/runtime/synthesis/synthesizer.ts.",
    source_aokp_module="src/runtime/synthesis/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "locale": {"type": "string", "enum": ["vi", "en"], "default": "vi"},
            "llm_mode": {
                "type": "string",
                "enum": ["skeleton", "real"],
                "default": "skeleton",
                "description": "skeleton = no LLM (deterministic); real = call LLM via bridge_request",
            },
            "model": {
                "type": "string",
                "description": "Provider-prefixed model id (e.g. 'ollama/qwen3:8b'). Used when llm_mode='real'.",
            },
            "context_chunks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string"},
                        "source_id": {"type": "string"},
                        "title": {"type": "string"},
                        "snippet": {"type": "string"},
                        "classification_path": {"type": "array", "items": {"type": "string"}},
                        "relevance_score": {"type": "number"},
                    },
                    "required": ["artifact_id", "source_id", "snippet"],
                },
            },
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    payload = req.payload or {}
    query = str(payload.get("query", "")).strip()
    locale = str(payload.get("locale", "vi"))
    if locale not in {"vi", "en"}:
        locale = "vi"
    chunks = payload.get("context_chunks") or []

    run_id = _new_run_id(req)

    if not query:
        return SynthesisResult(
            run_id=run_id,
            generator="report",
            status="failed",
            answer="",
            citations=[],
            diagnostics=["query is required"],
        )

    # Branch 1: no-context fallback (full AOKP parity).
    if not chunks:
        return SynthesisResult(
            run_id=run_id,
            generator="report",
            status="success",
            answer=_no_context_answer(locale),
            citations=[],
            usage={"input_tokens": 0, "output_tokens": 0, "knowledge_queries": 0, "duration_ms": 0},
            diagnostics=["no context chunks supplied — returned no-info fallback"],
        )

    # Branch 2: synthesis with chunks — skeleton (default) or real LLM.
    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model")  # may be None

    diagnostics: list[str] = [f"chunk_count={len(chunks)}"]
    status = "partial"
    if llm_mode == "real":
        try:
            answer = _llm_synthesis(query, chunks, locale, model if isinstance(model, str) else None)
            status = "success"  # real LLM produced an answer; not "partial" anymore
            diagnostics.append(f"llm_mode=real model={model or 'default'}")
        except LlmError as e:
            answer = _placeholder_synthesis(query, chunks)
            diagnostics.append(f"llm_error={e}; fell back to skeleton")
    else:
        answer = _placeholder_synthesis(query, chunks)
        diagnostics.append("llm_mode=skeleton (default — deterministic)")

    citations = [
        Citation(
            artifact_id=str(c.get("artifact_id", "")),
            source_id=str(c.get("source_id", "")),
            snippet=str(c.get("snippet", ""))[:4096],
            classification_path=tuple(c.get("classification_path") or ()),
            relevance_score=float(c.get("relevance_score", 0.0)),
            rank=i,
        )
        for i, c in enumerate(chunks, 1)
    ]

    return SynthesisResult(
        run_id=run_id,
        generator="report",
        status=status,
        answer=answer,
        citations=citations,
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
        },
        diagnostics=diagnostics,
    )
