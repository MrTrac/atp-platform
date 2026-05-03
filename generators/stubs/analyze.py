"""ATP generator: analyze — Doctrine v6.0 Step 4 W17-W18 (D5.3).

Ports the RAGAS evaluation pipeline (`runRagasEvaluation` in AOKP
`src/runtime/eval/ragas/pipeline.ts:177`) into ATP. Second must-ship
port of three (D5.2 = report, D5.3 = analyze, D5.4 = transform).

Phase 1 scope (this commit):
  ✅ Empty-pairs fallback — returns a structured "no data" result
     mirroring AOKP's behaviour when no eval pairs supplied
  ✅ Per-pair metric skeleton — for each (question, contexts,
     answer, ground_truth) pair, emits placeholder per-metric scores
     so the dispatch + aggregation surface (mean per metric) works
     end-to-end without requiring Ollama / cloud-LLM in CI
  ⏸ Real LLM-driven scoring (faithfulness / answer-relevancy /
     context-precision / context-recall) — deferred to phase 2

The 4 metric names match RAGAS standard. Phase 2 replaces the
placeholder per-pair score with real LLM calls; descriptor stays
incubating until then.
"""

from __future__ import annotations

from typing import Any

from generators.registry import (
    Citation,
    GeneratorRequest,
    SynthesisResult,
    register_generator,
)

RAGAS_METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def _new_run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_analyze_{suffix}"


def _placeholder_score(pair: dict[str, Any], metric: str) -> float:
    """Heuristic placeholder until LLM-driven scoring lands.

    Awards 1.0 only if the predicted answer appears literally in the contexts
    (a tiny lexical-overlap stand-in); 0.0 otherwise. This is intentionally
    weaker than the AOKP RAGAS implementation — it just exercises the
    dispatch + aggregation path. Phase 2 replaces this with real LLM judges.
    """
    answer = str(pair.get("answer", "")).strip().lower()
    contexts = " ".join(str(c) for c in (pair.get("contexts") or [])).lower()
    if not answer or not contexts:
        return 0.0
    overlap = answer in contexts
    return 1.0 if overlap else 0.5


@register_generator(
    name="analyze",
    version="0.2.0",
    lifecycle="incubating",
    description="RAGAS-shape evaluation synthesis (must-ship D5.3). Ports AOKP src/runtime/eval/ragas/pipeline.ts.",
    source_aokp_module="src/runtime/eval/ragas/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Identifying label for this eval run"},
            "pairs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {"type": "string"},
                        "contexts": {"type": "array", "items": {"type": "string"}},
                        "ground_truth": {"type": "string"},
                    },
                    "required": ["question", "answer", "contexts"],
                },
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string", "enum": list(RAGAS_METRICS)},
                "description": f"Subset of {list(RAGAS_METRICS)}; defaults to all 4",
            },
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    payload = req.payload or {}
    query = str(payload.get("query", "")).strip()
    pairs = payload.get("pairs") or []
    metrics = payload.get("metrics") or list(RAGAS_METRICS)
    bad_metrics = [m for m in metrics if m not in RAGAS_METRICS]

    run_id = _new_run_id(req)

    if not query:
        return SynthesisResult(
            run_id=run_id,
            generator="analyze",
            status="failed",
            answer="",
            citations=[],
            diagnostics=["query is required"],
        )
    if bad_metrics:
        return SynthesisResult(
            run_id=run_id,
            generator="analyze",
            status="failed",
            answer="",
            citations=[],
            diagnostics=[f"unknown metrics: {bad_metrics}"],
        )

    if not pairs:
        return SynthesisResult(
            run_id=run_id,
            generator="analyze",
            status="success",
            answer="No evaluation pairs supplied — RAGAS run skipped.",
            citations=[],
            usage={"input_tokens": 0, "output_tokens": 0, "knowledge_queries": 0, "duration_ms": 0},
            diagnostics=["empty pairs — no metrics computed"],
        )

    per_pair = []
    metric_totals: dict[str, float] = {m: 0.0 for m in metrics}
    for pair in pairs:
        scores = {m: _placeholder_score(pair, m) for m in metrics}
        for m, s in scores.items():
            metric_totals[m] += s
        per_pair.append(
            {
                "question": str(pair.get("question", "")),
                "answer": str(pair.get("answer", "")),
                "scores": scores,
            }
        )
    means = {m: metric_totals[m] / len(pairs) for m in metrics}

    answer_lines = [f"# RAGAS Eval — {query}", "", f"Pairs evaluated: **{len(pairs)}**", "", "## Mean scores"]
    for m in metrics:
        answer_lines.append(f"- `{m}`: **{means[m]:.3f}**")
    answer_lines.append("")
    answer_lines.append("_Skeletal scoring (lexical-overlap heuristic) — LLM judges land in W17-W18 phase 2._")
    answer = "\n".join(answer_lines)

    return SynthesisResult(
        run_id=run_id,
        generator="analyze",
        status="partial",
        answer=answer,
        citations=[],
        usage={
            "input_tokens": 0,
            "output_tokens": len(answer.split()),
            "knowledge_queries": 0,
            "duration_ms": 0,
            "pairs_evaluated": len(pairs),
            "metric_means": means,
        },
        diagnostics=[
            "skeletal scoring — LLM judges pending W17-W18 phase 2",
            f"pair_count={len(pairs)}",
            f"metrics={metrics}",
        ],
    )
