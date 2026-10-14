"""The aios-flow adapter authenticates as svc:atp (aios-flow >= 1.2.0): the Authorization header, the 401/403 vs 503/network distinction, retries inside `wait`.

What is pinned, and why (measured 14/10/2026 against the real aios-identity 1.2.4 and the real aios-flow, aios-flow scripts/e2e/verify_real_stack.py):
  * without a token an enforcing aios-flow answers 401 and the old adapter reported "aios-flow unreachable: HTTP Error 401" — an auth failure looked like an outage;
  * a poll that hits aios-flow while identity is unreachable at the verdict-cache expiry gets `503 identity_unavailable` + `Retry-After: 5`, and the old `wait` gave up on a
    healthy run at the first such answer;
  * identity's token really lives 3600 s, so the adapter must renew it (renewal itself is pinned in test_aios_flow_identity_token.py).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.error import URLError

import pytest
from aios_flow_fakes import (
    FLOW_URL,
    IDENTITY_URL,
    SECRET,
    TOKEN_PATH,
    Clock,
    FakeNet,
    Http,
    flow_error,
    identity_error,
    make_jwt,
    mint_answer,
)

from adapters.aios_flow import aios_flow_adapter as adapter
from adapters.aios_flow import identity_token
from adapters.aios_flow.identity_token import IdentityTokenProvider
from core.trace import trace_headers

RUN = {"id": "run-1", "status": "queued"}
RUNNING = {"id": "run-1", "status": "running"}
DONE = {"id": "run-1", "status": "succeeded"}


@pytest.fixture
def net(monkeypatch):
    fake = FakeNet()
    monkeypatch.setattr(adapter, "urlopen", fake)
    monkeypatch.setattr(identity_token, "urlopen", fake)
    monkeypatch.setattr(adapter, "AIOS_FLOW_URL", FLOW_URL)
    return fake


@pytest.fixture
def traces(monkeypatch):
    records: list[dict] = []
    monkeypatch.setattr(adapter, "record_trace", lambda **kw: records.append(kw))
    monkeypatch.setattr(identity_token, "record_trace", lambda **kw: records.append(kw))
    return records


@pytest.fixture
def configured(monkeypatch):
    """Authentication switched on, as an operator would with the environment."""
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_URL", IDENTITY_URL)
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_SECRET", SECRET)


@pytest.fixture
def clock(monkeypatch, configured):
    """The process-wide provider, driven by a manual clock so tests can age a token without sleeping."""
    c = Clock()
    monkeypatch.setattr(identity_token, "_provider", IdentityTokenProvider(IDENTITY_URL, SECRET, clock=c))
    return c


def flow_header(call) -> str | None:
    return call.headers.get("authorization")


# -- the header: present, absent, only to aios-flow --------------------------------------------------------------------------------------------------------


def test_every_call_to_aios_flow_carries_the_bearer_token(net, traces, configured):
    token = make_jwt(serial=1)
    net.on("POST", TOKEN_PATH, mint_answer(token))
    net.on("POST", "/api/runs", RUN)
    net.on("GET", "/api/runs/run-1", RUNNING, DONE)
    adapter.dispatch({"pipeline": "flows/a"})
    adapter.dispatch({"action": "status", "flow_run_id": "run-1"})
    adapter.dispatch({"action": "wait", "flow_run_id": "run-1", "timeout_s": 30, "poll_interval_s": 1})
    assert len(net.flow_calls) == 3
    assert {flow_header(c) for c in net.flow_calls} == {f"Bearer {token}"}
    assert len(net.mint_calls) == 1  # one token serves the dispatch and the polls
    # the existing G9 headers are still there next to it
    assert all("x-request-id" in c.headers and "traceparent" in c.headers and "x-source-module" in c.headers for c in net.flow_calls)


def test_without_configuration_nothing_is_sent_and_identity_is_never_contacted(net, traces):
    net.on("POST", "/api/runs", RUN)
    net.on("GET", "/api/runs/run-1", DONE)
    assert adapter.dispatch({"pipeline": "flows/a"})["status"] == "dispatched"
    assert adapter.dispatch({"action": "status", "flow_run_id": "run-1"})["status"] == "ok"
    assert all(flow_header(c) is None for c in net.flow_calls)
    assert net.mint_calls == []  # an aios-flow that does not enforce keeps working exactly as before


def test_the_token_goes_to_aios_flow_and_nowhere_else(net, traces, configured):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("POST", "/api/runs", RUN)
    adapter.dispatch({"pipeline": "flows/a"})
    assert flow_header(net.mint_calls[0]) is None  # the call to identity authenticates with the secret in its body, not with a bearer
    assert all(c.url.startswith(FLOW_URL) for c in net.flow_calls)
    assert all(c.url.startswith(IDENTITY_URL) for c in net.mint_calls)
    # the shared G9 helper every other adapter uses never carries an Authorization header, so AOKP / tdf-run / the cloud adapters cannot leak it
    assert not any(k.lower() == "authorization" for k in trace_headers("abcdef0123456789"))


def test_only_the_aios_flow_adapter_uses_the_identity_token_module():
    root = Path(__file__).resolve().parents[2]
    users = []
    for path in root.rglob("*.py"):
        if any(part in {"tests", "__pycache__", ".venv", ".claude", "node_modules"} for part in path.relative_to(root).parts):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = [a.name for a in node.names] if isinstance(node, ast.ImportFrom | ast.Import) else []
            module = getattr(node, "module", "") or ""
            if "identity_token" in module or any("identity_token" in n for n in names):
                users.append(str(path.relative_to(root)))
    assert sorted(set(users)) == ["adapters/aios_flow/aios_flow_adapter.py"], users


# -- nothing secret in anything the caller or the trace file can see -----------------------------------------------------------------------------------------


SCENARIOS = {
    "ok": lambda n: n.on("POST", "/api/runs", RUN),
    "flow-401-then-ok": lambda n: n.on("POST", "/api/runs", flow_error(401, "invalid_token", "token failed verification"), RUN),
    "flow-401-twice": lambda n: n.on("POST", "/api/runs", flow_error(401, "invalid_token"), flow_error(401, "invalid_token")),
    "flow-403": lambda n: n.on("POST", "/api/runs", flow_error(403, "forbidden", "missing permission aiosoc.flows.run")),
    "flow-503": lambda n: n.on("POST", "/api/runs", flow_error(503, "identity_unavailable", "identity unreachable", {"Retry-After": "5"})),
    "flow-500-html": lambda n: n.on("POST", "/api/runs", Http(500, b"<html>boom</html>")),
    "network": lambda n: n.on("POST", "/api/runs", URLError("connection refused")),
    "non-json": lambda n: n.on("POST", "/api/runs", b"not json"),
}


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_neither_token_nor_secret_is_in_the_result_or_the_trace(name, net, clock, tmp_path, monkeypatch):
    """Runs with the real `record_trace` writing to a temporary file, so what is checked is what would be on disk."""
    monkeypatch.setattr("core.trace._TRACE_FILE", tmp_path / "trace.jsonl")
    first, second = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(first), mint_answer(second))
    identity_token.get_provider().get_token()  # a token minted earlier ...
    clock.advance(40)  # ... old enough that a 401 may replace it
    SCENARIOS[name](net)
    result = adapter.dispatch({"pipeline": "flows/a"})
    on_disk = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
    everything = json.dumps(result) + on_disk + repr(result)
    for secret in (first, second, SECRET, "Bearer"):
        assert secret not in everything, f"{secret!r} leaked in scenario {name}"
    assert on_disk.count("\n") >= 1
    net.assert_all_closed()


# -- 401: a fresh token, once ------------------------------------------------------------------------------------------------------------------------------


def test_a_401_for_an_old_token_gets_one_fresh_token_and_the_request_is_repeated(net, traces, clock):
    old, new = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(old), mint_answer(new))
    identity_token.get_provider().get_token()
    clock.advance(40)
    net.on("POST", "/api/runs", flow_error(401, "session_revoked", "session has been revoked"), RUN)
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["status"] == "dispatched" and result["flow_run_id"] == "run-1"
    assert [flow_header(c) for c in net.flow_calls] == [f"Bearer {old}", f"Bearer {new}"]
    assert len(net.mint_calls) == 2
    assert len({c.headers["x-request-id"] for c in net.flow_calls}) == 1  # the repeat is the same logical request
    net.assert_all_closed()


def test_a_second_401_is_an_auth_failure_and_there_is_no_third_try(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)), mint_answer(make_jwt(serial=2)), mint_answer(make_jwt(serial=3)))
    identity_token.get_provider().get_token()
    clock.advance(40)
    net.on("POST", "/api/runs", flow_error(401, "invalid_token", "token failed verification"), flow_error(401, "invalid_token", "token failed verification"))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert (result["status"], result["error_code"], result["retryable"], result["http_status"], result["reason_code"]) == ("error", "auth_failed", False, 401, "invalid_token")
    assert "rejected the identity token" in result["error"] and "invalid_token" in result["error"]
    assert len(net.flow_calls) == 2 and len(net.mint_calls) == 2
    net.assert_all_closed()


def test_a_second_401_is_final_even_when_the_cooldown_would_allow_another_mint(net, traces, monkeypatch, configured):
    """The cooldown (30 s) is one guard against re-minting; "once per request" must hold without it: here every clock reading is 40 s after the last."""

    class Jumping(Clock):
        def __call__(self) -> float:
            self.now += 40
            return self.now

    monkeypatch.setattr(identity_token, "_provider", IdentityTokenProvider(IDENTITY_URL, SECRET, clock=Jumping()))
    net.on("POST", TOKEN_PATH, *[mint_answer(make_jwt(serial=i)) for i in range(1, 6)])
    net.on("POST", "/api/runs", *[flow_error(401, "invalid_token") for _ in range(5)])
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["error_code"] == "auth_failed" and result["http_status"] == 401
    assert len(net.flow_calls) == 2 and len(net.mint_calls) == 2  # the first mint, and ONE replacement
    net.assert_all_closed()


def test_a_401_for_a_token_issued_moments_ago_does_not_mint_again(net, traces, clock):
    """Otherwise a persistent 401 (a service account missing from AIOS_FLOW_SERVICE_ACCOUNTS, a clock problem at identity) would add a year-long session per request."""
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)), mint_answer(make_jwt(serial=2)))
    net.on("POST", "/api/runs", flow_error(401, "invalid_token", "token failed verification"))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["error_code"] == "auth_failed" and "not asking for another" in result["error"]
    assert len(net.flow_calls) == 1 and len(net.mint_calls) == 1
    net.assert_all_closed()


def test_a_401_on_a_poll_is_handled_the_same_way(net, traces, clock):
    old, new = make_jwt(serial=1), make_jwt(serial=2)
    net.on("POST", TOKEN_PATH, mint_answer(old), mint_answer(new))
    identity_token.get_provider().get_token()
    clock.advance(40)
    net.on("GET", "/api/runs/run-1", flow_error(401, "invalid_token"), DONE)
    result = adapter.dispatch({"action": "wait", "flow_run_id": "run-1", "timeout_s": 30, "poll_interval_s": 1})
    assert result["flow_status"] == "succeeded"
    assert [flow_header(c) for c in net.flow_calls] == [f"Bearer {old}", f"Bearer {new}"]
    net.assert_all_closed()


def test_a_401_when_nothing_is_configured_says_what_to_configure(net, traces):
    """The measured symptom: an enforcing aios-flow answers 401 missing_token to a caller that sends nothing."""
    net.on("POST", "/api/runs", flow_error(401, "missing_token", "Authorization Bearer header required"))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["error_code"] == "auth_failed" and result["retryable"] is False
    assert "requires an identity token" in result["error"] and "missing_token" in result["error"]
    assert "AIOS_FLOW_IDENTITY_URL" in result["error"] and "AIOS_FLOW_IDENTITY_SECRET" in result["error"]
    assert "unreachable" not in result["error"]  # no longer mistaken for an outage
    assert len(net.flow_calls) == 1  # nothing to renew: no token was sent
    net.assert_all_closed()


# -- 403: never retried ------------------------------------------------------------------------------------------------------------------------------------


def test_a_403_is_reported_with_the_servers_error_code_and_never_retried(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("POST", "/api/runs", flow_error(403, "forbidden", "service account may not do that"))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert (result["status"], result["error_code"], result["retryable"], result["http_status"], result["reason_code"]) == ("error", "auth_failed", False, 403, "forbidden")
    assert result["error"].startswith("aios-flow denied the request: HTTP 403 forbidden") and result["auth_source"] == "aios-flow"
    assert len(net.flow_calls) == 1 and len(net.mint_calls) == 1  # not re-sent, no new token
    net.assert_all_closed()


def test_a_403_ends_a_wait_at_once(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", flow_error(403, "forbidden"))
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert result["status"] == "error" and result["error_code"] == "auth_failed" and result["timed_out"] is False
    assert sleeps == [] and len(net.flow_calls) == 1  # no retry loop for something retrying cannot fix
    net.assert_all_closed()


def test_a_service_account_that_identity_refuses_is_an_auth_failure_not_an_outage(net, traces, clock):
    net.on("POST", TOKEN_PATH, identity_error(401, "invalid_service_credentials", "invalid credentials"))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["error_code"] == "auth_failed" and result["retryable"] is False
    assert "invalid_service_credentials" in result["error"] and "svc:atp" in result["error"]
    assert result["auth_source"] == "aios-identity" and result["reason_code"] == "invalid_service_credentials"
    assert net.flow_calls == []  # no request is sent without a token
    net.assert_all_closed()


def test_identity_being_down_when_a_token_is_needed_is_unavailable_and_says_it_is_identity(net, traces, clock):
    """Not "aios-flow unavailable": aios-flow was never contacted."""
    net.on("POST", TOKEN_PATH, identity_error(503, "busy", "restarting"), URLError("connection refused"))
    for _ in range(2):
        result = adapter.dispatch({"pipeline": "flows/a"})
        assert (result["status"], result["error_code"], result["retryable"]) == ("error", "unavailable", True)
        assert result["error"].startswith("cannot get an identity token for aios-flow: aios-identity ")
    assert net.flow_calls == []
    net.assert_all_closed()


# -- 503 / network: retried inside wait, bounded -----------------------------------------------------------------------------------------------------------


def test_wait_retries_a_503_with_retry_after_and_goes_on_to_the_result(net, traces, clock):
    """The measured case: identity briefly unreachable at the verdict-cache expiry → 503 identity_unavailable + Retry-After: 5 on a healthy run."""
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", flow_error(503, "identity_unavailable", "identity unreachable", {"Retry-After": "5"}), DONE)
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert result["status"] == "ok" and result["flow_status"] == "succeeded" and result["timed_out"] is False
    assert sleeps == [5.0]  # exactly what the server asked for
    assert result["poll_count"] == 1  # the retry happened inside the poll
    assert [t["status"] for t in traces if t["target_module"] == "aios-flow"] == ["error", "ok"]  # both attempts are in the trace
    net.assert_all_closed()


def test_one_transient_503_in_the_middle_of_a_run_no_longer_ends_the_wait(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", RUNNING, flow_error(503, "identity_unavailable", "", {"Retry-After": "5"}), RUNNING, DONE)
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=lambda _s: None)
    assert result["flow_status"] == "succeeded" and result["poll_count"] == 3
    net.assert_all_closed()


def test_a_persistent_503_is_bounded_and_reported_as_unavailable(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", *[flow_error(503, "identity_unavailable", "identity unreachable", {"Retry-After": "5"}) for _ in range(10)])
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=300, poll_interval_s=1, sleep_fn=sleeps.append)
    assert (result["status"], result["error_code"], result["retryable"], result["http_status"]) == ("error", "unavailable", True, 503)
    assert result["reason_code"] == "identity_unavailable" and result["retry_after_s"] == 5.0 and result["timed_out"] is False
    assert len(net.flow_calls) == 4 and sleeps == [5.0, 5.0, 5.0]  # four attempts, then the wait gives up and says why
    assert "identity_unavailable" in result["error"]
    net.assert_all_closed()  # the three dropped attempts AND the last one


def test_network_errors_are_retried_inside_wait_too(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", URLError("connection refused"), TimeoutError("timed out"), DONE)
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert result["flow_status"] == "succeeded" and len(sleeps) == 2
    assert 1.0 <= sleeps[0] <= 1.25 and 2.0 <= sleeps[1] <= 2.5  # core.retry's exponential backoff with jitter


def test_a_persistent_network_failure_ends_the_wait_as_unreachable(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", *[URLError("connection refused") for _ in range(10)])
    result = adapter._wait_for_run("run-1", timeout_s=300, poll_interval_s=1, sleep_fn=lambda _s: None)
    assert (result["status"], result["error_code"], result["retryable"]) == ("error", "unreachable", True)
    assert "unreachable" in result["error"] and len(net.flow_calls) == 4


def test_a_transient_failure_to_obtain_a_token_is_retried_inside_wait(net, traces, clock):
    """Identity down exactly when the token has to be renewed: the poll waits and tries again instead of failing the wait."""
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    identity_token.get_provider().get_token()
    clock.advance(3301)  # past the renewal point
    net.on("POST", TOKEN_PATH, identity_error(503, "busy", "identity restarting"), mint_answer(make_jwt(serial=2)))
    net.on("GET", "/api/runs/run-1", DONE)
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert result["flow_status"] == "succeeded" and len(sleeps) == 1
    assert flow_header(net.flow_calls[0]).endswith(make_jwt(serial=2).split(".")[-1])  # the renewed token was used
    net.assert_all_closed()


def test_retries_never_run_past_the_waits_own_timeout(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", flow_error(503, "identity_unavailable", "", {"Retry-After": "5"}), DONE)
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=3, poll_interval_s=1, sleep_fn=sleeps.append)
    assert sleeps == [] and len(net.flow_calls) == 1  # a 5 s pause would overrun a 3 s wait: no sleep, the failure is reported
    assert result["status"] == "error" and result["error_code"] == "unavailable"
    net.assert_all_closed()


def test_errors_that_waiting_cannot_fix_end_the_wait_without_a_retry(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", flow_error(404, "run_not_found", "no such run"))
    sleeps: list[float] = []
    result = adapter._wait_for_run("run-1", timeout_s=60, poll_interval_s=1, sleep_fn=sleeps.append)
    assert (result["error_code"], result["retryable"], result["http_status"], result["reason_code"]) == ("http_error", False, 404, "run_not_found")
    assert "404" in result["error"] and "run_not_found" in result["error"] and "unreachable" not in result["error"]
    assert sleeps == [] and len(net.flow_calls) == 1
    net.assert_all_closed()


def test_dispatch_is_never_retried_by_itself(net, traces, clock):
    """A POST that failed in transit may have started the run; only an explicit caller decision may send it again."""
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("POST", "/api/runs", flow_error(503, "identity_unavailable", "", {"Retry-After": "5"}))
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert (result["error_code"], result["retryable"], result["retry_after_s"]) == ("unavailable", True, 5.0)
    assert len(net.flow_calls) == 1
    net.on("POST", "/api/runs", URLError("connection refused"))
    again = adapter.dispatch({"pipeline": "flows/a"})
    assert again["error_code"] == "unreachable" and len(net.flow_calls) == 2
    net.assert_all_closed()


def test_status_is_a_single_shot(net, traces, clock):
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("GET", "/api/runs/run-1", flow_error(503, "identity_unavailable", "", {"Retry-After": "5"}))
    result = adapter.dispatch({"action": "status", "flow_run_id": "run-1"})
    assert result["error_code"] == "unavailable" and len(net.flow_calls) == 1
    net.assert_all_closed()


# -- every error path closes what it opened ----------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "answers",
    [
        [flow_error(400, "invalid_pipeline", "inline YAML is refused")],
        [flow_error(404, "flow_not_found")],
        [flow_error(409, "ambiguous_pipeline")],
        [flow_error(429, "too_many_runs", "", {"Retry-After": "30"})],
        [flow_error(500, "internal")],
        [flow_error(503, "identity_unavailable")],
        [flow_error(401, "invalid_token"), flow_error(401, "invalid_token")],
        [flow_error(401, "invalid_token"), flow_error(503, "identity_unavailable")],
        [flow_error(403, "forbidden")],
    ],
)
def test_every_http_error_from_aios_flow_is_closed_whichever_action_meets_it(net, traces, clock, answers):
    net.on("POST", TOKEN_PATH, *[mint_answer(make_jwt(serial=i)) for i in range(1, 5)])
    for action in ("dispatch", "status", "wait"):
        identity_token.get_provider().get_token()
        clock.advance(40)  # old enough that a 401 may replace the token
        if action == "dispatch":
            net.on("POST", "/api/runs", *answers)
            adapter.dispatch({"pipeline": "flows/a"})
        elif action == "status":
            net.on("GET", "/api/runs/run-1", *answers)
            adapter.dispatch({"action": "status", "flow_run_id": "run-1"})
        else:
            net.on("GET", "/api/runs/run-1", *(answers * 4))  # enough answers for every retry
            adapter._wait_for_run("run-1", timeout_s=5, poll_interval_s=1, sleep_fn=lambda _s: None)
    assert net.errors_raised >= len(answers) * 3
    net.assert_all_closed()


@pytest.mark.parametrize("answer", [identity_error(400, "validation_error", "x"), identity_error(401, "invalid_service_credentials", "x"), identity_error(404, "nf", "x"), identity_error(503, "busy", "x")])
def test_every_http_error_from_identity_is_closed(net, traces, clock, answer):
    net.on("POST", TOKEN_PATH, answer)
    adapter.dispatch({"pipeline": "flows/a"})
    assert net.errors_raised == 1
    net.assert_all_closed()


# -- configuration that cannot work is reported, before any network ------------------------------------------------------------------------------------------


def test_a_url_without_a_secret_is_reported_and_nothing_is_sent(net, traces, monkeypatch):
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_URL", IDENTITY_URL)
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["status"] == "error" and result["error_code"] == "auth_failed" and result["reason_code"] == "missing_secret"
    assert result["auth_source"] == "config"
    assert "AIOS_FLOW_IDENTITY_SECRET" in result["error"]
    assert net.calls == []


@pytest.mark.parametrize("flow_url", ["http://flow.internal:7700", "http://10.1.2.3:7700"])
def test_the_token_is_not_sent_in_clear_text_to_another_machine(net, traces, clock, monkeypatch, flow_url):
    monkeypatch.setattr(adapter, "AIOS_FLOW_URL", flow_url)
    result = adapter.dispatch({"pipeline": "flows/a"})
    assert result["error_code"] == "auth_failed" and result["reason_code"] == "insecure_transport" and "AIOS_FLOW_URL" in result["error"]
    assert net.calls == []  # not even a token was requested for it


@pytest.mark.parametrize("flow_url", ["https://flow.example", "http://localhost:7700", "http://127.0.0.1:7700", "http://[::1]:7700"])
def test_https_or_loopback_flow_urls_get_the_token(net, traces, clock, monkeypatch, flow_url):
    monkeypatch.setattr(adapter, "AIOS_FLOW_URL", flow_url)
    net.on("POST", TOKEN_PATH, mint_answer(make_jwt(serial=1)))
    net.on("POST", "/api/runs", RUN)
    assert adapter.dispatch({"pipeline": "flows/a"})["status"] == "dispatched"
    assert flow_header(net.flow_calls[0]) is not None


def test_plain_http_to_another_machine_is_unchanged_when_authentication_is_not_configured(net, traces, monkeypatch):
    monkeypatch.setattr(adapter, "AIOS_FLOW_URL", "http://flow.internal:7700")
    net.on("POST", "/api/runs", RUN)
    assert adapter.dispatch({"pipeline": "flows/a"})["status"] == "dispatched"
    assert flow_header(net.flow_calls[0]) is None


# -- the shape of the failures -----------------------------------------------------------------------------------------------------------------------------


def test_each_kind_of_failure_has_its_own_code_and_the_old_text_survives_for_a_real_outage(net, traces):
    net.on("POST", "/api/runs", URLError("connection refused"), flow_error(400, "invalid_pipeline", "inline YAML is refused"), b"not json")
    down = adapter.dispatch({"pipeline": "flows/a"})
    assert down["error"].startswith("aios-flow unreachable:") and (down["error_code"], down["retryable"]) == ("unreachable", True)
    bad = adapter.dispatch({"pipeline": "flows/a"})
    assert (bad["error_code"], bad["retryable"], bad["http_status"], bad["reason_code"]) == ("http_error", False, 400, "invalid_pipeline")
    assert "inline YAML is refused" in bad["error"] and "unreachable" not in bad["error"]
    junk = adapter.dispatch({"pipeline": "flows/a"})
    assert (junk["error_code"], junk["retryable"]) == ("bad_response", False) and "non-JSON" in junk["error"]
    for result in (down, bad, junk):
        assert result["status"] == "error" and result["selected_provider"] == "aios-flow" and result["request_id"]
    net.assert_all_closed()


def test_a_status_failure_names_the_run(net, traces):
    net.on("GET", "/api/runs/run-9", flow_error(404, "run_not_found", "no such run"))
    result = adapter.dispatch({"action": "status", "flow_run_id": "run-9"})
    assert result["flow_run_id"] == "run-9" and result["http_status"] == 404
