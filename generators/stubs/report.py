"""ATP generator: report — Doctrine v6.0 Step 4 W17-W18 (D5.2).

Ports the report-shape branch of AOKP `src/runtime/synthesis/synthesizer.ts`
(`synthesizeAnswer`) into ATP. This is the FIRST must-ship port of three
(D5.2 = report, D5.3 = analyze, D5.4 = transform).

Scope of this commit (honest):
  ✅ no-context fallback branch (synthesizer.ts:43-60) — full parity
  ✅ context-concat skeleton when chunks supplied — placeholder synthesis
     so the dispatch path + citation surface works end-to-end without
     requiring Ollama/cloud-LLM availability in CI
  ⏸ real LLM-driven synthesis (synthesizer.ts:62+) — deferred to follow-up
     once R8 mitigation (smoke tests) lands and the bridge HTTP layer
     wires /api/synthesis/* routes (D5.x phase 2)
  ⏸ quality-check loop + grounding verifier — deferred to v6.1

The descriptor stays `lifecycle="incubating"` until the LLM branch ships.
"""

from __future__ import annotations

from typing import Any

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
    under section headings. Replaced by the LLM branch in the W17-W18 phase 2
    follow-up; kept here so the round-trip (request → result → citations)
    can be exercised without external services."""
    lines = [f"# Report — {query}", ""]
    for i, chunk in enumerate(chunks, 1):
        title = str(chunk.get("title", f"Source {i}"))
        snippet = str(chunk.get("snippet", "")).strip()
        if snippet:
            lines.append(f"## [{i}] {title}")
            lines.append(snippet)
            lines.append("")
    lines.append("_Synthesis stub — LLM-driven answer generation pending W17-W18 phase 2._")
    return "\n".join(lines)


@register_generator(
    name="report",
    version="0.2.0",
    lifecycle="incubating",
    description="Report-shape answer synthesis (must-ship D5.2). Ports AOKP src/runtime/synthesis/synthesizer.ts.",
    source_aokp_module="src/runtime/synthesis/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "locale": {"type": "string", "enum": ["vi", "en"], "default": "vi"},
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

    # Branch 2: context-concat skeleton (placeholder for LLM synthesis).
    answer = _placeholder_synthesis(query, chunks)
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
        status="partial",
        answer=answer,
        citations=citations,
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
        },
        diagnostics=[
            "skeletal synthesis — LLM branch pending W17-W18 phase 2",
            f"chunk_count={len(chunks)}",
        ],
    )
