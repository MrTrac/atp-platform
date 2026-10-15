"""ATP generator: report_v2 — structured, grounded, quality-checked answers (KD-ATP-006, v6.1 Phase 2a/2b).

The Python port of AOKP `src/runtime/synthesis/*` (`generators/synthesis_v2/`), exposed as a registered generator. `report` (v1) stays as it was; this one adds what v1 lacked:
JSON sections (Tóm tắt / Chi tiết / ...), follow-up suggestions from the ATM domain engine, an LLM quality guard with one retry, a Jaccard citation-grounding verdict per `[n]`,
and the KB-gap statement. Behaviour is pinned to AOKP by golden vectors produced from the real TypeScript (tests/unit/test_synthesis_v2_golden.py).

NOT a cutover: nothing in AOKP or AIOS-OC calls it yet (Phase 2c lives in AOKP). Lifecycle stays `incubating`.

Modes (`params.llm_mode`):
  skeleton (default)  no LLM, deterministic: the chunk-based answer AOKP falls back to when the model fails, plus the domain suggestions and the grounding verdicts. status "partial".
  real                the model is called through `generators.llm.call_llm` with the system prompt kept separate (AOKP sends two messages); status "success" when every synthesis
                      call produced usable text, "partial" when AOKP's fallback had to take over.

The AOKP-shaped result goes into `structured` (snake_case): sections, suggestions, quality_score, grounding, kb_gap, external_ref_used, synthesis_retries, total_llm_calls, locale.
`citations` are the chunks the answer actually cites (AOKP semantics), in citation order.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from generators.llm import LlmError, call_llm
from generators.registry import Citation, GeneratorRequest, SynthesisResult, register_generator
from generators.synthesis_v2.jsrt import js_trim
from generators.synthesis_v2.parser import clean_llm_output
from generators.synthesis_v2.synthesizer import synthesize_answer


def _run_id(req: GeneratorRequest) -> str:
    suffix = (req.request_id or "")[:16]
    if not suffix:
        suffix = hashlib.sha256(json.dumps(req.payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"syn_report_v2_{suffix}"


def _to_aokp_chunks(chunks: list[Any]) -> list[dict[str, Any]]:
    """ATP context chunk -> AOKP ContextChunk. `snippet` is the text; `source_id` is the source pointer; a missing title falls back to the source id."""
    out: list[dict[str, Any]] = []
    for i, c in enumerate(chunks, 1):
        c = c if isinstance(c, dict) else {}
        chunk: dict[str, Any] = {
            "artifactId": str(c.get("artifact_id", "")),
            "title": str(c.get("title") or c.get("source_id") or f"Source {i}"),
            "content": str(c.get("snippet", "")),
        }
        if c.get("source_id"):
            chunk["sourcePointer"] = str(c["source_id"])
        if c.get("relevance_score") is not None:
            try:
                chunk["score"] = float(c["relevance_score"])
            except (TypeError, ValueError):
                pass
        out.append(chunk)
    return out


class _Chat:
    """Adapts AOKP's `chat(messages)` to ATP's `call_llm(prompt, model, system=...)` and remembers what went wrong, so the generator can say whether the answer is the model's or the fallback."""

    def __init__(self, model: str | None, real: bool) -> None:
        self.model = model
        self.real = real
        self.calls = 0
        self.synthesis_failures: list[str] = []

    def __call__(self, messages: list[dict[str, str]]) -> str:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        user = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
        is_synthesis = bool(system)
        if not self.real:
            if is_synthesis:
                self.synthesis_failures.append("llm_mode=skeleton")
            raise LlmError("llm_mode=skeleton (no model call)")
        self.calls += 1
        try:
            text = call_llm(user, self.model, system=system or None)
        except Exception as e:  # noqa: BLE001 — LlmError or a provider bug: either way AOKP degrades to the fallback, and the status must say so
            if is_synthesis:
                self.synthesis_failures.append(f"llm_error={type(e).__name__}: {e}")
            raise
        if is_synthesis and not clean_llm_output(js_trim(text)):
            self.synthesis_failures.append("empty_model_output")
        return text


def _snake_quality(q: dict[str, Any] | None) -> dict[str, Any] | None:
    if q is None:
        return None
    return {"naturalness": q["naturalness"], "relevance": q["relevance"], "completeness": q["completeness"],
            "raw_extraction": q["rawExtraction"], "vn_clarity": q["vnClarity"], "verdict": q["verdict"]}


def _snake_grounding(g: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall": g["overall"],
        "average_score": g["averageScore"],
        "unsupported_count": g["unsupportedCount"],
        "per_citation": [{"citation_index": p["citationIndex"], "artifact_id": p["artifactId"], "claim_snippet": p["claimSnippet"],
                          "support_score": p["supportScore"], "verdict": p["verdict"]} for p in g["perCitation"]],
    }


@register_generator(
    name="report_v2",
    version="0.1.0",
    lifecycle="incubating",
    description="Structured, grounded, quality-checked answer synthesis. Python port of AOKP src/runtime/synthesis (sections, suggestions, quality guard + retry, citation grounding, KB gap).",
    source_aokp_module="src/runtime/synthesis/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "locale": {"type": "string", "enum": ["vi", "en"], "default": "vi"},
            "llm_mode": {"type": "string", "enum": ["skeleton", "real"], "default": "skeleton",
                         "description": "skeleton = no LLM (deterministic, chunk-based answer); real = call the model through call_llm with a separate system prompt"},
            "model": {"type": "string", "description": "Provider-prefixed model id (e.g. 'anthropic/claude-haiku-4-5-20251001'; empty = bridge default). Used when llm_mode='real'."},
            "conversation_history": {"type": "string", "description": "Earlier turns, passed to the prompt as-is"},
            "quality_check": {"type": "boolean", "default": True, "description": "Grade the answer with the model and retry once when it is rejected"},
            "max_retries": {"type": "integer", "minimum": 0, "maximum": 3, "default": 1},
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
                    "required": ["artifact_id", "snippet"],
                },
            },
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    started = time.monotonic()
    payload = req.payload or {}
    run_id = _run_id(req)
    query = str(payload.get("query", "")).strip()
    if not query:
        return SynthesisResult(run_id=run_id, generator="report_v2", status="failed", diagnostics=["query is required"])

    locale = str(payload.get("locale", "vi"))
    if locale not in {"vi", "en"}:
        locale = "vi"
    raw_chunks = payload.get("context_chunks") or []
    if not isinstance(raw_chunks, list):
        return SynthesisResult(run_id=run_id, generator="report_v2", status="failed", diagnostics=["context_chunks must be an array"])
    llm_mode = str(payload.get("llm_mode", "skeleton"))
    model = payload.get("model") if isinstance(payload.get("model"), str) and payload.get("model") else None

    try:
        max_retries = int(payload.get("max_retries", 1))
    except (TypeError, ValueError):
        max_retries = 1
    max_retries = max(0, min(3, max_retries))
    config = {"maxRetries": max_retries, "qualityCheckEnabled": bool(payload.get("quality_check", True))}

    chunks = _to_aokp_chunks(raw_chunks)
    request: dict[str, Any] = {"query": query, "locale": locale, "contextChunks": chunks, "sourcePipeline": "atp.report_v2"}
    history = payload.get("conversation_history")
    if isinstance(history, str) and history:
        request["conversationHistory"] = history

    chat = _Chat(model, real=(llm_mode == "real"))
    result = synthesize_answer(request, chat, config)

    diagnostics = [f"chunk_count={len(chunks)}", f"llm_mode={llm_mode}" + (f" model={model or 'default'}" if llm_mode == "real" else "")]
    if not chunks:
        status = "success"
        diagnostics.append("no context chunks supplied — returned the no-info answer (no model call)")
    elif llm_mode != "real":
        status = "partial"
        diagnostics.append("llm_mode=skeleton (default — deterministic, chunk-based answer)")
    elif chat.synthesis_failures:
        status = "partial"
        diagnostics.append("fell back to the chunk-based answer: " + "; ".join(chat.synthesis_failures))
    else:
        status = "success"
    diagnostics.append(f"llm_calls={result['totalLlmCalls']} retries={result['synthesisRetries']} grounding={result['grounding']['overall']}")
    if result["kbGap"]:
        diagnostics.append(f"kb_gap={result['kbGap']}")

    citations = []
    for cit in result["citations"]:
        src = raw_chunks[cit["index"] - 1] if isinstance(raw_chunks[cit["index"] - 1], dict) else {}
        citations.append(Citation(
            artifact_id=str(src.get("artifact_id", "")),
            source_id=str(src.get("source_id", "")),
            snippet=str(src.get("snippet", ""))[:4096],
            classification_path=tuple(src.get("classification_path") or ()),
            relevance_score=float(src.get("relevance_score", 0.0) or 0.0),
            rank=cit["index"],
        ))

    return SynthesisResult(
        run_id=run_id,
        generator="report_v2",
        status=status,
        answer=result["answer"],
        citations=citations,
        usage={"input_tokens": 0, "output_tokens": len(result["answer"].split()), "knowledge_queries": 0, "duration_ms": int((time.monotonic() - started) * 1000)},
        diagnostics=diagnostics,
        structured={
            "locale": result["locale"],
            "sections": result["sections"],
            "suggestions": result["suggestions"],
            "quality_score": _snake_quality(result["qualityScore"]),
            "grounding": _snake_grounding(result["grounding"]),
            "kb_gap": result["kbGap"],
            "external_ref_used": result["externalRefUsed"],
            "synthesis_retries": result["synthesisRetries"],
            "total_llm_calls": result["totalLlmCalls"],
        },
    )
