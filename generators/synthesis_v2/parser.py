"""Port of the structured-response parser and text helpers of AOKP `src/runtime/synthesis/synthesizer.ts`.

`parse_structured_response` takes the model's raw text and returns sections / suggestions / external-reference flag / KB gap, falling back to one flat "Summary" section when the
output is not the JSON object the prompt asked for. JavaScript semantics are reproduced where they decide the result (see `jsrt`): truthiness of `[]`, `String()` of a number or an
array, `trim()`, the `JSON.parse` that refuses NaN/Infinity, and the greedy `/\\{[\\s\\S]*\\}/` that runs from the FIRST `{` to the LAST `}`.
"""

from __future__ import annotations

import re
from typing import Any

from .jsrt import JS_WS_CLASS, js_slice_utf16, js_string, js_trim, js_truthy, load_json

Section = dict[str, str]
Suggestion = dict[str, Any]
Parsed = dict[str, Any]

_BRACES = re.compile(r"\{.*\}", re.DOTALL)
_FENCE = re.compile(r"```json.*```", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
# JavaScript `/^\s*\n/gm`: `^` matches after ANY line terminator (\n \r U+2028 U+2029), not only after \n; `\s` is the ECMAScript whitespace set.
_BLANK_LINES = re.compile(r"(?<![^\n\r  ])" + JS_WS_CLASS + r"*\n")


def _summary_heading(locale: str) -> str:
    return "Tóm tắt" if locale == "vi" else "Summary"


def _prop(parsed: Any, key: str) -> Any:
    """`parsed[key]` as JavaScript evaluates it: undefined (None here) on anything but an object; `null` itself throws a TypeError."""
    if parsed is None:
        raise TypeError("Cannot read properties of null")
    return parsed.get(key) if isinstance(parsed, dict) else None


def parse_structured_response(raw: str, locale: str) -> Parsed:
    try:
        json_str = raw
        m = _BRACES.search(raw)
        if m:
            json_str = m.group(0)
        parsed = load_json(json_str)

        raw_sections = _prop(parsed, "sections")
        raw_sections = raw_sections if isinstance(raw_sections, list) else []
        sections: list[Section] = [
            {"heading": s["heading"], "content": s["content"]}
            for s in raw_sections
            if isinstance(s, dict) and isinstance(s.get("heading"), str) and isinstance(s.get("content"), str)
        ]

        raw_suggestions = _prop(parsed, "suggestions")
        raw_suggestions = raw_suggestions if isinstance(raw_suggestions, list) else []
        suggestions: list[Suggestion] = []
        for s in raw_suggestions:
            if not (isinstance(s, dict) and isinstance(s.get("question"), str)):
                continue
            rationale = s.get("rationale")
            item: Suggestion = {"question": s["question"], "rationale": "" if rationale is None else js_string(rationale)}
            if js_truthy(s.get("pipeline")):
                item["pipeline"] = js_string(s["pipeline"])
            suggestions.append(item)
        suggestions = suggestions[:3]

        external_ref_used = js_truthy(_prop(parsed, "external_ref_used"))
        gap = _prop(parsed, "kb_gap")
        kb_gap = js_trim(gap) if isinstance(gap, str) and js_trim(gap) else None

        if not sections:
            stripped = js_trim(_FENCE.sub("", raw))
            sections.append({"heading": _summary_heading(locale), "content": stripped or raw})

        return {"sections": sections, "suggestions": suggestions, "externalRefUsed": external_ref_used, "kbGap": kb_gap}
    except Exception:  # noqa: BLE001 — AOKP treats ANY failure as "not the JSON we asked for"
        return {"sections": [{"heading": _summary_heading(locale), "content": raw}], "suggestions": [], "externalRefUsed": False, "kbGap": None}


def clean_llm_output(text: str) -> str:
    """AOKP `cleanLlmOutput`: drop `<think>…</think>` blocks and blank-line runs, then trim."""
    text = _THINK.sub("", text)
    text = _BLANK_LINES.sub("\n", text)
    return js_trim(text)


def sections_to_plain_text(sections: list[Section]) -> str:
    return "\n\n".join(f"**{s['heading']}**\n{s['content']}" for s in sections)


def build_fallback(chunks: list[dict[str, Any]], locale: str) -> dict[str, Any]:
    """Answer built from the first three chunks when the model produced nothing usable."""
    header = "Dựa trên thông tin tìm được:" if locale == "vi" else "Based on available information:"
    items = [f"[{i + 1}] {c['title']}: {js_slice_utf16(c['content'], 200)}..." for i, c in enumerate(chunks[:3])]
    answer = f"{header}\n\n" + "\n\n".join(items)
    return {"answer": answer, "sections": [{"heading": _summary_heading(locale), "content": answer}], "suggestions": [], "externalRefUsed": False}
