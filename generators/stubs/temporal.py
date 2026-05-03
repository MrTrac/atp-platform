"""ATP generator: temporal — Doctrine v6.0 Step 4 W19-20 (D5.5 stretch).

Ports the synthesis tail of AOKP `src/runtime/graph/temporal/pipeline.ts`
(`queryTemporalGraph`) into ATP. Second of two stretch ports per roadmap §3
(D5.5 = federation + temporal).

Scope decision: ATP is the synthesis plane. Temporal-graph **build** and
**index storage** stay AOKP-side (`temporal-index.json` lives next to
AOKP's evidence store). The ATP port accepts a **pre-fetched temporal
context** (entities + causal_relations + causal_chains + timeline_events)
in the payload and applies skeleton-or-LLM synthesis. Callers route
graph-build through AOKP's `/api/temporal-graph` and pass the matched
slice into ATP for synthesis.

Phase 1 + 2 status:
  ✅ Empty-context fallback (structured no-data result, parity with AOKP
     pipeline.ts:91-103 "Temporal graph is empty.")
  ✅ Skeleton answer — `llm_mode=skeleton` (default) emits a structural
     summary: "Found N entities, M causal relations, K causal chains."
     plus a markdown digest. Deterministic, no external service.
  ✅ Real LLM synthesis — `llm_mode=real` calls call_llm with the AOKP
     temporal-synthesis prompt; LlmError or short output falls back to
     structural summary.
  ⏸ Live temporal-index loading — out-of-scope for ATP plane.
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
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_temporal_{suffix}"


_LLM_SYNTH_PROMPT = (
    "Answer this query about ATM systems using temporal and causal knowledge.\n\n"
    "Query: {query}\n\n"
    "Context:\n{context_block}\n\n"
    "Provide a concise answer focusing on causal relationships and temporal patterns. Answer:"
)


def _format_entities(entities: list[dict[str, Any]]) -> str:
    if not entities:
        return "(none)"
    return ", ".join(
        f"{e.get('label', e.get('entity_id', '?'))}({e.get('current_state', '?')})"
        for e in entities[:10]
    )


def _format_relations(relations: list[dict[str, Any]]) -> str:
    if not relations:
        return "(none)"
    return "; ".join(
        f"{r.get('cause_entity_id', '?')} -[{r.get('causal_type', 'caused_by')}]-> "
        f"{r.get('effect_entity_id', '?')}"
        for r in relations[:5]
    )


def _format_chains(chains: list[dict[str, Any]]) -> str:
    if not chains:
        return "(none)"
    return " | ".join(
        str(c.get("description", "")) for c in chains[:3] if c.get("description")
    )


def _build_context_block(
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    chains: list[dict[str, Any]],
) -> str:
    return "\n".join([
        f"Entities: {_format_entities(entities)}",
        f"Causal relations: {_format_relations(relations)}",
        f"Causal chains: {_format_chains(chains)}",
    ])


def _skeleton_answer(
    query: str,
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    chains: list[dict[str, Any]],
) -> str:
    """Deterministic fallback — structural summary of the temporal slice."""
    head = (
        f"Found {len(entities)} entities, {len(relations)} causal relations, "
        f"{len(chains)} causal chains."
    )
    parts = [f"# Temporal query — {query}", "", head, ""]
    if entities:
        parts.append("## Entities")
        for e in entities[:10]:
            label = e.get("label", e.get("entity_id", "?"))
            kind = e.get("kind", "?")
            state = e.get("current_state", "?")
            parts.append(f"- **{label}** ({kind}, state=`{state}`)")
        parts.append("")
    if relations:
        parts.append("## Causal relations")
        for r in relations[:8]:
            parts.append(
                f"- `{r.get('cause_entity_id', '?')}` "
                f"-[{r.get('causal_type', 'caused_by')}]-> "
                f"`{r.get('effect_entity_id', '?')}`"
            )
        parts.append("")
    if chains:
        parts.append("## Causal chains")
        for c in chains[:5]:
            d = c.get("description")
            if d:
                parts.append(f"- {d}")
        parts.append("")
    return "\n".join(parts).rstrip()


def _llm_synthesize(
    query: str,
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    chains: list[dict[str, Any]],
    model: str | None,
) -> tuple[str, str]:
    """Real LLM synthesis — returns (answer, source_label).
    Falls back to skeleton on LlmError or short output (<10 chars),
    matching AOKP pipeline.ts:159-196 fallback behaviour."""
    context_block = _build_context_block(entities, relations, chains)
    prompt = _LLM_SYNTH_PROMPT.format(query=query, context_block=context_block)
    try:
        raw = call_llm(prompt, model)
    except LlmError:
        return _skeleton_answer(query, entities, relations, chains), "skeleton_fallback_llm_error"
    if not raw or len(raw.strip()) < 10:
        return _skeleton_answer(query, entities, relations, chains), "skeleton_fallback_short_output"
    return raw.strip(), "llm"


def _collect_evidence(
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> list[str]:
    seen: dict[str, bool] = {}
    for e in entities:
        for tl in e.get("timeline") or []:
            sid = tl.get("source_artifact_id") if isinstance(tl, dict) else None
            if isinstance(sid, str) and sid not in seen:
                seen[sid] = True
    for r in relations:
        for eid in r.get("evidence_artifact_ids") or []:
            if isinstance(eid, str) and eid not in seen:
                seen[eid] = True
    return list(seen.keys())


@register_generator(
    name="temporal",
    version="0.3.0",
    lifecycle="incubating",
    description="Temporal causal KG synthesis (D5.5 stretch).",
    source_aokp_module="src/runtime/graph/temporal/pipeline.ts",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "entities": {
                "type": "array",
                "description": "Pre-matched entities from AOKP temporal-index",
                "items": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"type": "string"},
                        "label": {"type": "string"},
                        "kind": {"type": "string"},
                        "current_state": {"type": "string"},
                        "timeline": {"type": "array"},
                    },
                },
            },
            "causal_relations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "cause_entity_id": {"type": "string"},
                        "effect_entity_id": {"type": "string"},
                        "causal_type": {"type": "string"},
                        "evidence_artifact_ids": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "causal_chains": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"description": {"type": "string"}},
                },
            },
            "llm_mode": {
                "type": "string",
                "enum": ["skeleton", "real"],
                "default": "skeleton",
            },
            "model": {"type": "string"},
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    payload = req.payload or {}
    query = str(payload.get("query", "")).strip()
    entities = payload.get("entities") or []
    relations = payload.get("causal_relations") or []
    chains = payload.get("causal_chains") or []
    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model") if isinstance(payload.get("model"), str) else None

    run_id = _new_run_id(req)

    if not query:
        return SynthesisResult(
            run_id=run_id,
            generator="temporal",
            status="failed",
            answer="",
            citations=[],
            diagnostics=["query is required"],
        )

    if not entities and not relations and not chains:
        return SynthesisResult(
            run_id=run_id,
            generator="temporal",
            status="success",
            answer=(
                "Temporal context is empty — synthesis skipped. "
                "Build the temporal graph first (POST /api/temporal-graph "
                "{ action: 'build' } against AOKP) and pass matched entities."
            ),
            citations=[],
            usage={
                "input_tokens": 0,
                "output_tokens": 0,
                "knowledge_queries": 0,
                "duration_ms": 0,
                "entities": 0,
                "relations": 0,
                "chains": 0,
            },
            diagnostics=["empty temporal context — pass-through"],
        )

    if llm_mode == "real":
        answer, source = _llm_synthesize(query, entities, relations, chains, model)
    else:
        answer, source = _skeleton_answer(query, entities, relations, chains), "skeleton"

    evidence_ids = _collect_evidence(entities, relations)
    citations = [
        Citation(
            artifact_id=eid,
            source_id="temporal",
            snippet="",
            classification_path=(),
            relevance_score=0.0,
            rank=i,
        )
        for i, eid in enumerate(evidence_ids)
    ]

    diagnostics = [
        f"entities={len(entities)}",
        f"relations={len(relations)}",
        f"chains={len(chains)}",
        f"llm_mode={llm_mode}",
        f"answer_source={source}",
    ]

    return SynthesisResult(
        run_id=run_id,
        generator="temporal",
        status="success" if llm_mode == "real" else "partial",
        answer=answer,
        citations=citations,
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
            "entities": len(entities),
            "relations": len(relations),
            "chains": len(chains),
        },
        diagnostics=diagnostics,
    )
