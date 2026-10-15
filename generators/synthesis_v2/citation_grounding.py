"""Port of AOKP `src/runtime/synthesis/citation-grounding.ts`: does the sentence around each `[n]` share enough words with the chunk it cites?

Token-overlap Jaccard on normalised words, no external dependency. The odd parts are reproduced on purpose (the golden vectors pin them):
  * the text is decomposed (NFKD) before the non-letter filter, and combining marks are not letters, so a Vietnamese word is cut into fragments at its diacritics;
  * a token must be longer than 2 UTF-16 code units (an astral letter counts 2);
  * `supportScore` and `averageScore` are rounded with JavaScript's `toFixed(3)` (exact ties round up).
"""

from __future__ import annotations

import unicodedata
from typing import Any

from ._data import GROUNDED_AT, STOPWORDS, WEAK_AT
from .jsrt import JS_WS_SET, is_letter_or_number, js_split_ws, js_trim, to_fixed3, utf16_len

Chunk = dict[str, Any]
Citation = dict[str, Any]
GroundingReport = dict[str, Any]


def tokenize(text: str) -> set[str]:
    folded = unicodedata.normalize("NFKD", text.lower())
    cleaned = "".join(ch if (is_letter_or_number(ch) or ch in JS_WS_SET) else " " for ch in folded)
    return {t for t in js_split_ws(cleaned) if utf16_len(t) > 2 and t not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a) + len(b) - inter
    return 0.0 if union == 0 else inter / union


def extract_claim_around(answer: str, citation_index: int) -> str:
    marker = f"[{citation_index}]"
    pos = answer.find(marker)
    if pos < 0:
        return ""
    upto = pos + 1  # `lastIndexOf(x, pos)` finds a match that STARTS at or before pos
    start = max(answer.rfind(".", 0, upto), answer.rfind("!", 0, upto), answer.rfind("?", 0, upto), answer.rfind("\n", 0, upto))
    end = pos + len(marker)
    return js_trim(answer[start + 1:end])


def verdict_for(score: float) -> str:
    if score >= GROUNDED_AT:
        return "grounded"
    if score >= WEAK_AT:
        return "weak"
    return "unsupported"


def verify_citation_grounding(answer: str, citations: list[Citation], chunks: list[Chunk]) -> GroundingReport:
    chunk_by_id = {c["artifactId"]: c for c in chunks}  # a later chunk with the same id wins, like `new Map(...)`
    per_citation: list[dict[str, Any]] = []
    for citation in citations:
        chunk = chunk_by_id.get(citation["artifactId"])
        claim = extract_claim_around(answer, citation["index"])
        if chunk is None or not claim:
            per_citation.append({"citationIndex": citation["index"], "artifactId": citation["artifactId"], "claimSnippet": claim, "supportScore": 0, "verdict": "unsupported"})
            continue
        score = jaccard(tokenize(claim), tokenize(chunk["content"]))
        per_citation.append({"citationIndex": citation["index"], "artifactId": citation["artifactId"], "claimSnippet": claim,
                             "supportScore": to_fixed3(score), "verdict": verdict_for(score)})

    # `reduce((sum, c) => sum + c.supportScore, 0)`: add one by one in order. Python's `sum()` of floats is compensated since 3.12 (not on 3.11), so it would give a different
    # last bit than JavaScript — enough to flip `average < 0.08` — and a different answer on the two Python versions CI runs.
    total = 0.0
    for c in per_citation:
        total += c["supportScore"]
    average = 0.0 if not per_citation else total / len(per_citation)
    unsupported = sum(1 for c in per_citation if c["verdict"] == "unsupported")
    weak = sum(1 for c in per_citation if c["verdict"] == "weak")

    overall = "grounded"  # no citations at all: vacuously grounded
    if per_citation:
        if unsupported > 0 or average < WEAK_AT:
            overall = "unsupported"
        elif weak > 0 or average < GROUNDED_AT:
            overall = "weak"
    return {"overall": overall, "averageScore": to_fixed3(average), "perCitation": per_citation, "unsupportedCount": unsupported}
