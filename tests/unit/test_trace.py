"""Unit tests for core/trace.py — G9 cross-module observability."""

from __future__ import annotations

import json
import re
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from core.trace import (
    _SOURCE_MODULE,
    build_traceparent,
    generate_request_id,
    record_trace,
    trace_headers,
)

_W3C_RE = re.compile(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")


def test_generate_request_id_length():
    rid = generate_request_id()
    assert len(rid) == 16
    assert rid == rid.lower()
    assert all(c in "0123456789abcdef" for c in rid)


def test_generate_request_id_unique():
    ids = {generate_request_id() for _ in range(100)}
    assert len(ids) == 100


def test_build_traceparent_format():
    rid = generate_request_id()
    tp = build_traceparent(rid)
    assert _W3C_RE.match(tp), f"Invalid traceparent: {tp}"


def test_build_traceparent_pads_short_id():
    tp = build_traceparent("abc")
    assert _W3C_RE.match(tp)
    assert tp.startswith("00-abc")


def test_build_traceparent_truncates_long_id():
    long_id = "a" * 64
    tp = build_traceparent(long_id)
    assert _W3C_RE.match(tp)


def test_trace_headers_keys():
    rid = generate_request_id()
    headers = trace_headers(rid)
    assert "x-request-id" in headers
    assert "traceparent" in headers
    assert "x-source-module" in headers
    assert headers["x-source-module"] == _SOURCE_MODULE
    assert headers["x-request-id"] == rid
    assert _W3C_RE.match(headers["traceparent"])


def test_record_trace_writes_jsonl(tmp_path):
    trace_file = tmp_path / "cross_module_trace.jsonl"
    with patch("core.trace._TRACE_FILE", trace_file):
        record_trace(
            request_id="test1234abcd5678",
            target_module="aokp",
            route="/api/search",
            method="POST",
            status="ok",
            duration_ms=42,
            contract_version="AOKP_ATP_v2.3",
        )
    assert trace_file.exists()
    entry = json.loads(trace_file.read_text())
    assert entry["request_id"] == "test1234abcd5678"
    assert entry["target_module"] == "aokp"
    assert entry["source_module"] == "atp"
    assert entry["route"] == "/api/search"
    assert entry["method"] == "POST"
    assert entry["status"] == "ok"
    assert entry["duration_ms"] == 42
    assert entry["contract_version"] == "AOKP_ATP_v2.3"
    assert _W3C_RE.match(entry["traceparent"])
    assert "ts" in entry


def test_record_trace_appends_not_overwrites(tmp_path):
    trace_file = tmp_path / "cross_module_trace.jsonl"
    with patch("core.trace._TRACE_FILE", trace_file):
        record_trace(request_id="aaa", target_module="aokp", route="/api/health")
        record_trace(request_id="bbb", target_module="tdf", route="/api/exec/execute")
    lines = trace_file.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["request_id"] == "aaa"
    assert json.loads(lines[1])["request_id"] == "bbb"


def test_record_trace_entry_schema(tmp_path):
    trace_file = tmp_path / "cross_module_trace.jsonl"
    with patch("core.trace._TRACE_FILE", trace_file):
        record_trace(request_id="schema_test", target_module="tdf",
                     route="/api/exec/execute", method="POST", status="error",
                     duration_ms=99, contract_version="TDF_ATP_v1")
    entry = json.loads(trace_file.read_text())
    required_keys = {"ts", "request_id", "traceparent", "source_module",
                     "target_module", "route", "method", "status",
                     "duration_ms", "contract_version"}
    assert required_keys.issubset(entry.keys())


def test_record_trace_silent_fail_on_error(tmp_path):
    bad_path = tmp_path / "no_perm" / "trace.jsonl"
    with patch("core.trace._TRACE_FILE", bad_path):
        with patch.object(Path, "mkdir", side_effect=PermissionError("denied")):
            # Must not raise
            record_trace(request_id="x", target_module="aokp", route="/api/health")
