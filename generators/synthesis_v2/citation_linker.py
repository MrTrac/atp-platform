"""Port of AOKP `src/runtime/synthesis/citation-linker.ts`: number the context chunks for the prompt, and read back which `[n]` the answer used.

Data shapes are AOKP's own (camelCase dict keys: `artifactId`, `title`, `content`, `sourcePointer`) so that the golden vectors produced from the TypeScript compare directly;
`generators/stubs/report_v2.py` converts ATP's chunk shape at the boundary.
"""

from __future__ import annotations

import re
from typing import Any

Chunk = dict[str, Any]
Citation = dict[str, Any]

_MARKER = re.compile(r"\[([0-9]+)\]")  # JavaScript `\d` is ASCII-only


def format_context_with_citations(chunks: list[Chunk]) -> tuple[str, dict[int, Citation]]:
    citation_map: dict[int, Citation] = {}
    lines: list[str] = []
    for i, chunk in enumerate(chunks):
        idx = i + 1
        citation: Citation = {"index": idx, "artifactId": chunk["artifactId"], "title": chunk["title"]}
        if "sourcePointer" in chunk:  # `sourcePointer: chunk.sourcePointer` is `undefined` (and absent from JSON) when the chunk has none
            citation["sourcePointer"] = chunk["sourcePointer"]
        citation_map[idx] = citation
        lines.append(f"[{idx}] {chunk['title']}\n{chunk['content']}")
    return "\n\n".join(lines), citation_map


def extract_used_citations(answer: str, citation_map: dict[int, Citation]) -> list[Citation]:
    used: set[int] = set()
    for m in _MARKER.finditer(answer):
        idx = int(m.group(1))
        if idx in citation_map:
            used.add(idx)
    return [citation_map[i] for i in sorted(used)]
