"""Close the response an `urllib.error.HTTPError` still holds open (KD-ATP-012).

`urlopen` raises HTTPError for every non-2xx answer, and that exception object IS the response: it owns the open socket / file until `close()` is called or it is
garbage-collected. `with urlopen(...) as resp:` closes successful responses, but a handler that catches the error, reads (or ignores) the body and moves on leaves the
close to the garbage collector. CPython usually does that at once, which is why nothing ever failed; but it is a hidden dependency on refcounting (`ResourceWarning:
Implicitly cleaning up <HTTPError ...>` is what it looks like when it is made visible) and it does not hold on other interpreters or when the error sits in a reference cycle.

HTTPError subclasses URLError, which subclasses OSError, so `except URLError` / `except OSError` handlers receive it too: every handler around a network call that can see an
HTTPError calls this once it has read what it needs from the error (the attributes `code`, `reason` and `str(exc)` stay valid after the close; `read()` does not).
`tests/unit/test_http_errors_closed.py` fails when a new handler in a network-facing module forgets to.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError

_CODE = re.compile(r"[A-Za-z0-9_.:-]{1,64}")
_MESSAGE_LIMIT = 200


def close_http_error(exc: BaseException | None) -> None:
    """Close the open response of `exc` if it is an HTTPError; do nothing for any other exception. Never raises: this runs on an error path."""
    if isinstance(exc, HTTPError):
        try:
            exc.close()
        except OSError:
            pass


def read_error_body(exc: BaseException | None, limit: int = 4096) -> bytes:
    """The first `limit` bytes of the body an HTTPError carries; b"" for any other exception or when the body cannot be read. Never raises.

    Call it BEFORE `close_http_error`: a closed response cannot be read (ValueError). `fp=None` errors (tests, some proxies) read as b"".
    """
    if not isinstance(exc, HTTPError):
        return b""
    try:
        return exc.read(limit) or b""
    except (OSError, ValueError, AttributeError):
        return b""


def _flatten(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    flat = " ".join(text.split())[:_MESSAGE_LIMIT]
    return flat or None


def error_code_and_message(body: bytes) -> tuple[str | None, str | None]:
    """`(code, message)` out of an error body, in either house format: aios-flow `{"detail": {"error": <code>, "message": <text>}}` (FastAPI nests it in
    `detail`; a plain-string or pydantic-list `detail` gives a message only) and aios-identity `{"error": <code>, "message": <text>}`.

    The code is kept only if it looks like an identifier; the message is flattened to one line and cut at 200 characters, so what a server sends can be put in
    an error text without carrying control characters or a page of HTML. Anything unparseable -> `(None, None)`. Never raises.
    """
    try:
        data = json.loads(body.decode("utf-8"))
    except ValueError:
        return None, None
    if not isinstance(data, dict):
        return None, None
    detail = data.get("detail", data)
    if isinstance(detail, str):
        return None, _flatten(detail)
    if isinstance(detail, list):
        first = detail[0] if detail else None
        return None, _flatten(first.get("msg") if isinstance(first, dict) else None)
    if not isinstance(detail, dict):
        return None, None
    code = detail.get("error")
    return (code if isinstance(code, str) and _CODE.fullmatch(code) else None), _flatten(detail.get("message"))
