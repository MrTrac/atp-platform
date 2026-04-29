"""Unit tests for adapters/aios_flow/aios_flow_adapter.py."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from adapters.aios_flow.aios_flow_adapter import dispatch


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
