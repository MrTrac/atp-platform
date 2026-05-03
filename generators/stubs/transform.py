"""ATP generator: transform — Doctrine v6.0 Step 4 W17-W18 (D5.4).

Ports the CRAG / Self-RAG / HyDE query-transform pipeline from AOKP
`src/runtime/retrieval/` (entry point `runRetrievalQuery` in
`service.ts:151`, plus `crag/query-decomposer.ts` for multi-hop +
`crag/hyde.ts` for hypothesis expansion). Third must-ship port of three
(D5.2 = report, D5.3 = analyze, D5.4 = transform).

Phase 1 + 2 status:
  ✅ Empty-query fail branch + 3-mode dispatch (passthrough/decompose/hyde)
  ✅ Heuristic transformations — `llm_mode=skeleton` (default) keeps CI
     deterministic without external service.
     - decompose: splits on " và " / " and " / "?" boundaries
     - hyde: appends fixed hypothesis suffix
     - passthrough: query verbatim
  ✅ Real LLM transformation — `llm_mode=real` calls call_llm() with
     mode-specific prompt:
     - decompose: LLM splits compound query into sub-queries
     - hyde: LLM writes a hypothetical answer passage
     - passthrough: still bypasses LLM (no-op transform)
     LlmError or unparseable response falls back to heuristic so the
     dispatch never blocks.
  ⏸ CRAG self-grader + reflection loop (`reflectOnRetrieval` in
     AOKP crag/reflection.ts) — deferred to v6.1
"""

from __future__ import annotations

import re
from typing import Any

from generators.llm import LlmError, call_llm
from generators.registry import (
    GeneratorRequest,
    SynthesisResult,
    register_generator,
)

VALID_MODES = ("decompose", "hyde", "passthrough")


def _new_run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_transform_{suffix}"


def _decompose_heuristic(query: str) -> list[str]:
    """Regex multi-hop split — used in skeleton mode and as fallback when
    LLM decompose fails."""
    parts = re.split(r"\s+(?:và|and)\s+|\?\s+", query.strip())
    return [p.strip().rstrip("?") for p in parts if p.strip()]


def _hyde_heuristic(query: str) -> list[str]:
    """Fixed hypothesis-suffix expansion — fallback for HyDE."""
    return [query, f"{query} — hypothetical answer passage"]


_DECOMPOSE_PROMPT = (
    "You are a query decomposer. Split the question into the SMALLEST set of "
    "self-contained sub-questions that together cover the original. Output one "
    "sub-question per line, no numbering, no commentary.\n\n"
    "QUESTION: {query}\n\nSUB-QUESTIONS:"
)

_HYDE_PROMPT = (
    "You are a HyDE retriever. Write ONE hypothetical answer passage (2-4 "
    "sentences) that COULD answer the question. The passage will be used for "
    "vector-similarity retrieval against the corpus, so prefer concrete nouns "
    "and named entities.\n\n"
    "QUESTION: {query}\n\nPASSAGE:"
)


def _decompose_llm(query: str, model: str | None) -> tuple[list[str], str]:
    """Returns (queries, source_label). Source is 'llm' on success,
    'heuristic_fallback_*' otherwise."""
    try:
        raw = call_llm(_DECOMPOSE_PROMPT.format(query=query), model)
    except LlmError:
        return _decompose_heuristic(query), "heuristic_fallback_llm_error"
    parts = [line.strip().lstrip("-•*0123456789. )").strip() for line in raw.splitlines()]
    parts = [p.rstrip("?") for p in parts if p]
    if not parts:
        return _decompose_heuristic(query), "heuristic_fallback_empty"
    return parts, "llm"


def _hyde_llm(query: str, model: str | None) -> tuple[list[str], str]:
    try:
        passage = call_llm(_HYDE_PROMPT.format(query=query), model)
    except LlmError:
        return _hyde_heuristic(query), "heuristic_fallback_llm_error"
    passage = passage.strip()
    if not passage:
        return _hyde_heuristic(query), "heuristic_fallback_empty"
    return [query, passage], "llm"


@register_generator(
    name="transform",
    version="0.3.0",
    lifecycle="incubating",
    description="Query transform pipeline (CRAG/Self-RAG/HyDE, must-ship D5.4). Ports AOKP src/runtime/retrieval/.",
    source_aokp_module="src/runtime/retrieval/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {"type": "string", "enum": list(VALID_MODES), "default": "passthrough"},
            "llm_mode": {"type": "string", "enum": ["skeleton", "real"], "default": "skeleton"},
            "model": {"type": "string"},
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    payload = req.payload or {}
    query = str(payload.get("query", "")).strip()
    mode = str(payload.get("mode", "passthrough"))

    run_id = _new_run_id(req)

    if not query:
        return SynthesisResult(
            run_id=run_id,
            generator="transform",
            status="failed",
            answer="",
            citations=[],
            diagnostics=["query is required"],
        )
    if mode not in VALID_MODES:
        return SynthesisResult(
            run_id=run_id,
            generator="transform",
            status="failed",
            answer="",
            citations=[],
            diagnostics=[f"mode '{mode}' invalid; expected one of {list(VALID_MODES)}"],
        )

    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model") if isinstance(payload.get("model"), str) else None
    source = "heuristic"

    if mode == "decompose":
        if llm_mode == "real":
            transformed, source = _decompose_llm(query, model)
        else:
            transformed = _decompose_heuristic(query)
        intent = "multi-hop" if len(transformed) > 1 else "simple"
    elif mode == "hyde":
        if llm_mode == "real":
            transformed, source = _hyde_llm(query, model)
        else:
            transformed = _hyde_heuristic(query)
        intent = "ambiguous"  # HyDE is the disambiguation tool
    else:  # passthrough
        transformed = [query]
        intent = "simple"
        source = "passthrough"

    mode_label = f"{mode} (LLM)" if llm_mode == "real" and mode != "passthrough" else mode
    answer = "\n".join(
        [
            f"# Query Transform — mode={mode_label}",
            "",
            f"Input: `{query}`",
            f"Detected intent: **{intent}**",
            "",
            "## Transformed queries",
            *[f"- {q}" for q in transformed],
            "",
        ]
        + (["_Skeleton mode — pass `params.llm_mode='real'` for LLM-driven transform._"]
           if llm_mode == "skeleton" else [])
    )

    return SynthesisResult(
        run_id=run_id,
        generator="transform",
        status="success" if llm_mode == "real" else "partial",
        answer=answer,
        citations=[],
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
            "transformed_count": len(transformed),
            "intent": intent,
        },
        diagnostics=[
            f"mode={mode}",
            f"llm_mode={llm_mode}",
            f"source={source}",
            f"transformed_count={len(transformed)}",
        ],
    )
