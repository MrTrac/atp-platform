"""ATP generator: federation — Doctrine v6.0 Step 4 W19-20 (D5.5 stretch).

Ports the merge-strategy core of AOKP `src/runtime/federation/coordinator.ts`
(`runFederatedQuery` → `mergeRankFusion` / `mergeLLMSynthesize`) into ATP.
First of two stretch ports per roadmap §3 (D5.5 = federation, plus temporal).

Scope decision: ATP is the synthesis plane. Node discovery, health checks,
and HTTP fan-out remain AOKP-side concerns (federation registry coupled to
AOKP's KB nodes). ATP's federation generator accepts **pre-fetched node
answers** in the payload and applies the merge strategy. Callers route
fan-out through AIOS-OC (presentation plane) which already aggregates
multi-source results.

Phase 1 + 2 status:
  ✅ Empty-results fallback (structured no-data result, parity with AOKP
     `mergeRankFusion` "No nodes returned results.")
  ✅ Skeleton merge — `llm_mode=skeleton` (default) covers rank_fusion
     (interleave by node, label "[node]: answer") and concatenate
     (`---`-joined). Deterministic, no external service.
  ✅ Real LLM synthesis — `llm_mode=real` with `merge_strategy=llm_synthesize`
     calls call_llm with the AOKP synthesis prompt; LlmError or short
     output falls back to rank_fusion so federation never blocks the
     dispatch path.
  ⏸ Live HTTP fan-out + node registry — out-of-scope for ATP plane.
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

VALID_STRATEGIES = ("rank_fusion", "llm_synthesize", "concatenate")


def _new_run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_federation_{suffix}"


def _success_results(node_answers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter to `status` == "success" (default if status absent)."""
    out: list[dict[str, Any]] = []
    for n in node_answers:
        status = str(n.get("status", "success")).lower()
        if status == "success" and str(n.get("answer", "")).strip():
            out.append(n)
    return out


def _merge_rank_fusion(success: list[dict[str, Any]]) -> str:
    """Interleave by node — parity with AOKP coordinator.ts:172-180."""
    if not success:
        return "No nodes returned results."
    if len(success) == 1:
        return str(success[0].get("answer", ""))
    return "\n\n".join(
        f"[{n.get('node_name', n.get('node_id', '?'))}]: {n.get('answer', '')}"
        for n in success
    )


def _merge_concatenate(success: list[dict[str, Any]]) -> str:
    """`---`-separated raw answers — parity with coordinator.ts:296-297."""
    if not success:
        return "No nodes returned results."
    return "\n\n---\n\n".join(
        str(n.get("answer", "")).strip() for n in success if n.get("answer")
    )


_LLM_SYNTH_PROMPT = (
    "Synthesize answers from multiple knowledge bases into one unified answer.\n\n"
    "Query: {query}\n\n"
    "Node answers:\n{answers_block}\n\n"
    "Unified answer (combine non-contradictory info, note disagreements):"
)


def _merge_llm_synthesize(
    query: str,
    success: list[dict[str, Any]],
    model: str | None,
) -> tuple[str, str]:
    """Real LLM synthesis — returns (answer, source_label).
    Falls back to rank_fusion on LlmError or short output (<10 chars),
    matching AOKP coordinator.ts:185-228 fallback behaviour."""
    if not success:
        return "No nodes returned results.", "no_nodes"
    if len(success) == 1:
        return str(success[0].get("answer", "")), "single_node_passthrough"

    answers_block = "\n\n".join(
        f"[{n.get('node_name', n.get('node_id', '?'))}]: {str(n.get('answer', ''))[:800]}"
        for n in success
    )
    prompt = _LLM_SYNTH_PROMPT.format(query=query, answers_block=answers_block)
    try:
        raw = call_llm(prompt, model)
    except LlmError:
        return _merge_rank_fusion(success), "rank_fusion_fallback_llm_error"
    if not raw or len(raw.strip()) < 10:
        return _merge_rank_fusion(success), "rank_fusion_fallback_short_output"
    return raw.strip(), "llm"


def _collect_evidence(success: list[dict[str, Any]]) -> list[str]:
    seen: dict[str, bool] = {}
    for n in success:
        for eid in n.get("evidence_ids") or []:
            if isinstance(eid, str) and eid not in seen:
                seen[eid] = True
    return list(seen.keys())


@register_generator(
    name="federation",
    version="0.3.0",
    lifecycle="incubating",
    description="Cross-facility federation rank fusion + LLM synthesis (D5.5 stretch).",
    source_aokp_module="src/runtime/federation/coordinator.ts",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Federated query text"},
            "node_answers": {
                "type": "array",
                "description": "Pre-fetched answers from KB nodes (fan-out happens upstream)",
                "items": {
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "string"},
                        "node_name": {"type": "string"},
                        "status": {"type": "string", "enum": ["success", "error", "timeout"]},
                        "answer": {"type": "string"},
                        "evidence_ids": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["answer"],
                },
            },
            "merge_strategy": {
                "type": "string",
                "enum": list(VALID_STRATEGIES),
                "default": "rank_fusion",
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
    node_answers = payload.get("node_answers") or []
    merge_strategy = str(payload.get("merge_strategy", "rank_fusion"))
    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model") if isinstance(payload.get("model"), str) else None

    run_id = _new_run_id(req)

    if not query:
        return SynthesisResult(
            run_id=run_id,
            generator="federation",
            status="failed",
            answer="",
            citations=[],
            diagnostics=["query is required"],
        )
    if merge_strategy not in VALID_STRATEGIES:
        return SynthesisResult(
            run_id=run_id,
            generator="federation",
            status="failed",
            answer="",
            citations=[],
            diagnostics=[f"unknown merge_strategy: {merge_strategy!r}"],
        )

    if not node_answers:
        return SynthesisResult(
            run_id=run_id,
            generator="federation",
            status="success",
            answer="No node answers supplied — federation merge skipped.",
            citations=[],
            usage={
                "input_tokens": 0,
                "output_tokens": 0,
                "knowledge_queries": 0,
                "duration_ms": 0,
                "nodes_queried": 0,
                "nodes_responded": 0,
            },
            diagnostics=["empty node_answers — pass-through"],
        )

    success = _success_results(node_answers)

    # Resolve effective strategy: skeleton mode never invokes LLM
    use_llm = llm_mode == "real" and merge_strategy == "llm_synthesize"
    if use_llm:
        answer, source = _merge_llm_synthesize(query, success, model)
    elif merge_strategy == "concatenate":
        answer, source = _merge_concatenate(success), "concatenate"
    elif merge_strategy == "llm_synthesize":
        # Skeleton mode but caller asked for llm — degrade to rank_fusion
        answer, source = _merge_rank_fusion(success), "rank_fusion_skeleton_degrade"
    else:
        answer, source = _merge_rank_fusion(success), "rank_fusion"

    evidence_ids = _collect_evidence(success)
    citations = [
        Citation(
            artifact_id=eid,
            source_id="federation",
            snippet="",
            classification_path=(),
            relevance_score=0.0,
            rank=i,
        )
        for i, eid in enumerate(evidence_ids)
    ]

    diagnostics = [
        f"nodes_total={len(node_answers)}",
        f"nodes_responded={len(success)}",
        f"merge_strategy={merge_strategy}",
        f"llm_mode={llm_mode}",
        f"answer_source={source}",
    ]

    return SynthesisResult(
        run_id=run_id,
        generator="federation",
        status="success" if use_llm else "partial",
        answer=answer,
        citations=citations,
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
            "nodes_queried": len(node_answers),
            "nodes_responded": len(success),
        },
        diagnostics=diagnostics,
    )
