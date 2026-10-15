"""Port of AOKP `src/runtime/synthesis/suggestion-engine.ts`: domain-aware follow-up questions (radar, FDP, safety net, network, firewall, rack, TWR).

The topic regexes are taken from the TypeScript SOURCE (`_data.TOPIC_PATTERN_SOURCES`) and compiled here with JavaScript semantics, because Python's `re` differs in exactly the places
these patterns touch:
  * `\\b` in JavaScript is ASCII-only: "tủ" ends in a non-word character, so `\\b(...|tủ)\\b` needs a word character AFTER it ("tủx" matches, "tủ " does not);
  * `\\s` is the ECMAScript whitespace set, `\\d` is `[0-9]`;
  * the `i` flag folds case per character with `toUpperCase` and never maps a non-ASCII character onto an ASCII one (so U+212A KELVIN SIGN does not match "k").
"""

from __future__ import annotations

import re
from typing import Any

from ._data import GENERIC_SUGGESTIONS, TOPIC_PATTERN_SOURCES, TOPIC_SUGGESTIONS
from .jsrt import JS_WS_CLASS, js_canon_upper, js_split_ws, utf16_len

Chunk = dict[str, Any]
Suggestion = dict[str, Any]

_WORD = "[A-Za-z0-9_]"
_BOUNDARY = f"(?:(?<={_WORD})(?!{_WORD})|(?<!{_WORD})(?={_WORD}))"  # JavaScript `\b`: exactly one side is an ASCII word character


def compile_js_pattern(source: str, flags: str) -> "re.Pattern[str]":
    """Translate the (small) JavaScript regex dialect used by AOKP's topic patterns into an equivalent Python pattern."""
    ignore = "i" in flags
    out: list[str] = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch == "\\":
            esc = source[i + 1]
            if esc == "b":
                out.append(_BOUNDARY)
            elif esc == "s":
                out.append(JS_WS_CLASS)
            elif esc == "d":
                out.append("[0-9]")
            else:
                raise NotImplementedError(f"unsupported escape \\{esc} in {source!r}")
            i += 2
            continue
        out.append(js_canon_upper(ch) if ignore else ch)
        i += 1
    return re.compile("".join(out))


_PATTERNS: list[tuple[str, "re.Pattern[str]", bool]] = [(topic, compile_js_pattern(src, fl), "i" in fl) for topic, src, fl in TOPIC_PATTERN_SOURCES]


def _matches(topic_regex: "re.Pattern[str]", ignore: bool, text: str) -> bool:
    return topic_regex.search(js_canon_upper(text) if ignore else text) is not None


def _is_too_similar(query: str, suggestion: str) -> bool:
    q_words = {w for w in js_split_ws(query.lower()) if utf16_len(w) > 2}
    s_words = [w for w in js_split_ws(suggestion.lower()) if utf16_len(w) > 2]
    overlap = sum(1 for w in s_words if w in q_words)
    return overlap > len(s_words) * 0.6


def generate_suggestions(query: str, context_chunks: list[Chunk]) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    used: set[str] = set()
    all_text = f"{query} {' '.join(c['title'] + ' ' + c['content'] for c in context_chunks)}"

    for topic, regex, ignore in _PATTERNS:
        if _matches(regex, ignore, all_text) and topic in TOPIC_SUGGESTIONS:
            for s in TOPIC_SUGGESTIONS[topic]:
                if s["question"] not in used and len(suggestions) < 3:
                    if not _is_too_similar(query, s["question"]):
                        suggestions.append(dict(s))
                        used.add(s["question"])
        if len(suggestions) >= 3:
            break

    if not suggestions:
        suggestions.extend(dict(s) for s in GENERIC_SUGGESTIONS)
    return suggestions[:3]
