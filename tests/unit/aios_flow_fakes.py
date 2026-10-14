"""Test kit for the aios-flow adapter and its identity token provider: a scripted fake network, JWTs shaped like aios-identity's, a manual clock.

`FakeNet` replaces `urlopen` in BOTH modules. Calls are routed by (method, path) and answered from a script; every request is recorded with ALL its headers
(`req.headers` plus the unredirected ones, which is where the Authorization header lives) and the timeout it asked for, and every HTTPError it raises has a tracked
response buffer, so a test can assert that nothing was left open (`net.assert_all_closed()`). The raised HTTPError objects are KEPT ALIVE by the net: CPython closes an
HTTPError's response itself when the object is freed, which would make a missing `close_http_error` invisible (found by an independent review, 14/10/2026).
"""

from __future__ import annotations

import base64
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlsplit

IDENTITY_URL = "https://identity.example/identity"
FLOW_URL = "http://localhost:7700"
SECRET = "s3cret-value-that-must-never-leak-0123"
TOKEN_PATH = "/identity/service-account/token"


def make_jwt(*, lifetime: int = 3600, iat: int = 1_800_000_000, serial: int = 0, sub: str = "svc:atp") -> str:
    """A token shaped like identity's: header.payload.signature, base64url, claims iss/sub/sid/consumer/iat/exp/jti. The signature is junk (nobody verifies it here)."""

    def seg(obj: Any) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")

    claims = {"iss": "aios-identity", "sub": sub, "sid": f"sess-{serial}", "consumer": "ATP", "iat": iat, "exp": iat + lifetime, "jti": f"jti-{serial}"}
    return f"{seg({'alg': 'EdDSA', 'typ': 'JWT'})}.{seg(claims)}.c2lnbmF0dXJl{serial}"


def mint_answer(token: str, *, expires_in: int = 31_536_000) -> dict[str, Any]:
    """What POST /service-account/token answers: `expires_in` advertises a year whatever the JWT's own exp says (measured on identity 1.2.4)."""
    return {"access_token": token, "expires_in": expires_in, "token_type": "Bearer", "session_id": "sess"}


@dataclass
class Http:
    """A scripted HTTP error answer."""

    code: int
    body: Any = None  # dict -> JSON, bytes -> as is, None -> empty
    headers: dict[str, str] = field(default_factory=dict)


def flow_error(code: int, error: str, message: str = "", headers: dict[str, str] | None = None) -> Http:
    """aios-flow's error shape."""
    return Http(code, {"detail": {"error": error, "message": message}}, dict(headers or {}))


def identity_error(code: int, error: str, message: str = "") -> Http:
    """aios-identity's error shape."""
    return Http(code, {"error": error, "message": message})


@dataclass
class Call:
    method: str
    url: str
    path: str
    headers: dict[str, str]  # lower-cased names; request headers AND unredirected headers
    body: Any
    timeout: float | None = None


class _Response:
    def __init__(self, body: Any) -> None:
        self._raw = body if isinstance(body, bytes) else json.dumps(body).encode()

    def read(self, *_a: Any) -> bytes:
        return self._raw

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_a: Any) -> bool:
        return False


class FakeNet:
    """`urlopen` stand-in. `net.on("POST", "/api/runs", {...}, Http(503...), URLError(...))` queues answers for that route, consumed in order; a call with an empty
    queue is a test failure (an unexpected extra request is exactly what several of these tests exist to catch)."""

    def __init__(self) -> None:
        self._script: dict[tuple[str, str], deque[Any]] = defaultdict(deque)
        self.calls: list[Call] = []
        self._buffers: list[BytesIO] = []
        self._errors: list[HTTPError] = []  # keep-alive, see the module docstring

    def on(self, method: str, path: str, *answers: Any) -> "FakeNet":
        self._script[(method, path)].extend(answers)
        return self

    def __call__(self, req: Any, timeout: float | None = None) -> Any:
        parts = urlsplit(req.full_url)
        headers = {k.lower(): v for k, v in {**req.headers, **req.unredirected_hdrs}.items()}
        raw = req.data
        body = json.loads(raw) if raw else None
        self.calls.append(Call(req.get_method(), req.full_url, parts.path, headers, body, timeout))
        queue = self._script[(req.get_method(), parts.path)]
        if not queue:
            raise AssertionError(f"unscripted request: {req.get_method()} {req.full_url}")
        answer = queue.popleft()
        if isinstance(answer, Http):
            raw_body = answer.body if isinstance(answer.body, bytes) else (b"" if answer.body is None else json.dumps(answer.body).encode())
            buf = BytesIO(raw_body)
            self._buffers.append(buf)
            error = HTTPError(req.full_url, answer.code, "scripted", answer.headers, buf)
            self._errors.append(error)
            raise error
        if isinstance(answer, BaseException):
            raise answer
        return _Response(answer)

    # -- inspection ------------------------------------------------------------------------------------------------------------------------------------

    def calls_to(self, method: str, path: str) -> list[Call]:
        return [c for c in self.calls if c.method == method and c.path == path]

    @property
    def flow_calls(self) -> list[Call]:
        return [c for c in self.calls if not c.path.endswith("/service-account/token")]

    @property
    def mint_calls(self) -> list[Call]:
        return [c for c in self.calls if c.path.endswith("/service-account/token")]

    def assert_all_closed(self) -> None:
        open_ = [i for i, b in enumerate(self._buffers) if not b.closed]
        assert not open_, f"{len(open_)} of {len(self._buffers)} HTTPError responses were left open (error #{open_})"

    @property
    def errors_raised(self) -> int:
        return len(self._buffers)

    def leftover(self) -> dict[tuple[str, str], int]:
        return {k: len(v) for k, v in self._script.items() if v}


class Clock:
    """A manual monotonic clock."""

    def __init__(self, start: float = 1000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds
