"""Unit tests for adapters/aios_flow/aios_flow_adapter.py."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from adapters.aios_flow.aios_flow_adapter import (
    _get_run_status,
    _wait_for_run,
    dispatch,
)


def _mock_response(body: dict, status: int = 200):
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    resp.status = status
    return resp


def test_dispatch_success():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        mock_open.return_value = _mock_response({"id": "run-abc", "status": "queued"})
        result = dispatch({"provider": "aios-flow", "pipeline": "flows/test.yml"})
    assert result["status"] == "dispatched"
    assert result["flow_run_id"] == "run-abc"
    assert result["flow_status"] == "queued"
    assert result["selected_provider"] == "aios-flow"
    assert "request_id" in result


def test_dispatch_missing_pipeline_returns_error():
    result = dispatch({"provider": "aios-flow"})
    assert result["status"] == "error"
    assert "pipeline" in result["error"]


def test_dispatch_pipeline_from_target_flow():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        mock_open.return_value = _mock_response({"id": "run-xyz", "status": "running"})
        result = dispatch({"provider": "aios-flow", "target": {"flow": "flows/deploy.yml"}})
    assert result["status"] == "dispatched"
    assert result["flow_run_id"] == "run-xyz"


def test_dispatch_url_error():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen",
               side_effect=URLError("connection refused")), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = dispatch({"pipeline": "flows/test.yml"})
    assert result["status"] == "error"
    assert "unreachable" in result["error"]


def test_dispatch_http_error():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen",
               side_effect=HTTPError(url="http://x", code=500,
                                     msg="Server Error", hdrs=None, fp=None)), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = dispatch({"pipeline": "flows/test.yml"})
    assert result["status"] == "error"


def test_dispatch_non_json_response():
    resp = MagicMock()
    resp.read.return_value = b"not json"
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", return_value=resp), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = dispatch({"pipeline": "flows/test.yml"})
    assert result["status"] == "error"
    assert "non-JSON" in result["error"]


def test_dispatch_injects_trace_headers():
    captured_req = {}

    def fake_urlopen(req, timeout=10):
        captured_req["headers"] = dict(req.headers)
        return _mock_response({"id": "run-1", "status": "queued"})

    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", side_effect=fake_urlopen), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        dispatch({"pipeline": "flows/test.yml"})

    hdrs = {k.lower(): v for k, v in captured_req["headers"].items()}
    assert "x-request-id" in hdrs
    assert "traceparent" in hdrs
    assert "x-source-module" in hdrs


def test_dispatch_records_trace():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace") as mock_trace:
        mock_open.return_value = _mock_response({"id": "run-2", "status": "queued"})
        dispatch({"pipeline": "flows/test.yml"})
    mock_trace.assert_called_once()
    call_kwargs = mock_trace.call_args.kwargs
    assert call_kwargs["target_module"] == "aios-flow"
    assert call_kwargs["route"] == "/api/runs"
    assert call_kwargs["status"] == "ok"


# ---------------------------------------------------------------------------
# v2.4.0 — status + wait actions
# ---------------------------------------------------------------------------


def test_status_action_returns_run_snapshot():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        mock_open.return_value = _mock_response({
            "id": "run-99", "status": "in_progress", "stages": []
        })
        result = dispatch({"action": "status", "flow_run_id": "run-99"})
    assert result["status"] == "ok"
    assert result["flow_run_id"] == "run-99"
    assert result["flow_status"] == "in_progress"
    assert result["flow_run"]["stages"] == []


def test_status_missing_flow_run_id():
    result = dispatch({"action": "status"})
    assert result["status"] == "error"
    assert "flow_run_id" in result["error"]


def test_status_url_error():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen",
               side_effect=URLError("connection refused")), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = dispatch({"action": "status", "flow_run_id": "run-1"})
    assert result["status"] == "error"
    assert "unreachable" in result["error"]


def test_status_records_trace_with_correct_route():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace") as mock_trace:
        mock_open.return_value = _mock_response({"id": "run-7", "status": "success"})
        dispatch({"action": "status", "flow_run_id": "run-7"})
    call_kwargs = mock_trace.call_args.kwargs
    assert call_kwargs["target_module"] == "aios-flow"
    assert call_kwargs["route"] == "/api/runs/run-7"
    assert call_kwargs["method"] == "GET"


def test_wait_returns_when_terminal_state_reached():
    states = iter([
        {"id": "r1", "status": "in_progress"},
        {"id": "r1", "status": "in_progress"},
        {"id": "r1", "status": "success"},
    ])

    def fake_urlopen(req, timeout=10):
        return _mock_response(next(states))

    sleeps: list[float] = []
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", side_effect=fake_urlopen), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = _wait_for_run(
            "r1", timeout_s=30, poll_interval_s=1,
            sleep_fn=lambda s: sleeps.append(s),
        )
    assert result["flow_status"] == "success"
    assert result["timed_out"] is False
    assert result["poll_count"] == 3
    assert sleeps == [1, 1]


def test_wait_times_out_when_run_never_terminal():
    def fake_urlopen(req, timeout=10):
        return _mock_response({"id": "r1", "status": "in_progress"})

    fake_now = iter([0.0, 5.0, 12.0, 35.0])
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", side_effect=fake_urlopen), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = _wait_for_run(
            "r1", timeout_s=30, poll_interval_s=1,
            sleep_fn=lambda _s: None,
            now_fn=lambda: next(fake_now),
        )
    assert result["status"] == "timeout"
    assert result["timed_out"] is True
    assert "30s" in result["error"]


def test_wait_returns_immediately_on_failed_status():
    def fake_urlopen(req, timeout=10):
        return _mock_response({"id": "r1", "status": "failed"})

    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", side_effect=fake_urlopen), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = _wait_for_run(
            "r1", timeout_s=30, poll_interval_s=1, sleep_fn=lambda _s: None,
        )
    assert result["flow_status"] == "failed"
    assert result["poll_count"] == 1


def test_wait_returns_error_if_polling_call_fails():
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen",
               side_effect=URLError("down")), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        result = _wait_for_run(
            "r1", timeout_s=30, poll_interval_s=1, sleep_fn=lambda _s: None,
        )
    assert result["status"] == "error"
    assert "unreachable" in result["error"]


def test_wait_action_via_dispatch_router():
    states = iter([
        {"id": "r9", "status": "in_progress"},
        {"id": "r9", "status": "succeeded"},
    ])

    def fake_urlopen(req, timeout=10):
        return _mock_response(next(states))

    with patch("adapters.aios_flow.aios_flow_adapter.urlopen", side_effect=fake_urlopen), \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"), \
         patch("adapters.aios_flow.aios_flow_adapter.time.sleep", lambda _s: None):
        result = dispatch({
            "action": "wait", "flow_run_id": "r9",
            "timeout_s": 30, "poll_interval_s": 1,
        })
    assert result["flow_status"] == "succeeded"
    assert result["timed_out"] is False


def test_dispatch_unknown_action_returns_error():
    result = dispatch({"action": "bogus"})
    assert result["status"] == "error"
    assert "unknown action" in result["error"]


def test_dispatch_default_action_is_submit():
    """Backward compat: no action field still submits a flow."""
    with patch("adapters.aios_flow.aios_flow_adapter.urlopen") as mock_open, \
         patch("adapters.aios_flow.aios_flow_adapter.record_trace"):
        mock_open.return_value = _mock_response({"id": "run-bc", "status": "queued"})
        result = dispatch({"pipeline": "flows/back-compat.yml"})
    assert result["status"] == "dispatched"
    assert result["flow_run_id"] == "run-bc"
