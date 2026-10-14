"""core/http_errors.py — reading what an error answer says (`read_error_body`, `error_code_and_message`), used by the aios-flow adapter and its identity token provider."""

from __future__ import annotations

import http.client
import socket
import ssl
from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from core.http_errors import close_http_error, error_code_and_message, network_reason, read_error_body

_created: list[HTTPError] = []


def _error(body: bytes | None, code: int = 400) -> HTTPError:
    exc = HTTPError("http://x", code, "Err", {}, None if body is None else BytesIO(body))
    _created.append(exc)
    return exc


@pytest.fixture(autouse=True)
def _close_what_the_tests_open():
    """An HTTPError owns its response until it is closed: these tests make their own, so they close them (the repo runs with ResourceWarning promoted to an error)."""
    yield
    while _created:
        close_http_error(_created.pop())


def test_the_body_is_read_up_to_the_limit():
    assert read_error_body(_error(b"x" * 10_000), limit=4096) == b"x" * 4096
    assert read_error_body(_error(b'{"a": 1}')) == b'{"a": 1}'


@pytest.mark.parametrize("exc", [None, URLError("refused"), OSError("x"), ValueError("v")])
def test_anything_that_is_not_an_http_error_reads_as_empty(exc):
    assert read_error_body(exc) == b""


def test_an_error_without_a_body_reads_as_empty():
    assert read_error_body(_error(None)) == b""


def test_a_closed_error_reads_as_empty_instead_of_raising():
    exc = _error(b'{"a": 1}')
    close_http_error(exc)
    assert read_error_body(exc) == b""  # why the body has to be read BEFORE the close


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (b'{"detail": {"error": "identity_unavailable", "message": "identity unreachable"}}', ("identity_unavailable", "identity unreachable")),  # aios-flow
        (b'{"error": "invalid_service_credentials", "message": "invalid credentials"}', ("invalid_service_credentials", "invalid credentials")),  # aios-identity
        (b'{"detail": "Not Found"}', (None, "Not Found")),  # FastAPI's plain HTTPException
        (b'{"detail": [{"loc": ["body"], "msg": "field required"}]}', (None, "field required")),  # pydantic 422
        (b'{"detail": {"error": "flow_not_found"}}', ("flow_not_found", None)),
        (b'{"detail": {"message": "no code"}}', (None, "no code")),
        (b'{"detail": []}', (None, None)),
        (b'{"detail": 7}', (None, None)),
        (b"<html><body>502 Bad Gateway</body></html>", (None, None)),
        (b"", (None, None)),
        (b"[1, 2]", (None, None)),
        (b"null", (None, None)),
        (b"\xff\xfe\x00", (None, None)),
    ],
)
def test_code_and_message_in_either_house_format(body, expected):
    assert error_code_and_message(body) == expected


def test_a_code_that_is_not_an_identifier_is_dropped():
    assert error_code_and_message(b'{"error": "has space", "message": "m"}') == (None, "m")
    assert error_code_and_message(b'{"error": "x\\ny", "message": "m"}') == (None, "m")
    assert error_code_and_message(('{"error": "' + "a" * 65 + '"}').encode()) == (None, None)
    assert error_code_and_message(('{"error": "' + "a" * 64 + '"}').encode()) == ("a" * 64, None)


def test_a_message_is_flattened_and_cut():
    code, message = error_code_and_message(b'{"error": "e", "message": "line one\\n\\tline   two\\r\\nline three"}')
    assert (code, message) == ("e", "line one line two line three")
    _code, long = error_code_and_message(('{"error": "e", "message": "' + "w" * 5000 + '"}').encode())
    assert long == "w" * 200


# -- the helpers run on an error path: they must not raise ------------------------------------------------------------------------------------------------


def test_a_body_cut_off_mid_chunk_reads_as_empty_instead_of_raising_incomplete_read():
    """Measured on 3.11, 3.12 and 3.14: a chunked error body that ends early raised http.client.IncompleteRead out of the helper, past the close."""
    exc = _error(b"x")
    exc.read = lambda *_a: (_ for _ in ()).throw(http.client.IncompleteRead(b"par", 10))  # type: ignore[method-assign]
    assert read_error_body(exc) == b""


def test_a_body_of_deeply_nested_brackets_is_not_a_crash():
    """Python 3.11 raises RecursionError for ~1000 nested brackets, which fit in the 4 KiB the adapter reads."""
    assert error_code_and_message(b"[" * 4000) == (None, None)
    assert error_code_and_message(b'{"a":' * 2000 + b"1" + b"}" * 2000) == (None, None)


def test_network_reason_unwraps_a_url_error_and_returns_an_ssl_error_whole():
    refused = ConnectionRefusedError(61, "Connection refused")
    assert network_reason(URLError(refused)) is refused
    assert network_reason(refused) is refused
    gai = socket.gaierror(8, "no such host")
    assert network_reason(URLError(gai)) is gai
    cert = ssl.SSLCertVerificationError(1, "certificate verify failed")
    cert.reason = "CERTIFICATE_VERIFY_FAILED"  # real ones carry this code string (set by the ssl module); it is why the error is returned whole
    assert network_reason(cert) is cert
    assert network_reason(URLError(cert)) is cert
