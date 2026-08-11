"""ATP generator: analyze — Doctrine v6.0 Step 4 W17-W18 (D5.3).

Ports the RAGAS evaluation pipeline (`runRagasEvaluation` in AOKP
`src/runtime/eval/ragas/pipeline.ts:177`) into ATP. Second must-ship
port of three (D5.2 = report, D5.3 = analyze, D5.4 = transform).

Phase 1 + 2 status:
  ✅ Empty-pairs fallback (structured no-data result)
  ✅ Skeleton scoring (lexical-overlap heuristic) — `llm_mode=skeleton`
     (default) keeps CI deterministic without external service.
  ✅ Real LLM-judge scoring (`llm_mode=real`) — wired via
     generators.llm.call_llm; one metric-specific judge prompt per
     RAGAS metric. Score parsed from "Score: 0.NN" pattern; parse
     failure or LLM error falls back to heuristic so soak metrics
     never go to NaN.
  ⏸ Long-context chunking (>8K tokens get summarised first) — v6.1
"""

from __future__ import annotations

import re
from typing import Any

from generators.llm import LlmError, call_llm
from generators.registry import (
    Citation,
    GeneratorRequest,
    SynthesisResult,
    register_generator,
)

RAGAS_METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

# Metric-specific judge prompts. Each MUST end with the word "Score:" so
# the parser can find the float that follows. Mirrors AOKP's RAGAS prompt
# convention in src/runtime/eval/ragas/{faithfulness,...}.ts.
_JUDGE_PROMPTS: dict[str, str] = {
    "faithfulness": (
        "You are a RAGAS faithfulness judge. Score 0.0-1.0 where 1.0 means "
        "every claim in the answer is supported by the contexts.\n\n"
        "QUESTION: {question}\nCONTEXTS:\n{contexts}\nANSWER: {answer}\n\nScore:"
    ),
    "answer_relevancy": (
        "You are a RAGAS answer-relevancy judge. Score 0.0-1.0 where 1.0 means "
        "the answer directly addresses the question.\n\n"
        "QUESTION: {question}\nANSWER: {answer}\n\nScore:"
    ),
    "context_precision": (
        "You are a RAGAS context-precision judge. Score 0.0-1.0 where 1.0 means "
        "every context item is relevant to the question.\n\n"
        "QUESTION: {question}\nCONTEXTS:\n{contexts}\n\nScore:"
    ),
    "context_recall": (
        "You are a RAGAS context-recall judge. Score 0.0-1.0 where 1.0 means "
        "the contexts contain all the information needed to answer the question.\n\n"
        "QUESTION: {question}\nGROUND_TRUTH: {ground_truth}\nCONTEXTS:\n{contexts}\n\nScore:"
    ),
}

_SCORE_RE = re.compile(r"(?:^|\b)(0(?:\.\d+)?|1(?:\.0+)?)\b")


def _new_run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16] or f"{abs(hash(repr(req.payload))):016x}"
    return f"syn_analyze_{suffix}"


def _heuristic_score(pair: dict[str, Any], metric: str) -> float:
    """Lexical-overlap heuristic — used in skeleton mode and as fallback
    when an LLM judge raises LlmError or returns unparseable output.
    Awards 1.0 if predicted answer appears in contexts; 0.5 otherwise."""
    answer = str(pair.get("answer", "")).strip().lower()
    contexts = " ".join(str(c) for c in (pair.get("contexts") or [])).lower()
    if not answer or not contexts:
        return 0.0
    return 1.0 if answer in contexts else 0.5


def _parse_score(raw: str) -> float | None:
    """Extract a float in [0, 1] from an LLM judge response. Returns None
    when the response can't be parsed — caller falls back to heuristic."""
    if not raw:
        return None
    m = _SCORE_RE.search(raw.strip())
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    return v if 0.0 <= v <= 1.0 else None


def _llm_score(pair: dict[str, Any], metric: str, model: str | None) -> tuple[float, str]:
    """Real LLM judge — returns (score, source_label). Source is "llm" on
    successful judge call + parse, "heuristic_fallback_*" otherwise so the
    diagnostics layer can see WHY each score got the value it did."""
    template = _JUDGE_PROMPTS.get(metric)
    if template is None:
        return _heuristic_score(pair, metric), f"heuristic_fallback_unknown_metric"
    contexts = "\n".join(f"- {c}" for c in (pair.get("contexts") or []))
    prompt = template.format(
        question=str(pair.get("question", "")),
        answer=str(pair.get("answer", "")),
        ground_truth=str(pair.get("ground_truth", "")),
        contexts=contexts,
    )
    try:
        raw = call_llm(prompt, model)
    except LlmError:
        return _heuristic_score(pair, metric), "heuristic_fallback_llm_error"
    parsed = _parse_score(raw)
    if parsed is None:
        return _heuristic_score(pair, metric), "heuristic_fallback_unparseable"
    return parsed, "llm"


@register_generator(
    name="analyze",
    version="0.3.0",
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

    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model") if isinstance(payload.get("model"), str) else None

    per_pair = []
    metric_totals: dict[str, float] = {m: 0.0 for m in metrics}
    source_counts: dict[str, int] = {}  # tracks where each score came from
    for pair in pairs:
        scores: dict[str, float] = {}
        for m in metrics:
            if llm_mode == "real":
                score, source = _llm_score(pair, m, model)
            else:
                score, source = _heuristic_score(pair, m), "heuristic"
            scores[m] = score
            metric_totals[m] += score
            source_counts[source] = source_counts.get(source, 0) + 1
        per_pair.append(
            {
                "question": str(pair.get("question", "")),
                "answer": str(pair.get("answer", "")),
                "scores": scores,
            }
        )
    means = {m: metric_totals[m] / len(pairs) for m in metrics}

    mode_label = "LLM judges" if llm_mode == "real" else "lexical-overlap heuristic"
    answer_lines = [f"# RAGAS Eval — {query}", "", f"Pairs evaluated: **{len(pairs)}**", "",
                    f"Scoring mode: **{mode_label}**", "", "## Mean scores"]
    for m in metrics:
        answer_lines.append(f"- `{m}`: **{means[m]:.3f}**")
    answer_lines.append("")
    if llm_mode == "skeleton":
        answer_lines.append("_Skeleton mode — pass `params.llm_mode='real'` for LLM judges._")
    answer = "\n".join(answer_lines)

    diagnostics = [f"pair_count={len(pairs)}", f"metrics={metrics}", f"llm_mode={llm_mode}"]
    if source_counts:
        diagnostics.append(f"score_sources={source_counts}")

    return SynthesisResult(
        run_id=run_id,
        generator="analyze",
        status="success" if llm_mode == "real" else "partial",
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
        diagnostics=diagnostics,
    )
