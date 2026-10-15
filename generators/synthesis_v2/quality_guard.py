"""Port of AOKP `src/runtime/synthesis/quality-guard.ts`: ask the model to grade its own answer (naturalness, relevance, completeness, raw extraction, Vietnamese clarity).

A failure of any kind returns `None`, which the caller treats as "not passed" for the retry decision but never as an error (AOKP: "quality check failure should not block the response").
"""

from __future__ import annotations

import re
from typing import Any, Callable

from generators.prompts.synthesis_bank import QUALITY_CHECK_PROMPT, render_prompt

from .jsrt import JS_WS_CLASS, js_number, js_trim, js_truthy, load_json

ChatFn = Callable[[list[dict[str, str]]], str]
QualityScore = dict[str, Any]

# `/^```json\s*/i` and `/```\s*$/` — the `i` is spelled out so that only ASCII letters fold (JavaScript's non-unicode `/i` does not fold U+017F to "s").
_START_FENCE = re.compile(r"\A```[jJ][sS][oO][nN]" + JS_WS_CLASS + "*")
_END_FENCE = re.compile("```" + JS_WS_CLASS + r"*\Z")


def _clamp(n: float) -> float:
    return max(0.0, min(1.0, n))


def _num(v: Any) -> float:
    """`Number(v) || 0`"""
    x = js_number(v)
    return x if (x == x and x != 0) else 0.0


def check_answer_quality(query: str, answer: str, locale: str, config: dict[str, Any], chat: ChatFn) -> QualityScore | None:
    prompt = render_prompt(QUALITY_CHECK_PROMPT, locale, {"query": query, "answer": answer})
    try:
        raw = js_trim(chat([{"role": "user", "content": prompt}]))
        json_str = js_trim(_END_FENCE.sub("", _START_FENCE.sub("", raw, count=1), count=1))
        parsed = load_json(json_str)
        if parsed is None:
            raise TypeError("Cannot read properties of null")
        get = (lambda k: parsed.get(k)) if isinstance(parsed, dict) else (lambda k: None)
        return {
            "naturalness": _clamp(_num(get("naturalness"))),
            "relevance": _clamp(_num(get("relevance"))),
            "completeness": _clamp(_num(get("completeness"))),
            "rawExtraction": js_truthy(get("raw_extraction")),
            "vnClarity": get("vn_clarity") is not False,
            "verdict": "retry" if get("verdict") == "retry" else "pass",
        }
    except Exception:  # noqa: BLE001 — any failure means "no score"
        return None
