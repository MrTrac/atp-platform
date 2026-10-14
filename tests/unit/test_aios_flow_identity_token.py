"""Unit tests for adapters/aios_flow/identity_token.py — the access token ATP presents to aios-flow.

Facts these tests pin come from MEASUREMENTS against the real aios-identity 1.2.4 (14/10/2026, aios-flow scripts/e2e/real_identity_sandbox.py):
POST /service-account/token answers {"access_token", "expires_in": 31536000, "token_type", "session_id"} while the JWT itself lives 3600 s (`exp - iat`) and the
server enforces the JWT; errors are {"error": <code>, "message": <text>}; 401 invalid_service_credentials / 403 not_service_account / 400 validation_error.
"""

from __future__ import annotations

import threading
from urllib.error import URLError

import pytest
from aios_flow_fakes import (
    IDENTITY_URL,
    SECRET,
    TOKEN_PATH,
    Clock,
    FakeNet,
    identity_error,
    make_jwt,
    mint_answer,
)

from adapters.aios_flow import identity_token
from adapters.aios_flow.identity_token import AuthError, IdentityTokenProvider, IdentityUnavailable


@pytest.fixture
def net(monkeypatch):
    fake = FakeNet()
    monkeypatch.setattr(identity_token, "urlopen", fake)
    return fake


@pytest.fixture
def traces(monkeypatch):
    records: list[dict] = []
    monkeypatch.setattr(identity_token, "record_trace", lambda **kw: records.append(kw))
    return records


@pytest.fixture
def clock():
    return Clock()


def make_provider(clock: Clock, **kw) -> IdentityTokenProvider:
    return IdentityTokenProvider(IDENTITY_URL, SECRET, clock=clock, **kw)


# -- the exchange ------------------------------------------------------------------------------------------------------------------------------------------


def test_the_exchange_request_has_the_shape_identity_expects(net, clock):
    token = make_jwt()
    net.on("POST", TOKEN_PATH, mint_answer(token))
    assert make_provider(clock).get_token() == token
    (call,) = net.mint_calls
    assert call.url == "https://identity.example/identity/service-account/token"
    assert call.body == {"username": "svc:atp", "secret": SECRET, "consumer": "ATP"}
    assert call.headers["content-type"] == "application/json"
    assert "authorization" not in call.headers  # the secret travels in the body; there is no token yet
    assert "x-request-id" in call.headers and "traceparent" in call.headers  # G9: this is a cross-module call


def test_username_and_trailing_slash_are_respected(net, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt()))
    IdentityTokenProvider(IDENTITY_URL + "/", SECRET, username="svc:other", clock=clock).get_token()
    assert net.mint_calls[0].body["username"] == "svc:other"
    assert net.mint_calls[0].path == TOKEN_PATH


def test_a_fresh_token_is_reused(net, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    p = make_provider(clock)
    assert p.get_token() == p.get_token()
    assert len(net.mint_calls) == 1


# -- lifetime: the JWT decides, not `expires_in` -----------------------------------------------------------------------------------------------------------


def test_renewed_at_55_minutes_for_the_3600_s_token_identity_really_issues(net, clock):
    t1, t2 = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(t2))
    p = make_provider(clock)
    assert p.get_token() == t1
    clock.advance(3299)
    assert p.get_token() == t1  # 54 min 59 s: still the first token
    clock.advance(1)
    assert p.get_token() == t2  # 55 min: renewed, 5 minutes before the server stops accepting it
    assert len(net.mint_calls) == 2


def test_the_advertised_expires_in_of_a_year_is_ignored(net, clock):
    """The measured bug: identity says 31536000, the JWT says 3600 and aios-flow's identity enforces the JWT. Trusting the advertised value would keep a dead token."""
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1), expires_in=31_536_000), mint_answer(make_jwt(serial=2), expires_in=31_536_000))
    p = make_provider(clock)
    first = p.get_token()
    clock.advance(3301)
    assert p.get_token() != first


def test_a_tiny_advertised_expires_in_does_not_cause_early_renewal_either(net, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1), expires_in=60))
    p = make_provider(clock)
    first = p.get_token()
    clock.advance(1800)
    assert p.get_token() == first
    assert len(net.mint_calls) == 1


def test_a_longer_real_lifetime_is_honoured_so_an_identity_fix_does_not_cause_hourly_mints(net, clock):
    """Every mint leaves a year-long session row at identity: once the JWT lives longer, renew later, not every 55 minutes."""
    t1 = make_jwt(lifetime=86_400, serial=1)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(make_jwt(lifetime=86_400, serial=2)))
    p = make_provider(clock)
    assert p.get_token() == t1
    clock.advance(3600 * 23)
    assert p.get_token() == t1
    clock.advance(3600 + 1)
    assert p.get_token() != t1


def test_lifetime_is_exp_minus_iat_not_a_comparison_with_this_machines_clock(net, clock):
    """iat 0 / exp 3600 sits 56 years from the manual clock (and a Mac whose clock is minutes off would behave the same): only the difference matters."""
    t1 = make_jwt(iat=0, lifetime=3600, serial=1)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(make_jwt(iat=0, serial=2)))
    p = make_provider(clock)
    assert p.get_token() == t1
    clock.advance(3000)
    assert p.get_token() == t1
    clock.advance(301)
    assert p.get_token() != t1


@pytest.mark.parametrize("token", ["opaque-token-without-dots", "a.b.c", "aaa.e30.ccc", "aaa.W10.ccc", "aaa.eyJleHAiOiAxfQ.ccc"])
def test_a_token_whose_lifetime_cannot_be_read_is_assumed_to_live_3600_s(net, clock, token):
    # e30 = {} ; W10 = [] ; the last one has exp but no iat
    net.on("POST", TOKEN_PATH, mint_answer(token), mint_answer(make_jwt(serial=9)))
    p = make_provider(clock)
    assert p.get_token() == token
    clock.advance(3299)
    assert p.get_token() == token
    clock.advance(2)
    assert p.get_token() != token


def test_the_renewal_margin_shrinks_with_a_very_short_lifetime(net, clock):
    t1 = make_jwt(lifetime=100, serial=1)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(make_jwt(lifetime=100, serial=2)))
    p = make_provider(clock)
    assert p.get_token() == t1
    clock.advance(49)
    assert p.get_token() == t1  # margin = min(300, 100 / 2) = 50
    clock.advance(2)
    assert p.get_token() != t1


# -- one mint at a time ------------------------------------------------------------------------------------------------------------------------------------


def test_threads_share_one_mint(net, monkeypatch, clock):
    started, gate = threading.Event(), threading.Event()

    def slow(req, timeout=None):
        started.set()
        gate.wait(5)
        return net(req, timeout)

    monkeypatch.setattr(identity_token, "urlopen", slow)
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)), mint_answer(make_jwt(serial=2)))
    p = make_provider(clock)
    results: list[str] = []
    threads = [threading.Thread(target=lambda: results.append(p.get_token())) for _ in range(8)]
    for t in threads:
        t.start()
    assert started.wait(5)
    threading.Event().wait(0.2)  # let the other seven reach the lock
    gate.set()
    for t in threads:
        t.join(5)
    assert len(net.mint_calls) == 1
    assert len(results) == 8 and len(set(results)) == 1


# -- a token aios-flow rejected ----------------------------------------------------------------------------------------------------------------------------


def test_a_rejected_token_is_replaced(net, clock):
    t1, t2 = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(t2))
    p = make_provider(clock)
    assert p.get_token() == t1
    clock.advance(31)
    assert p.refresh_after_rejection(t1) == t2
    assert p.get_token() == t2


def test_two_threads_rejected_by_the_same_token_cause_one_mint(net, clock):
    t1, t2 = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(t2))
    p = make_provider(clock)
    p.get_token()
    clock.advance(31)
    assert p.refresh_after_rejection(t1) == t2
    assert p.refresh_after_rejection(t1) == t2  # the second thread arrives with the old token: it gets the new one, no second mint
    assert len(net.mint_calls) == 2


def test_a_token_identity_issued_moments_ago_is_not_replaced_again(net, clock):
    """aios-flow turned down a fresh token: another mint would fail the same way and only add a year-long session row at identity."""
    t1 = make_jwt(serial=1)
    net.on("POST", TOKEN_PATH, mint_answer(t1), mint_answer(make_jwt(serial=2)))
    p = make_provider(clock)
    p.get_token()
    clock.advance(10)
    assert p.refresh_after_rejection(t1) is None
    assert len(net.mint_calls) == 1
    assert p.get_token() == t1  # untouched; it is replaced when it expires or after the cooldown
    clock.advance(21)
    assert p.refresh_after_rejection(t1) is not None


# -- identity says no --------------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("answer", "code", "status"),
    [
        (identity_error(401, "invalid_service_credentials", "invalid credentials"), "invalid_service_credentials", 401),
        (identity_error(403, "not_service_account", "user lacks 'service-account' role"), "not_service_account", 403),
        (identity_error(400, "validation_error", "String must contain at least 16 character(s)"), "validation_error", 400),
    ],
)
def test_refused_credentials_are_an_auth_error_and_are_not_asked_again_for_a_minute(net, clock, answer, code, status):
    net.on("POST", TOKEN_PATH, answer, mint_answer(make_jwt(serial=1)))
    p = make_provider(clock)
    with pytest.raises(AuthError) as first:
        p.get_token()
    assert (first.value.code, first.value.source, first.value.http_status) == (code, "aios-identity", status)
    assert "svc:atp" in str(first.value) and code in str(first.value)
    clock.advance(59)
    with pytest.raises(AuthError) as again:
        p.get_token()
    assert str(again.value) == str(first.value)
    assert len(net.mint_calls) == 1  # the 401 is remembered: identity is not hammered while the secret is wrong
    clock.advance(2)
    assert p.get_token()  # a minute later it tries again (the operator may have fixed the secret) and this time it works
    assert len(net.mint_calls) == 2
    net.assert_all_closed()


def test_a_wrong_url_prefix_gets_a_hint(net, clock):
    net.on("POST", TOKEN_PATH, identity_error(404, "not_found", "no such route"))
    with pytest.raises(AuthError, match="/identity prefix"):
        make_provider(clock).get_token()


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_transient_http_answers_are_unavailable_and_are_not_remembered(net, clock, status):
    net.on("POST", TOKEN_PATH, identity_error(status, "busy", "try later"), mint_answer(make_jwt(serial=1)))
    p = make_provider(clock)
    with pytest.raises(IdentityUnavailable) as err:
        p.get_token()
    assert err.value.http_status == status
    assert isinstance(err.value, URLError)  # core.retry.with_retry retries URLError
    assert p.get_token()  # the very next call goes back to identity
    net.assert_all_closed()


@pytest.mark.parametrize("failure", [URLError("connection refused"), TimeoutError("timed out"), ConnectionResetError("reset by peer")])
def test_network_failures_are_unavailable(net, clock, failure):
    net.on("POST", TOKEN_PATH, failure)
    with pytest.raises(IdentityUnavailable, match="unreachable"):
        make_provider(clock).get_token()


@pytest.mark.parametrize(
    "answer",
    [b"<html>502 Bad Gateway</html>", b"", b"\xff\xfe"],
)
def test_an_answer_that_is_not_json_is_unavailable(net, clock, answer):
    net.on("POST", TOKEN_PATH, answer)
    with pytest.raises(IdentityUnavailable, match="not JSON"):
        make_provider(clock).get_token()


@pytest.mark.parametrize(
    "answer",
    [{}, {"access_token": ""}, {"access_token": None}, {"access_token": 7}, {"access_token": "two words"}, {"access_token": "abc\r\nX-Evil: 1"}, ["access_token"]],
)
def test_a_200_without_a_usable_token_is_a_bad_response(net, clock, answer):
    """Includes a token with CR/LF in it: it must never reach an HTTP header."""
    net.on("POST", TOKEN_PATH, answer)
    with pytest.raises(AuthError) as err:
        make_provider(clock).get_token()
    assert err.value.code == "bad_response"


# -- secrets stay secret -----------------------------------------------------------------------------------------------------------------------------------


def test_the_secret_and_the_token_are_not_in_repr_or_in_any_error_text(net, clock, traces):
    token = make_jwt(serial=1)
    p = make_provider(clock)
    texts = [repr(p), str(p)]
    scripted = [
        identity_error(401, "invalid_service_credentials", "invalid credentials"),
        identity_error(400, "validation_error", f"the secret {SECRET} is wrong"),  # an identity that echoes its input
        identity_error(503, "busy", f"overloaded while checking {SECRET}"),
        URLError(f"cannot reach {SECRET}"),
        mint_answer(token),
    ]
    for answer in scripted:
        net.on("POST", TOKEN_PATH, answer)
        clock.advance(61)
        try:
            p.get_token()
        except (AuthError, IdentityUnavailable) as exc:
            texts.append(str(exc))
            texts.append(repr(exc))
    blob = "\n".join(texts) + repr(traces)
    assert SECRET not in blob
    assert token not in blob
    assert "***" in blob  # the echoed secret was scrubbed, not just dropped


def test_the_mint_leaves_a_g9_trace_record_without_credentials(net, clock, traces):
    net.on("POST", TOKEN_PATH, identity_error(401, "invalid_service_credentials", "no"), mint_answer(make_jwt(serial=1)))
    p = make_provider(clock)
    with pytest.raises(AuthError):
        p.get_token()
    clock.advance(61)
    p.get_token()
    assert [(t["target_module"], t["route"], t["method"], t["status"]) for t in traces] == [
        ("aios-identity", "/service-account/token", "POST", "error"),
        ("aios-identity", "/service-account/token", "POST", "ok"),
    ]
    assert all(set(t) == {"request_id", "target_module", "route", "method", "status", "duration_ms", "contract_version"} for t in traces)


# -- transport ---------------------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    ["https://identity.example/identity", "http://127.0.0.1:3010", "http://localhost:3010/identity", "http://[::1]:3010", "http://identity.localhost", "https://10.0.0.5/x"],
)
def test_https_or_loopback_is_accepted(url):
    IdentityTokenProvider(url, SECRET)


@pytest.mark.parametrize(
    "url",
    ["http://identity.example/identity", "http://10.0.0.5:3010", "http://103.245.255.211/identity", "ftp://identity.example", "identity.example/identity", "", "https://"],
)
def test_clear_text_to_another_machine_and_unparseable_urls_are_refused(url):
    with pytest.raises(AuthError) as err:
        IdentityTokenProvider(url, SECRET)
    assert err.value.code == "insecure_transport" and err.value.source == "config"


def test_credentials_in_a_url_are_not_echoed_in_the_refusal():
    with pytest.raises(AuthError) as err:
        IdentityTokenProvider("http://alice:hunter2@identity.example/identity", SECRET)
    assert "hunter2" not in str(err.value) and "alice" not in str(err.value)
    assert "http://identity.example" in str(err.value)


def test_a_url_with_credentials_does_not_appear_in_the_providers_repr():
    p = IdentityTokenProvider("https://alice:hunter2@identity.example/identity", SECRET)
    assert "hunter2" not in repr(p) and "alice" not in repr(p)


# -- configuration from the environment --------------------------------------------------------------------------------------------------------------------


def test_nothing_is_configured_when_the_url_is_unset_or_blank():
    assert identity_token.get_provider({}) is None
    assert identity_token.get_provider({"AIOS_FLOW_IDENTITY_URL": "   ", "AIOS_FLOW_IDENTITY_SECRET": SECRET}) is None


@pytest.mark.parametrize("secret", [None, "", "   ", "\n"])
def test_a_url_without_a_secret_is_an_error_not_a_silent_downgrade(secret):
    env = {"AIOS_FLOW_IDENTITY_URL": IDENTITY_URL}
    if secret is not None:
        env["AIOS_FLOW_IDENTITY_SECRET"] = secret
    with pytest.raises(AuthError) as err:
        identity_token.get_provider(env)
    assert err.value.code == "missing_secret" and err.value.source == "config"
    assert "AIOS_FLOW_IDENTITY_SECRET" in str(err.value)


def test_defaults_and_overrides_from_the_environment():
    env = {"AIOS_FLOW_IDENTITY_URL": IDENTITY_URL, "AIOS_FLOW_IDENTITY_SECRET": SECRET}
    assert identity_token.get_provider(env).username == "svc:atp"
    assert identity_token.get_provider({**env, "AIOS_FLOW_IDENTITY_USER": " svc:other "}).username == "svc:other"
    assert identity_token.get_provider({**env, "AIOS_FLOW_IDENTITY_USER": ""}).username == "svc:atp"


def test_an_unchanged_environment_reuses_the_provider_and_a_changed_one_replaces_it():
    env = {"AIOS_FLOW_IDENTITY_URL": IDENTITY_URL, "AIOS_FLOW_IDENTITY_SECRET": SECRET}
    first = identity_token.get_provider(env)
    assert identity_token.get_provider(dict(env)) is first
    assert identity_token.get_provider({**env, "AIOS_FLOW_IDENTITY_SECRET": SECRET + "x"}) is not first
    assert identity_token.get_provider({**env, "AIOS_FLOW_IDENTITY_URL": IDENTITY_URL + "/"}) is not None


def test_a_trailing_newline_from_the_keychain_is_not_part_of_the_secret():
    env = {"AIOS_FLOW_IDENTITY_URL": IDENTITY_URL, "AIOS_FLOW_IDENTITY_SECRET": SECRET + "\n"}
    assert identity_token.get_provider(env).matches(IDENTITY_URL, SECRET, "svc:atp")


def test_an_insecure_url_in_the_environment_is_an_error_at_the_first_call():
    with pytest.raises(AuthError, match="https"):
        identity_token.get_provider({"AIOS_FLOW_IDENTITY_URL": "http://identity.example", "AIOS_FLOW_IDENTITY_SECRET": SECRET})
