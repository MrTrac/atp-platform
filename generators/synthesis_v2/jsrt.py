"""The few JavaScript runtime behaviours the AOKP synthesis code relies on, reproduced exactly.

The port must give the same answer as `src/runtime/synthesis/*.ts` for the same input, including the odd cases. Python and JavaScript disagree on small things that matter here;
each helper below names the disagreement it removes. Everything is standard library (ATP has no runtime dependencies, ADR-0001).

  js_trim / JS_WS      `String.prototype.trim` and the `\\s` class: they include U+FEFF and U+00A0..., and exclude U+001C-U+001F (Python's `str.strip()` is the other way round).
  to_fixed3            `Number(x.toFixed(3))`: an exact binary tie rounds HALF UP (0.0625 -> 0.063); Python `round` is half-even (0.062).
  utf16_len            `String.length` counts UTF-16 code units: an astral letter is 2, so a 2-letter astral token has length 4. js_slice_utf16: `slice(0, n)` counts the same way.
  js_truthy            `Boolean(v)`: `[]` and `{}` are TRUE in JavaScript, false in Python.
  js_number            `Number(v)`: `"0x10"` is 16, `" 7 "` is 7, `[5]` is 5, `""` is 0, `"abc"` is NaN.
  js_string            `String(v)`: `1e21` prints as `1e+21`, `[1,[2,null]]` as `1,2,`, an object as `[object Object]`.
  js_canon_upper       what a non-unicode `/.../i` regex does to a character before comparing (used to emulate the `i` flag without Python's wider Unicode folding).
  load_json            `JSON.parse`: NaN / Infinity / -Infinity are errors (Python's `json` accepts them).
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

# ECMAScript WhiteSpace + LineTerminator: what `\s` matches and what `trim()` strips.
JS_WS = "\t\n\x0b\x0c\r                  　﻿"
JS_WS_SET = frozenset(JS_WS)
JS_WS_CLASS = "[" + "".join(sorted(JS_WS_SET)).replace("\\", "\\\\").replace("]", "\\]").replace("^", "\\^").replace("-", "\\-") + "]"
_WS_SPLIT = re.compile(JS_WS_CLASS + "+")


def js_trim(s: str) -> str:
    return s.strip(JS_WS)


def js_split_ws(s: str) -> list[str]:
    """`s.split(/\\s+/)`: a leading/trailing run of whitespace yields an empty first/last element, exactly like JavaScript."""
    return _WS_SPLIT.split(s)


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def js_slice_utf16(s: str, n: int) -> str:
    """`s.slice(0, n)`: n counts UTF-16 code units, so an astral character on the boundary is cut in two (leaving a lone surrogate), exactly like JavaScript."""
    return s.encode("utf-16-le", "surrogatepass")[: 2 * n].decode("utf-16-le", "surrogatepass")


def to_fixed3(x: float) -> float:
    """`Number(x.toFixed(3))` for 0 <= x < 1e21: the integer n closest to x*1000, the LARGER one on an exact tie, computed on the exact binary value."""
    if math.isnan(x) or math.isinf(x):
        return x
    return float(Decimal(x).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def js_truthy(v: Any) -> bool:
    if v is None or v is False:
        return False
    if v is True:
        return True
    if isinstance(v, (int, float)):
        return not (v == 0 or (isinstance(v, float) and math.isnan(v)))
    if isinstance(v, str):
        return len(v) > 0
    return True  # list, dict: objects are always truthy in JavaScript


_DEC = re.compile(r"[+-]?(?:[0-9]+\.?[0-9]*(?:[eE][+-]?[0-9]+)?|\.[0-9]+(?:[eE][+-]?[0-9]+)?)")


def _string_to_number(s: str) -> float:
    t = js_trim(s)
    if t == "":
        return 0.0
    low = t.lower()
    for prefix, base in (("0x", 16), ("0b", 2), ("0o", 8)):
        if low.startswith(prefix):
            body = t[2:]
            if body and all(c in "0123456789abcdefABCDEF"[: base if base <= 10 else 22] for c in body):
                try:
                    return float(int(body, base))
                except ValueError:
                    return math.nan
            return math.nan
    if t in ("Infinity", "+Infinity"):
        return math.inf
    if t == "-Infinity":
        return -math.inf
    if _DEC.fullmatch(t):
        try:
            return float(t)
        except (ValueError, OverflowError):
            return math.nan
    return math.nan


def js_number(v: Any) -> float:
    """`Number(v)` for values that come out of `JSON.parse`."""
    if v is None:
        return 0.0
    if v is True:
        return 1.0
    if v is False:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        return _string_to_number(v)
    if isinstance(v, list):
        return _string_to_number(js_string(v))
    return math.nan  # a plain object stringifies to "[object Object]"


def _number_to_string(x: float) -> str:
    """ECMAScript Number::toString (radix 10)."""
    if math.isnan(x):
        return "NaN"
    if x == 0:
        return "0"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    sign = "-" if x < 0 else ""
    d = Decimal(repr(abs(x))).normalize()
    digits = "".join(str(i) for i in d.as_tuple().digits)
    k = len(digits)
    n = k + d.as_tuple().exponent  # value = 0.<digits> * 10**n
    if k <= n <= 21:
        return sign + digits + "0" * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits
    e = n - 1
    es = ("+" if e >= 0 else "-") + str(abs(e))
    return sign + (digits[0] if k == 1 else digits[0] + "." + digits[1:]) + "e" + es


def js_string(v: Any) -> str:
    """`String(v)` for values that come out of `JSON.parse` (JSON numbers are doubles in JavaScript, so an int is converted first)."""
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, str):
        return v
    if isinstance(v, (int, float)):
        try:
            return _number_to_string(float(v))
        except OverflowError:
            return "Infinity" if v > 0 else "-Infinity"
    if isinstance(v, list):
        return ",".join("" if x is None else js_string(x) for x in v)
    return "[object Object]"


def js_canon_upper(s: str) -> str:
    """Per-character `Canonicalize` of a non-unicode case-insensitive regex: upper-case it, unless that is several characters, or turns a non-ASCII character into an ASCII one."""
    out = []
    for ch in s:
        if ord(ch) > 0xFFFF:
            out.append(ch)  # a surrogate pair in JavaScript: each half maps to itself
            continue
        u = ch.upper()
        out.append(ch if len(u) != 1 or (ord(ch) >= 128 and ord(u) < 128) else u)
    return "".join(out)


def _reject_constant(name: str) -> Any:
    raise ValueError(f"JSON.parse does not accept {name}")


def load_json(text: str) -> Any:
    """`JSON.parse(text)`: raises on anything JavaScript rejects. Python's loader additionally accepts the bare constants NaN / Infinity / -Infinity, which are removed here."""
    return json.loads(text, parse_constant=_reject_constant)


def is_letter_or_number(ch: str) -> bool:
    """`/[\\p{L}\\p{N}]/u` for one code point."""
    return unicodedata.category(ch)[0] in ("L", "N")
