#!/usr/bin/env python3
"""Deterministic INPUTS for the synthesis_v2 golden vectors (KD-ATP-006, Phase 2a).

`make_golden.ts` runs the REAL AOKP TypeScript (src/runtime/synthesis/*) on these inputs and writes `golden.json` (inputs + the outputs AOKP produced). The Python port
in `generators/synthesis_v2/` must reproduce every output; `tests/unit/test_synthesis_v2_golden.py` checks that WITHOUT needing the AOKP checkout (CI has none).

Why hand cases AND a seeded fuzz: the places where JavaScript and Python quietly disagree are not the ones a reviewer thinks of —
  * `Number.toFixed(3)` rounds an exact tie HALF UP (0.0625 -> "0.063"); Python `round` is half-even (-> 0.062). Jaccard ratios like 1/16 are tie values.
  * `String.length` counts UTF-16 units: a token of two astral letters has length 4 in JS and 2 in Python.
  * Vietnamese text is decomposed (NFKD) and the combining marks are NOT letters, so words are cut into fragments; `\\p{L}`/`\\p{N}` must be reproduced by Unicode category.
  * JS `\\b` is ASCII-only (`[A-Za-z0-9_]`): "tủ" is not followed by a boundary the way a Python `\\b` would say; JS `\\s`/`trim()` include U+FEFF and exclude U+001C-001F.
  * `JSON.parse` rejects NaN/Infinity that Python's `json` accepts; JS truthiness of `[]`/`{}` is true, Python's is false; `Number("0x10")` is 16.
Run:  python3 make_inputs.py  ->  inputs.json   (seed fixed; the file is committed).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
RNG = random.Random(20261015)

VI = ["radar", "mạng", "đường truyền", "kết nối", "hệ thống", "giám sát", "cảnh báo", "thiết bị", "nguồn điện", "dữ liệu", "sơ đồ", "tủ rack", "đài kiểm soát",
      "xử lý chuyến bay", "FDP", "Fortigate", "VLAN", "Fortinet", "STCA", "MSAW", "ASTERIX", "MLAT", "ADS-B", "safety net", "TWR", "tower", "remote site", "ip", "IP",
      "network", "firewall", "cyber", "không lưu", "ATSEP", "ATCC", "độ trễ", "băng thông", "lưu lượng", "quản lý", "bảo trì", "cập nhật", "Thales", "Indra"]
EN = ["the", "system", "radar", "network", "link", "failover", "primary", "backup", "traffic", "latency", "alert", "rack", "power", "feed", "site", "tower", "wan",
      "ethernet", "and", "of", "to", "is", "was", "this", "that", "with", "for", "firewall", "signature", "offline"]
PUNCT = [".", "!", "?", "\n", ",", ";", ":", " "]
EXOTIC = [" ", "\t", "\r\n", " ", "﻿", "​", "😀", "𝐀𝐁", "𝐀𝐁𝐂", "ǅ", "İ", "ſ", "K", "ß", "Σ", "ΑΣ", "é", "é", "x̣̂", "①", "²", "٣", "—", "…", "“", "”"]


def words(n: int, pool: list[str], exotic_rate: float = 0.08) -> list[str]:
    out = []
    for _ in range(n):
        out.append(RNG.choice(EXOTIC) if RNG.random() < exotic_rate else RNG.choice(pool))
    return out


def sentence(pool: list[str], n: int | None = None) -> str:
    n = n or RNG.randint(4, 18)
    return " ".join(words(n, pool)) + RNG.choice([".", "!", "?", ".", "."])


def text_block(pool: list[str], sentences: int | None = None) -> str:
    sentences = sentences or RNG.randint(1, 5)
    sep = RNG.choice([" ", "\n", "  ", "\r\n"])
    return sep.join(sentence(pool) for _ in range(sentences))


def chunk(i: int, pool: list[str]) -> dict:
    c = {"artifactId": f"a{RNG.choice([i, i, i, max(1, i - 1)])}", "title": " ".join(words(RNG.randint(1, 5), pool, 0.03)).strip() or f"T{i}", "content": text_block(pool)}
    if RNG.random() < 0.3:
        c["sourcePointer"] = f"p/{i}"
    if RNG.random() < 0.2:
        c["score"] = round(RNG.random(), 3)
    return c


def with_markers(base: str, max_idx: int) -> str:
    """Insert [n] markers after random sentences/words (including n=0 and n beyond the context)."""
    parts = base.split(" ")
    for _ in range(RNG.randint(0, 6)):
        pos = RNG.randint(0, len(parts))
        n = RNG.choice(list(range(1, max_idx + 1)) * 3 + [0, 99, 10, 11])
        parts.insert(pos, f"[{n}]")
    return " ".join(parts)


# ───────────────────────────── grounding / citation helpers ─────────────────────────────
def grounding_cases() -> list[dict]:
    cases: list[dict] = []

    def add(answer: str, chunks: list[dict], name: str = "") -> None:
        cases.append({"name": name, "mode": "pipeline", "answer": answer, "chunks": chunks})

    # Exact Jaccard ties: |inter|/|union| in {1/16, 3/16, 5/16, 7/16, 9/16, 11/16, 13/16, 15/16, 1/8 ...}; JS toFixed(3) rounds a binary-exact tie HALF UP.
    def tie_case(inter: int, union: int, name: str) -> None:
        a = union - (union - inter) // 2  # |A|
        b = union + inter - a             # |B|
        shared = [f"shared{k}" for k in range(inter)]
        only_a = [f"alpha{k}" for k in range(a - inter)]
        only_b = [f"bravo{k}" for k in range(b - inter)]
        claim = " ".join(shared + only_a)
        content = " ".join(shared + only_b)
        add(f"{claim} [1]", [{"artifactId": "t1", "title": "tie", "content": content}], name)

    for inter, union in [(1, 16), (3, 16), (5, 16), (7, 16), (9, 16), (11, 16), (13, 16), (1, 32), (3, 32), (1, 8), (3, 8), (5, 8), (7, 8)]:
        tie_case(inter, union, f"tie {inter}/{union}")

    # sentence boundary, repeated markers, missing marker, missing chunk, duplicate artifact ids
    add("Radar chính mất kết nối. Hệ thống chuyển sang radar dự phòng [1]. Kíp trực xác nhận [2] và ghi nhật ký.",
        [{"artifactId": "r1", "title": "Radar", "content": "Radar chính mất kết nối thì hệ thống chuyển sang radar dự phòng."},
         {"artifactId": "r2", "title": "Nhật ký", "content": "Kíp trực xác nhận và ghi nhật ký vận hành."}], "vi basic")
    add("The primary link fails! Traffic moves to the backup link [1]. Operators confirm [1] it.",
        [{"artifactId": "l1", "title": "Links", "content": "When the primary link fails traffic moves to the backup link and operators confirm."}], "en repeated marker")
    add("No markers at all in this answer.", [{"artifactId": "x", "title": "x", "content": "anything"}], "no markers")
    add("Cited [3] but only two chunks [2] exist [1].", [{"artifactId": "a", "title": "a", "content": "alpha beta gamma"}, {"artifactId": "b", "title": "b", "content": "delta epsilon zeta"}], "marker beyond context")
    add("Same artifact twice [1] and [2].", [{"artifactId": "dup", "title": "one", "content": "first version of the text"}, {"artifactId": "dup", "title": "two", "content": "second different text entirely"}], "duplicate artifact ids")
    add("Câu hỏi?\n[1] đứng đầu dòng. Sau đó [2]!", [{"artifactId": "q", "title": "q", "content": "đứng đầu dòng sau đó"}, {"artifactId": "q2", "title": "q2", "content": "khác hẳn"}], "marker at line start")
    # NFKD + combining marks cut Vietnamese words; astral letters have UTF-16 length 2
    add("đường truyền chuyển sang cáp dự phòng [1]", [{"artifactId": "v", "title": "v", "content": "Đường truyền chuyển sang cáp dự phòng khi mất tín hiệu"}], "vi diacritics fragments")
    add("𝐀𝐁 𝐀𝐁𝐂 𝐃 [1]", [{"artifactId": "m", "title": "m", "content": "𝐀𝐁 𝐀𝐁𝐂 𝐃 và thêm"}], "astral letters utf16 length")
    add("Σίσυφος ΑΣ ſtraße STRASSE İstanbul KELVIN K [1]", [{"artifactId": "u", "title": "u", "content": "σίσυφος ας straße strasse i̇stanbul kelvin k"}], "case mapping")
    add("Numbers ①②③ ² ٣٤٥ 12345 and 4.5 [1]", [{"artifactId": "n", "title": "n", "content": "numbers 12345 and 4 5 ٣٤٥"}], "numeric categories")
    add("a b c nbsp ls　ideo﻿bom [1]", [{"artifactId": "w", "title": "w", "content": "nbsp ls ideo bom"}], "js whitespace set")
    add("x", [], "no chunks")
    add("", [{"artifactId": "e", "title": "e", "content": "empty answer"}], "empty answer")
    add("[1][1][1] only markers", [{"artifactId": "o", "title": "o", "content": "only markers"}], "only markers")
    add("Stopwords the and of là có các và hoặc [1]", [{"artifactId": "s", "title": "s", "content": "the and of là có các"}], "stopwords only")

    # astral LETTERS with no compatibility decomposition: a 2-letter token is 4 UTF-16 units in JavaScript (kept), 2 code points in Python (would be dropped)
    add("𐐨𐐩 𐐨𐐩𐐪 [1]", [{"artifactId": "d", "title": "d", "content": "𐐨𐐩 𐐨𐐩𐐪 và thêm chữ"}], "deseret letters")
    add("𠀀𠀁 𠀂𠀃𠀄 [1]", [{"artifactId": "c", "title": "c", "content": "𠀀𠀁 𠀂𠀃𠀄 khác"}], "cjk ext B")
    add("𐐨 𠀀 [1]", [{"artifactId": "s", "title": "s", "content": "𐐨 𠀀"}], "single astral letters are length 2 (dropped)")

    # exact threshold ratios (verdict uses the UNROUNDED score): 0.18 -> grounded, 0.08 -> weak; just below -> weak / unsupported
    for inter, union in [(9, 50), (2, 25), (17, 100), (7, 100), (4, 50)]:
        tie_case(inter, union, f"threshold {inter}/{union}")

    # many citations whose scores are all exactly 0.08 / 0.18: the float AVERAGE (sequential sum / n) falls below the threshold for n=29 / n=27 (not for n=28 / n=26).
    # Python 3.12 `sum()` is compensated and would not: the port must add one by one like JavaScript's reduce.
    def many(n: int, inter: int, union: int, name: str) -> None:
        a = union - (union - inter) // 2
        b = union + inter - a
        chunks_, parts = [], []
        for k in range(1, n + 1):
            shared = [f"sha{k}x{j}" for j in range(inter)]
            only_a = [f"aaa{k}x{j}" for j in range(a - inter)]
            only_b = [f"bbb{k}x{j}" for j in range(b - inter)]
            chunks_.append({"artifactId": f"m{k}", "title": f"m{k}", "content": " ".join(shared + only_b)})
            parts.append(" ".join(shared + only_a) + f" [{k}].")
        add(" ".join(parts), chunks_, name)
    # sequential float sum / n falls BELOW the threshold for n = 10..14 (0.08) and n = 6..12, 31 (0.18); n = 27..29 / 26..27 only separate a compensated sum() from JavaScript's reduce.
    for n in (10, 11, 12, 13, 14, 27, 28, 29):
        many(n, 2, 25, f"many equal 0.08 x{n}")
    for n in (6, 7, 12, 26, 27, 31):
        many(n, 9, 50, f"many equal 0.18 x{n}")

    # marker order and more than 8 chunks (a Python set of small ints happens to iterate ascending; JavaScript sorts explicitly)
    twelve = [{"artifactId": f"z{k}", "title": f"t{k}", "content": f"contentword{k} shared words here {k}"} for k in range(1, 13)]
    add("Out of order [10] then [2] and [9] plus [11] also [1] and [12].", twelve, "twelve chunks, out-of-order markers")
    forty = [{"artifactId": f"y{k}", "title": f"t{k}", "content": f"alpha{k} beta{k} gamma{k} delta words"} for k in range(1, 41)]
    add("Order [33] first, [1] next, then [40], [2], [17] and [8] last.", forty, "forty chunks, markers out of order (set order differs from sorted)")

    # explicit citations (indices not in the text, artifacts not in the chunks)
    cases.append({"name": "explicit missing chunk", "mode": "explicit", "answer": "Claim one [1]. Claim two [2].",
                  "citations": [{"index": 1, "artifactId": "zz", "title": "z"}, {"index": 2, "artifactId": "k", "title": "k"}],
                  "chunks": [{"artifactId": "k", "title": "k", "content": "claim two content words here"}]})
    cases.append({"name": "explicit index not in text", "mode": "explicit", "answer": "No marker here.",
                  "citations": [{"index": 5, "artifactId": "k", "title": "k"}], "chunks": [{"artifactId": "k", "title": "k", "content": "some words"}]})
    cases.append({"name": "explicit empty list", "mode": "explicit", "answer": "Nothing [1].", "citations": [], "chunks": []})

    for k in range(260):
        pool = RNG.choice([VI, EN, VI + EN])
        n_chunks = RNG.randint(1, 6)
        chunks = [chunk(i, pool) for i in range(1, n_chunks + 1)]
        # answer built from the chunk vocabulary so overlaps are non-trivial
        src = RNG.choice(chunks)["content"].split()
        ans_words = RNG.sample(src, k=min(len(src), RNG.randint(2, 14))) + words(RNG.randint(0, 6), pool)
        RNG.shuffle(ans_words)
        answer = with_markers(" ".join(ans_words) + RNG.choice(PUNCT) + " " + sentence(pool), n_chunks)
        cases.append({"name": f"fuzz {k}", "mode": "pipeline", "answer": answer, "chunks": chunks})
    return cases


def format_extract_cases() -> list[dict]:
    out = []
    for k in range(60):
        pool = RNG.choice([VI, EN])
        chunks = [chunk(i, pool) for i in range(1, RNG.randint(0, 6) + 1)]
        ans = with_markers(text_block(pool), max(1, len(chunks)))
        out.append({"chunks": chunks, "answer": ans})
    out.append({"chunks": [{"artifactId": "a", "title": "T", "content": "C"}], "answer": "[01] [1] [ 1] [1 ] [١] [1][2]"})
    tw = [{"artifactId": f"z{k}", "title": f"t{k}", "content": f"c{k}"} for k in range(1, 13)]
    out.append({"chunks": tw, "answer": "[10][2][9][11][1][12][3] and [10] again"})
    fo = [{"artifactId": f"y{k}", "title": f"t{k}", "content": f"c{k}"} for k in range(1, 41)]
    out.append({"chunks": fo, "answer": "[33] [1] [40] [2] [17] [8] [33]"})
    out.append({"chunks": tw, "answer": "[99999999999999999999] [9007199254740993] [012] [00001]"})
    out.append({"chunks": [], "answer": "[1]"})
    return out


# ───────────────────────────── suggestion engine ─────────────────────────────
def suggestion_cases() -> list[dict]:
    out = []

    def add(query: str, chunks: list[dict] | None = None, name: str = "") -> None:
        out.append({"name": name, "query": query, "chunks": chunks or []})

    add("Radar SMR mất kết nối thì sao?", name="radar")
    add("Cấu hình FDP và STCA", name="two topics")
    add("Quy trình cập nhật signature cho Fortigate", name="firewall")
    # the one suggestion with exactly 10 words longer than 2 units: "Khi radar mất kết nối, hệ thống fallback như thế nào?"; the cut-off is overlap > 0.6 * 10
    add("radar khi mất kết thống fallback", name="overlap exactly 6 of 10 (kept: not > 6.0)")
    add("radar khi mất kết thống fallback như", name="overlap 7 of 10 (too similar)")
    add("radar khi mất kết thống", name="overlap 5 of 10 (kept)")
    add("ſtca alert", name="long s must not match STCA (JS /i)")
    add("ıp network ıp", name="dotless i must not match IP")
    add("rad\u0131ar", name="dotless i inside radar")
    add("STCA ſ", name="stca plus long s")
    add("tủ", name="rack tu alone")
    add("tủx", name="rack tu followed by ascii word char (JS boundary quirk)")
    add("tủ rack RSA01", name="rack real")
    add("RSA12 power feed", name="rack code")
    add("xử lý chuyến bay", name="fdp vi")
    add("XỬ LÝ CHUYẾN BAY", name="fdp vi upper (case-insensitive)")
    add("flight data processing", name="fdp en")
    add("đài kiểm soát TWR", name="twr vi")
    add("đài  kiểm soát", name="twr nbsp")
    add("remote\tsite", name="remote tab")
    add("KELVIN network", name="kelvin sign")
    add("ADSB and ads-b and ADS-B", name="adsb")
    add("mạng", name="network vi alone")
    add("kết nối", name="ket noi")
    add("IP", name="ip upper")
    add("ipv6", name="ipv6 (no boundary)")
    add("Hệ thống này có dependency nào cần lưu ý?", name="too similar to generic")
    add("Radar này sử dụng giao thức ASTERIX category nào", name="too similar to suggestion")
    add("hello world", name="no topic")
    add("", name="empty")
    add("Q", [{"artifactId": "1", "title": "Safety net STCA", "content": "MSAW APW"}], name="topic only in context")
    add("Q", [{"artifactId": "1", "title": "x", "content": "firewall fortinet"}, {"artifactId": "2", "title": "y", "content": "radar psr ssr"}], name="two topics from context")
    for k in range(150):
        pool = RNG.choice([VI, EN, VI + EN])
        q = " ".join(words(RNG.randint(1, 9), pool, 0.05))
        chunks = [chunk(i, pool) for i in range(1, RNG.randint(0, 4) + 1)] if RNG.random() < 0.6 else []
        out.append({"name": f"fuzz {k}", "query": q, "chunks": chunks})
    return out


# ───────────────────────────── structured-response parser ─────────────────────────────
def parse_cases() -> list[dict]:
    out: list[dict] = []

    def add(raw: str, locale: str = "vi", name: str = "") -> None:
        out.append({"name": name, "raw": raw, "locale": locale})

    good = {"sections": [{"heading": "Tóm tắt", "content": "Trả lời [1]."}, {"heading": "Chi tiết", "content": "Phân tích [1][2]."}],
            "suggestions": [{"question": "Hỏi tiếp?", "rationale": "vì sao"}, {"question": "Hỏi nữa?"}], "external_ref_used": False, "kb_gap": None}
    add(json.dumps(good, ensure_ascii=False), name="good")
    add("```json\n" + json.dumps(good, ensure_ascii=False) + "\n```", name="fenced")
    add("Here you go:\n" + json.dumps(good) + "\nThanks", "en", "text around")
    add("{}", name="empty object")
    add('{"sections": []}', name="empty sections")
    add('{"sections": "no"}', name="sections not array")
    add('{"sections": [null, 1, "x", [], {"heading": 1, "content": "c"}, {"heading": "h", "content": 2}, {"heading": "ok", "content": "fine"}]}', name="mixed section items")
    add('{"suggestions": [{"question": "a"}, {"question": "b"}, {"question": "c"}, {"question": "d"}, {"question": "e"}]}', name="more than 3 suggestions")
    add('{"suggestions": [{"question": "q", "rationale": null, "pipeline": ""}, {"question": "r", "rationale": 5, "pipeline": "p"}, {"question": "s", "rationale": [1, [2, null], "x"], "pipeline": 7}, {"question": "t", "rationale": {"a": 1}, "pipeline": true}, {"question": "u", "rationale": 1.5, "pipeline": 0}, {"question": "v", "rationale": 1e21, "pipeline": false}]}', name="rationale/pipeline stringification")
    for k, vals in enumerate([[1.0, 100.0, 1e-7], [1.5e300, 12345678901234567890, 0.000001], [1e21, 123456789.123456789, -1.5], [5e-324, 0.30000000000000004, 4.35],
                              [1e100, 255, 1e5], [-0.0, 1e-6, 1e-5], [123456789012345680000, 1e20, 1e22], [0.1, 0.5, 2.5e-5]]):
        sg = ",".join('{"question": "q%d", "rationale": %s, "pipeline": %s}' % (i, json.dumps(v), json.dumps(v if v else 1.0)) for i, v in enumerate(vals))
        add('{"suggestions": [' + sg + ']}', name=f"number stringification {k}")
    add('{"external_ref_used": "false"}', name="truthy string")
    add('{"external_ref_used": 0}', name="falsy zero")
    add('{"external_ref_used": []}', name="js-truthy empty array")
    add('{"external_ref_used": {}}', name="js-truthy empty object")
    add('{"external_ref_used": null}', name="null flag")
    add('{"external_ref_used": ""}', name="empty string flag")
    add('{"external_ref_used": -0}', name="negative zero flag")
    add('{"kb_gap": "  thiếu bảng  "}', name="kb_gap trim")
    add('{"kb_gap": "\\ufeff x \\ufeff"}', name="kb_gap bom trim")
    add('{"kb_gap": "\\u001cx\\u001f"}', name="kb_gap control chars trim")
    add('{"kb_gap": "   "}', name="kb_gap blank")
    add('{"kb_gap": 5}', name="kb_gap number")
    add('{"kb_gap": null}', name="kb_gap null")
    add('not json at all', name="plain text")
    add('not json {"sections": [{"heading": "h", "content": "c"}]} trailing } brace', name="greedy braces")
    add('{"a": NaN}', name="NaN")
    add('{"a": Infinity, "sections": [{"heading": "h", "content": "c"}]}', name="Infinity")
    add('{"a": -Infinity}', name="-Infinity")
    add('{"a": 1e400, "sections": [{"heading": "h", "content": "c"}]}', name="overflow number")
    add('{"sections": [{"heading": "h", "content": "c"}], "sections": [{"heading": "second", "content": "wins"}]}', name="duplicate keys")
    add('{"sections": [{"heading": "h\\ud800", "content": "lone surrogate"}]}', name="lone surrogate escape")
    add('{"sections": [{"heading": "tab\there", "content": "raw tab in string"}]}', name="raw control char in string")
    add('{"sections": [{"heading": "h", "content": "c"}],}', name="trailing comma")
    add("{'sections': []}", name="single quotes")
    add('{"sections": [{"heading": "h", "content": "c"}]', name="unbalanced")
    add('[1, 2, 3]', name="array top level")
    add('123', name="number top level")
    add('null', name="null top level")
    add('"just a string"', name="string top level")
    add('true', name="true top level")
    add('{"sections": []} ```json {"x": 1} ```', name="two fences")
    add('```json\n{"sections": []}\n``` and more ```json\nxx\n```', "en", "greedy fence strip")
    add('', name="empty raw")
    add('   ', name="blank raw")
    add('{"sections": [{"heading": "Tóm tắt", "content": "bảng\\nxuống dòng\\ttab"}]}', name="escapes in content")
    add('{"sections": [{"heading": "h", "content": "c"}], "suggestions": [{"question": "q"}], "kb_gap": "gap", "external_ref_used": true, "extra": [1, {"deep": [null]}]}', "en", "all fields")
    for k in range(300):
        loc = RNG.choice(["vi", "en"])
        pool = RNG.choice([VI, EN])
        obj: dict = {}
        if RNG.random() < 0.85:
            secs = []
            for _ in range(RNG.randint(0, 4)):
                r = RNG.random()
                if r < 0.7:
                    secs.append({"heading": sentence(pool, 2), "content": text_block(pool, 2)})
                elif r < 0.8:
                    secs.append({"heading": RNG.choice([1, None, True, ["h"]]), "content": "c"})
                elif r < 0.9:
                    secs.append(RNG.choice([None, 3, "str", [], {}]))
                else:
                    secs.append({"heading": "h"})
            obj["sections"] = secs if RNG.random() < 0.95 else RNG.choice(["x", 5, {}, None])
        if RNG.random() < 0.7:
            sg = []
            for _ in range(RNG.randint(0, 5)):
                s = {"question": sentence(pool, 4)}
                if RNG.random() < 0.7:
                    s["rationale"] = RNG.choice([sentence(pool, 3), None, 3, True, [1, 2], {"k": 1}, ""])
                if RNG.random() < 0.4:
                    s["pipeline"] = RNG.choice(["p1", "", 0, 1, None, True, False, [1]])
                sg.append(s if RNG.random() < 0.9 else RNG.choice([{}, {"question": 5}, "q", None]))
            obj["suggestions"] = sg
        if RNG.random() < 0.5:
            obj["external_ref_used"] = RNG.choice([True, False, 0, 1, "", "x", None, [], {}, "false", 0.0, -0.0])
        if RNG.random() < 0.5:
            obj["kb_gap"] = RNG.choice([None, "", "  ", "thiếu tài liệu", 3, "﻿x﻿", "x ", sentence(pool, 6)])
        raw = json.dumps(obj, ensure_ascii=RNG.random() < 0.5)
        r = RNG.random()
        if r < 0.25:
            raw = "```json\n" + raw + "\n```"
        elif r < 0.4:
            raw = sentence(pool, 3) + "\n" + raw + "\n" + sentence(pool, 3)
        elif r < 0.5:
            raw = raw[: RNG.randint(0, len(raw))]
        elif r < 0.55:
            raw = raw.replace('"', "'", 1)
        elif r < 0.6:
            raw = raw.replace("null", "NaN").replace("true", "True")
        out.append({"name": f"fuzz {k}", "raw": raw, "locale": loc})
    return out


# ───────────────────────────── quality guard ─────────────────────────────
def quality_cases() -> list[dict]:
    out: list[dict] = []

    def add(raw: str, name: str = "") -> None:
        out.append({"name": name, "raw": raw, "query": "Q?", "answer": "A.", "locale": "vi"})

    add('{"naturalness": 0.9, "relevance": 0.8, "completeness": 0.7, "raw_extraction": false, "vn_clarity": true, "verdict": "pass"}', "pass")
    add('{"naturalness": 0.2, "relevance": 0.8, "completeness": 0.7, "raw_extraction": true, "vn_clarity": false, "verdict": "retry"}', "retry")
    add('```json\n{"naturalness": 1.5, "relevance": -2, "completeness": "0.5", "raw_extraction": "yes", "verdict": "retry"}\n```', "clamp and strings")
    add('{"naturalness": "abc", "relevance": null, "completeness": [], "raw_extraction": 0, "vn_clarity": 0, "verdict": "PASS"}', "garbage values")
    add('{"naturalness": "0x10", "relevance": " 0.25 ", "completeness": true, "raw_extraction": [], "vn_clarity": null}', "number coercion")
    add('{"naturalness": "1e-1", "relevance": "", "completeness": "Infinity", "raw_extraction": {}, "vn_clarity": false}', "number coercion 2")
    add('{"naturalness": [0.5], "relevance": [1, 2], "completeness": {"a": 1}, "verdict": "retry"}', "array/object numbers")
    add('{"naturalness": 0.9, "verdict": "retry"}', "partial")
    add('not json', "not json")
    add('', "empty")
    add('```JSON\n{"verdict": "retry"}\n```', "upper fence")
    add('```json{"verdict": "retry"}```', "fence no newline")
    add('prefix {"verdict": "retry"} suffix', "text around -> parse error")
    add('[1]', "array")
    add('null', "null")
    add('{"vn_clarity": false}', "vn false")
    add('{"vn_clarity": 0}', "vn zero (not false)")
    add('{"vn_clarity": "false"}', "vn string")
    for k in range(60):
        obj = {}
        for key in ("naturalness", "relevance", "completeness"):
            if RNG.random() < 0.9:
                obj[key] = RNG.choice([round(RNG.random(), 2), 0, 1, 2, -1, "0.4", "x", None, True, False, [], [0.3], {}, "  7 ", "1e2", 1e-7])
        if RNG.random() < 0.8:
            obj["raw_extraction"] = RNG.choice([True, False, 0, 1, "", "x", None, [], {}])
        if RNG.random() < 0.8:
            obj["vn_clarity"] = RNG.choice([True, False, 0, 1, "", "x", None, [], {}])
        if RNG.random() < 0.8:
            obj["verdict"] = RNG.choice(["pass", "retry", "PASS", "", None, 1])
        raw = json.dumps(obj)
        if RNG.random() < 0.2:
            raw = "```json\n" + raw + "\n```"
        out.append({"name": f"fuzz {k}", "raw": raw, "query": "Q?", "answer": "A.", "locale": RNG.choice(["vi", "en"])})
    return out


# ───────────────────────────── end-to-end scenarios (scripted LLM) ─────────────────────────────
def scenarios() -> list[dict]:
    chunks = [
        {"artifactId": "d1", "title": "Radar chính", "content": "Radar chính mất kết nối thì hệ thống chuyển sang radar dự phòng trong vòng 5 giây. Kíp trực xác nhận bằng bảng điều khiển. " * 3, "sourcePointer": "doc1#p3"},
        {"artifactId": "d2", "title": "Nhật ký vận hành", "content": "Ghi nhật ký mọi lần chuyển đổi radar, kèm thời điểm và người xác nhận. " * 4},
        {"artifactId": "d3", "title": "Mạng WAN", "content": "Đường truyền WAN dự phòng qua Fortigate, VLAN 120. " * 3},
    ]
    thin = [{"artifactId": "t1", "title": "Mỏng", "content": "ít"}]
    good = json.dumps({"sections": [{"heading": "Tóm tắt", "content": "Radar dự phòng tiếp quản trong 5 giây [1]."}, {"heading": "Chi tiết", "content": "Kíp trực xác nhận và ghi nhật ký [1][2]."}],
                       "suggestions": [{"question": "Radar dự phòng kết nối thế nào?", "rationale": "hiểu luồng dữ liệu"}], "external_ref_used": False, "kb_gap": None}, ensure_ascii=False)
    good_en = json.dumps({"sections": [{"heading": "Summary", "content": "Backup radar takes over in 5 s [1]."}, {"heading": "Details", "content": "Operators confirm [2]."}],
                          "suggestions": [{"question": "a?", "rationale": "r"}, {"question": "b?", "rationale": "r"}, {"question": "c?", "rationale": "r"}], "external_ref_used": True, "kb_gap": "bảng thiếu"}, ensure_ascii=False)
    q_pass = '{"naturalness": 0.9, "relevance": 0.9, "completeness": 0.8, "raw_extraction": false, "vn_clarity": true, "verdict": "pass"}'
    q_retry = '{"naturalness": 0.4, "relevance": 0.9, "completeness": 0.8, "raw_extraction": true, "vn_clarity": true, "verdict": "retry"}'
    base = {"query": "Radar chính mất kết nối thì sao?", "locale": "vi", "contextChunks": chunks, "sourcePipeline": "p"}
    S = []

    def add(name, request, script, config=None):
        S.append({"name": name, "request": request, "config": config, "script": script})

    add("no context vi", {**base, "contextChunks": []}, [])
    add("no context en", {**base, "locale": "en", "contextChunks": []}, [])
    add("pass first try", base, [{"text": good}, {"text": q_pass}])
    add("retry then pass", base, [{"text": good}, {"text": q_retry}, {"text": good_en}, {"text": q_pass}])
    add("retry exhausted", base, [{"text": good}, {"text": q_retry}, {"text": good}, {"text": q_retry}])
    add("quality null (bad json) retries", base, [{"text": good}, {"text": "xin chào"}, {"text": good}, {"text": q_pass}])
    add("quality llm throws", base, [{"text": good}, {"throw": "boom"}, {"text": good}, {"text": q_pass}])
    add("synthesis throws -> fallback", base, [{"throw": "network down"}])
    add("empty output -> fallback", base, [{"text": "  \n "}])
    add("think-only output -> fallback", base, [{"text": "<think>plan</think>"}])
    add("think tags and blank lines", base, [{"text": "<think>\nreasoning [9]\n</think>\n\n\n" + good + "\n\n"}, {"text": q_pass}])
    add("crlf and unicode blank lines", base, [{"text": "\r\n \r\n" + good.replace("},", "},\r\n")}, {"text": q_pass}])
    add("non-json answer", base, [{"text": "Radar dự phòng tiếp quản [1]. Kíp trực xác nhận [2]."}, {"text": q_pass}])
    add("json with no sections", base, [{"text": '{"suggestions": []}'}, {"text": q_pass}])
    add("english full", {**base, "locale": "en", "query": "What happens when the primary radar link fails?"}, [{"text": good_en}, {"text": q_pass}])
    add("thin context", {**base, "contextChunks": thin}, [{"text": '{"sections": [{"heading": "Tóm tắt", "content": "Chưa đủ."}], "kb_gap": null}'}, {"text": q_pass}])
    add("thin context english", {**base, "contextChunks": thin, "locale": "en"}, [{"text": good_en}, {"text": q_pass}])
    add("history given", {**base, "conversationHistory": "User: hi\nAssistant: hello"}, [{"text": good}, {"text": q_pass}])
    add("quality disabled", base, [{"text": good}], {"maxRetries": 3, "qualityCheckEnabled": False})
    add("maxRetries 0", base, [{"text": good}, {"text": q_retry}], {"maxRetries": 0, "qualityCheckEnabled": True})
    add("maxRetries 2 all retry", base, [{"text": good}, {"text": q_retry}, {"text": good}, {"text": q_retry}, {"text": good}, {"text": q_retry}], {"maxRetries": 2, "qualityCheckEnabled": True})
    en_req = {**base, "locale": "en", "query": "What happens when the primary radar link fails?"}
    add("retry then pass en", en_req, [{"text": good_en}, {"text": q_retry}, {"text": good_en}, {"text": q_pass}])
    add("retry exhausted en", en_req, [{"text": good_en}, {"text": q_retry}, {"text": good_en}, {"text": q_retry}])
    add("synthesis throws en", en_req, [{"throw": "network down"}])
    add("empty output en", en_req, [{"text": "\n"}])
    add("non-json en", en_req, [{"text": "Backup radar takes over [1]. Operators confirm [2]."}, {"text": q_pass}])
    add("no sections en", en_req, [{"text": '{"suggestions": []}'}, {"text": q_pass}])
    add("history en", {**en_req, "conversationHistory": "User: hi"}, [{"text": good_en}, {"text": q_pass}])
    add("non-json with blank lines", base, [{"text": "Dòng 1\n\n\n  \nDòng 2\r\n\r\nDòng 3 [1]"}, {"text": q_pass}])
    add("non-json cr only", base, [{"text": "A\r\r\rB [1]"}, {"text": q_pass}])
    add("non-json unicode line separators", base, [{"text": "A\u2028 \u2028B\u2029\u2029C [2]"}, {"text": q_pass}])
    add("think then blank lines then text", base, [{"text": "<think>x\n\ny</think>\n\n\nA\n\u2028\u2028\nB [2]"}, {"text": q_pass}])
    add("fallback cuts an emoji in half", {**base, "contextChunks": [{"artifactId": "e", "title": "emoji", "content": "a" + "😀" * 150}]}, [{"throw": "down"}])
    add("fallback exactly 200 units", {**base, "contextChunks": [{"artifactId": "f", "title": "f", "content": "x" * 250}, {"artifactId": "g", "title": "g", "content": "y" * 10}]}, [{"throw": "down"}])
    for n in (399, 400, 401):
        add(f"content length {n}", {**base, "contextChunks": [{"artifactId": "l", "title": "l", "content": "x" * n}]}, [{"text": good}, {"text": q_pass}])
    add("content 400 utf16 units as 200 emoji", {**base, "contextChunks": [{"artifactId": "l", "title": "l", "content": "😀" * 200}]}, [{"text": good}, {"text": q_pass}])
    add("content 398 utf16 units as 199 emoji", {**base, "contextChunks": [{"artifactId": "l", "title": "l", "content": "😀" * 199}]}, [{"text": good}, {"text": q_pass}])
    add("exactly two suggestions: no top-up", base, [{"text": json.dumps({"sections": [{"heading": "Tóm tắt", "content": "x [1]"}], "suggestions": [{"question": "Câu một?"}, {"question": "Câu hai?"}]}, ensure_ascii=False)}, {"text": q_pass}])
    add("zero suggestions: topped up to three", base, [{"text": json.dumps({"sections": [{"heading": "Tóm tắt", "content": "x [1]"}], "suggestions": []}, ensure_ascii=False)}, {"text": q_pass}])
    add("suggestions enriched from domain", base, [{"text": json.dumps({"sections": [{"heading": "Tóm tắt", "content": "x [1]"}], "suggestions": [{"question": "Radar này sử dụng giao thức ASTERIX category nào?", "rationale": "dup"}]}, ensure_ascii=False)}, {"text": q_pass}])
    add("citation weak grounding", base, [{"text": json.dumps({"sections": [{"heading": "Tóm tắt", "content": "Hoàn toàn khác chủ đề thời tiết hôm nay đẹp [3]."}]}, ensure_ascii=False)}, {"text": q_pass}])
    add("braces in prompt values", {**base, "query": "{context} {history} {query}", "contextChunks": [{"artifactId": "b", "title": "{query}", "content": "chứa {history} và {query} trong nội dung"}], "conversationHistory": "{query}"}, [{"text": good}, {"text": q_pass}])
    add("dollar signs in values", {**base, "query": "$& $1 $$ price"}, [{"text": good}, {"text": q_pass}])
    return S


# ───────────────────────────── prompt rendering ─────────────────────────────
def render_cases() -> list[dict]:
    out = []
    for tpl, vars_list in [
        ("SYNTHESIS_SYSTEM_PROMPT", [None, {}, {"x": "y"}]),
        ("SYNTHESIS_USER_PROMPT", [{"context": "C", "query": "Q", "history": "H"}, {"context": "{query}", "query": "{history}", "history": "$&"}, {"context": "a", "query": "b"}]),
        ("QUALITY_CHECK_PROMPT", [{"query": "Q?", "answer": "{query}"}, {"query": "Q", "answer": "A"}]),
    ]:
        for loc in ("vi", "en"):
            for v in vars_list:
                out.append({"template": tpl, "locale": loc, "vars": v})
    return out


def main() -> None:
    data = {
        "format": 1,
        "grounding": grounding_cases(),
        "format_extract": format_extract_cases(),
        "suggestions": suggestion_cases(),
        "parse": parse_cases(),
        "quality": quality_cases(),
        "scenarios": scenarios(),
        "render": render_cases(),
    }
    (HERE / "inputs.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print({k: len(v) for k, v in data.items() if isinstance(v, list)})


if __name__ == "__main__":
    main()
