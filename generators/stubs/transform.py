"""ATP generator: transform — Doctrine v6.0 Step 4 W17-W18 (D5.4).

Ports the CRAG / Self-RAG / HyDE query-transform pipeline from AOKP
`src/runtime/retrieval/` (entry point `runRetrievalQuery` in
`service.ts:151`, plus `crag/query-decomposer.ts` for multi-hop +
`crag/hyde.ts` for hypothesis expansion). Third must-ship port of three
(D5.2 = report, D5.3 = analyze, D5.4 = transform).

Phase 1 scope (this commit):
  ✅ Empty-query fail branch
  ✅ Mode dispatch — `decompose` (multi-hop) | `hyde` (hypothesis
     expansion) | `passthrough`. Each emits a list of transformed
     query strings + intent label so the dispatch + downstream
     retrieval surface works without LLM availability.
  ✅ Heuristic transformations (no LLM): decompose splits on " và "
     / " and " / "?" boundaries; hyde appends a fixed hypothesis
     suffix; passthrough returns the query verbatim.
  ⏸ Real LLM-driven transformation (CRAG self-grader + reflection
     loop) — deferred to phase 2

The 3 modes match AOKP's `QueryIntent` enum (simple / multi-hop /
ambiguous) at the dispatch layer.
"""

from __future__ import annotations

import re
from typing import Any

from generators.registry import (
    GeneratorRequest,
    SynthesisResult,
    register_generator,
)

VALID_MODES = ("decompose", "hyde", "passthrough")


def _new_run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_transform_{suffix}"


def _decompose(query: str) -> list[str]:
    """Heuristic multi-hop split — replaced by LLM decomposer in phase 2."""
    parts = re.split(r"\s+(?:và|and)\s+|\?\s+", query.strip())
    return [p.strip().rstrip("?") for p in parts if p.strip()]


def _hyde(query: str) -> list[str]:
    """Skeleton HyDE — phase 2 calls the LLM with a 'write a passage that
    answers' prompt. For now we stub a single hypothesis suffix so the
    surface (returns 1+ transformed queries) stays exercisable."""
    return [query, f"{query} — hypothetical answer passage"]


@register_generator(
    name="transform",
    version="0.2.0",
    lifecycle="incubating",
    description="Query transform pipeline (CRAG/Self-RAG/HyDE, must-ship D5.4). Ports AOKP src/runtime/retrieval/.",
    source_aokp_module="src/runtime/retrieval/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {
                "type": "string",
                "enum": list(VALID_MODES),
                "default": "passthrough",
            },
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

    if mode == "decompose":
        transformed = _decompose(query)
        intent = "multi-hop" if len(transformed) > 1 else "simple"
    elif mode == "hyde":
        transformed = _hyde(query)
        intent = "ambiguous"  # HyDE is the disambiguation tool
    else:  # passthrough
        transformed = [query]
        intent = "simple"

    answer = "\n".join(
        [
            f"# Query Transform — mode={mode}",
            "",
            f"Input: `{query}`",
            f"Detected intent: **{intent}**",
            "",
            "## Transformed queries",
            *[f"- {q}" for q in transformed],
            "",
            "_Heuristic transformation — CRAG self-grader + reflection lands in W17-W18 phase 2._",
        ]
    )

    return SynthesisResult(
        run_id=run_id,
        generator="transform",
        status="partial",
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
            "heuristic transform — LLM-driven CRAG pending W17-W18 phase 2",
            f"mode={mode}",
            f"transformed_count={len(transformed)}",
        ],
    )
