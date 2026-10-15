#!/usr/bin/env python3
"""Generate the two DATA modules of the synthesis_v2 port from golden.json.gz (which was produced from the real AOKP source by run_golden.sh).

    generators/synthesis_v2/_data.py          topic suggestions, topic-pattern sources (JS regex source + flags), generic suggestions, stopwords, thresholds
    generators/prompts/synthesis_bank.py      the three bilingual prompt templates (verbatim) + render_prompt()

Nothing here is typed by hand: the prompt texts and the constants were read out of AOKP's TypeScript, so a transcription typo is impossible by construction; the golden test
additionally pins their sha256. Re-run after run_golden.sh if AOKP's text changes:   python3 gen_python_data.py
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
g = json.load(gzip.open(HERE / "golden.json.gz", "rt", encoding="utf-8"))
COMMIT = g["aokp_commit"]


def lit(s: str) -> str:
    """A readable Python literal for any string: one source line per text line (implicit concatenation), non-ASCII kept as is."""
    lines = s.split("\n")
    parts = [json.dumps(line + ("\n" if i < len(lines) - 1 else ""), ensure_ascii=False) for i, line in enumerate(lines)]
    for p in parts:  # json.dumps output is a valid Python literal except for these two (never present in AOKP's text; fail loudly if they ever are)
        assert " " not in p and " " not in p
    return parts[0] if len(parts) == 1 else "(\n        " + "\n        ".join(parts) + "\n    )"


def dump(obj, indent: int = 0) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=4).replace("\n", "\n" + " " * indent)


c = g["constants"]
data = f'''"""Constants of AOKP `synthesis/suggestion-engine.ts` and `synthesis/citation-grounding.ts` — GENERATED, do not edit.

Source: AOKP commit {COMMIT}, read out of the TypeScript by tests/fixtures/synthesis_v2/make_golden.ts and written here by gen_python_data.py.
"""

from __future__ import annotations

# topic -> follow-up suggestions (Vietnamese text as in AOKP)
TOPIC_SUGGESTIONS: dict[str, list[dict[str, str]]] = {dump(c["topic_suggestions"])}

# (topic, JavaScript regex SOURCE, JavaScript flags) in AOKP's order; compiled with JS semantics by suggestion_engine.py
TOPIC_PATTERN_SOURCES: list[tuple[str, str, str]] = [
{chr(10).join("    (" + json.dumps(x["topic"]) + ", " + json.dumps(x["source"], ensure_ascii=False) + ", " + json.dumps(x["flags"]) + ")," for x in c["topic_patterns"])}
]

GENERIC_SUGGESTIONS: list[dict[str, str]] = {dump(c["generic_suggestions"])}

# NOTE: these are NFC strings, but the grounding tokenizer decomposes text (NFKD) before comparing, so the Vietnamese ones never match a token. AOKP behaves the same; kept as is.
STOPWORDS: frozenset[str] = frozenset({dump(c["stopwords"])})

GROUNDED_AT: float = {c["thresholds"]["grounded"]!r}
WEAK_AT: float = {c["thresholds"]["weak"]!r}
'''
(ROOT / "generators/synthesis_v2").mkdir(parents=True, exist_ok=True)
(ROOT / "generators/synthesis_v2/_data.py").write_text(data, encoding="utf-8")

bank = [f'"""Bilingual prompt bank — verbatim copy of AOKP `src/runtime/locale/prompt-bank.ts` — GENERATED, do not edit.\n\nSource: AOKP commit {COMMIT}. The texts were read out of the TypeScript, not retyped;\n`tests/unit/test_synthesis_v2_golden.py` pins their sha256 against AOKP.\n"""\n\nfrom __future__ import annotations\n']
for name, tpl in g["prompts"].items():
    bank.append(f"{name}: dict[str, str] = {{\n    \"vi\": {lit(tpl['vi'])},\n    \"en\": {lit(tpl['en'])},\n}}\n")
bank.append('''

def _substitute(replacement: str, matched: str, before: str, after: str) -> str:
    """ECMAScript GetSubstitution for a STRING pattern (no captures): `$$` -> `$`, `$&` -> the match, `$`` -> text before, `$'` -> text after; anything else stays literal."""
    out: list[str] = []
    i = 0
    while i < len(replacement):
        ch = replacement[i]
        if ch == "$" and i + 1 < len(replacement):
            nxt = replacement[i + 1]
            if nxt == "$":
                out.append("$")
                i += 2
                continue
            if nxt == "&":
                out.append(matched)
                i += 2
                continue
            if nxt == "`":
                out.append(before)
                i += 2
                continue
            if nxt == "'":
                out.append(after)
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def js_replace_all(text: str, search: str, replacement: str) -> str:
    """`String.prototype.replaceAll(search, replacement)` with two strings. Unlike `str.replace`, `$` sequences in the replacement are special (AOKP passes user text through it)."""
    if search == "":
        raise ValueError("empty search is not used by the prompt bank")
    out: list[str] = []
    pos = 0
    while True:
        k = text.find(search, pos)
        if k < 0:
            break
        out.append(text[pos:k])
        out.append(_substitute(replacement, search, text[:k], text[k + len(search):]))
        pos = k + len(search)
    out.append(text[pos:])
    return "".join(out)


def render_prompt(template: dict[str, str], locale: str, variables: dict[str, str] | None = None) -> str:
    """AOKP `renderPrompt`: pick the locale, then replace `{key}` for each variable IN ORDER (a value that contains a later `{key}` is substituted again, as in AOKP)."""
    text = template[locale]
    if variables:
        for key, value in variables.items():
            text = js_replace_all(text, "{" + key + "}", value)
    return text
''')
(ROOT / "generators/prompts").mkdir(parents=True, exist_ok=True)
(ROOT / "generators/prompts/synthesis_bank.py").write_text("\n".join(bank), encoding="utf-8")
(ROOT / "generators/prompts/__init__.py").write_text('"""Prompt banks used by the ATP synthesis generators."""\n', encoding="utf-8")
print("wrote _data.py and synthesis_bank.py from AOKP", COMMIT[:10])
