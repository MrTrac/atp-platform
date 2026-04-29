"""Unit tests for core/evaluator.py — ATP evaluator pattern."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from core.evaluator import _run_http_probe, run_evaluator


def _mock_urlopen(status: int, body: str):
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = body.encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_http_probe_pass_status():
    with patch("core.evaluator.urlopen", return_value=_mock_urlopen(200, "{}")):
        result = _run_http_probe({"url": "http://localhost/health"})
    assert result["passed"] is True
    assert result["http_status"] == 200


def test_http_probe_fail_wrong_status():
    with patch("core.evaluator.urlopen", return_value=_mock_urlopen(503, "{}")):
        result = _run_http_probe({"url": "http://localhost/health"})
    assert result["passed"] is False
    assert result["http_status"] == 503


def test_http_probe_json_key_match():
    body = json.dumps({"status": "ok"})
    with patch("core.evaluator.urlopen", return_value=_mock_urlopen(200, body)):
        result = _run_http_probe({
            "url": "http://localhost/health",
            "expect_json_key": "status",
            "expect_json_value": "ok",
        })
    assert result["passed"] is True


def test_http_probe_json_key_mismatch():
    body = json.dumps({"status": "degraded"})
    with patch("core.evaluator.urlopen", return_value=_mock_urlopen(200, body)):
        result = _run_http_probe({
            "url": "http://localhost/health",
            "expect_json_key": "status",
            "expect_json_value": "ok",
        })
    assert result["passed"] is False


def test_http_probe_url_error():
    with patch("core.evaluator.urlopen", side_effect=URLError("connection refused")):
        result = _run_http_probe({"url": "http://localhost/health"})
    assert result["passed"] is False
    assert "error" in result
    assert "duration_ms" in result


def test_http_probe_http_error():
    exc = HTTPError(url="http://x", code=500, msg="Server Error", hdrs=None, fp=None)
    with patch("core.evaluator.urlopen", side_effect=exc):
        result = _run_http_probe({"url": "http://localhost/health"})
    assert result["passed"] is False
    assert result["http_status"] == 500


def test_http_probe_missing_url():
    result = _run_http_probe({})
    assert result["passed"] is False
    assert "url" in result["error"]


def test_run_evaluator_dispatches_http_probe():
    with patch("core.evaluator.urlopen", return_value=_mock_urlopen(200, "{}")):
        result = run_evaluator({"type": "http-probe-evaluator", "url": "http://localhost/h"})
    assert "passed" in result
    assert result.get("skipped") is not True


def test_run_evaluator_unknown_type_returns_skipped():
    result = run_evaluator({"type": "llm-judge-evaluator", "rubric": "Is it good?"})
    assert result["passed"] is None
    assert result["skipped"] is True
    assert "aios-flow" in result["reason"]


def test_run_evaluator_visual_diff_stub():
    result = run_evaluator({"type": "visual-diff-evaluator", "url": "http://x",
                             "baseline_path": "tests/baselines/foo.png"})
    assert result["skipped"] is True
