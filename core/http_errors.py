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

from urllib.error import HTTPError


def close_http_error(exc: BaseException | None) -> None:
    """Close the open response of `exc` if it is an HTTPError; do nothing for any other exception. Never raises: this runs on an error path."""
    if isinstance(exc, HTTPError):
        try:
            exc.close()
        except OSError:
            pass
