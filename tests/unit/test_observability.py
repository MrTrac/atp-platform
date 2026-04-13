"""Unit tests for ATP v1.6 observability and hardening modules."""

from __future__ import annotations

import io
import json
import sys
import unittest

from core.config import ConfigWarning, summary, validate
from core.error_codes import (
    CONTRACT_VIOLATION,
    NETWORK_ERROR,
    TIMEOUT,
    UNKNOWN_ERROR,
    classify_error,
    get_error_code,
    to_dict,
)
from core.structured_log import log_event


class TestConfig(unittest.TestCase):

    def test_summary_returns_dict(self) -> None:
        s = summary()
        self.assertIsInstance(s, dict)
        self.assertIn("bridge_port", s)
        self.assertIn("aokp_enabled", s)
        self.assertIn("persist_artifacts", s)
        self.assertIn("anthropic_api_key_set", s)

    def test_validate_returns_list(self) -> None:
        warnings = validate()
        self.assertIsInstance(warnings, list)
        for w in warnings:
            self.assertIsInstance(w, ConfigWarning)
            self.assertIsInstance(w.key, str)
            self.assertIsInstance(w.message, str)

    def test_summary_has_model_allowlist(self) -> None:
        s = summary()
        self.assertIn("model_allowlist", s)


class TestErrorCodes(unittest.TestCase):

    def test_classify_timeout(self) -> None:
        ec = classify_error("Connection timed out after 120s")
        self.assertEqual(ec.code, "timeout")
        self.assertTrue(ec.recoverable)

    def test_classify_network_error(self) -> None:
        ec = classify_error("URLError: Connection refused")
        self.assertEqual(ec.code, "network_error")
        self.assertTrue(ec.recoverable)

    def test_classify_contract_violation(self) -> None:
        ec = classify_error("Execution contract violated: 'model' is required.")
        self.assertEqual(ec.code, "contract_violation")
        self.assertFalse(ec.recoverable)
        self.assertTrue(ec.requires_modification)

    def test_classify_completion_validation(self) -> None:
        ec = classify_error("Completion validation failed: empty response.")
        self.assertEqual(ec.code, "completion_validation_failed")

    def test_classify_unknown(self) -> None:
        ec = classify_error("Something totally unexpected")
        self.assertEqual(ec.code, "unknown_error")

    def test_get_error_code_known(self) -> None:
        ec = get_error_code("timeout")
        self.assertEqual(ec, TIMEOUT)

    def test_get_error_code_unknown(self) -> None:
        ec = get_error_code("nonexistent")
        self.assertEqual(ec, UNKNOWN_ERROR)

    def test_to_dict(self) -> None:
        d = to_dict(NETWORK_ERROR)
        self.assertEqual(d["code"], "network_error")
        self.assertEqual(d["category"], "transient")
        self.assertTrue(d["recoverable"])
        self.assertFalse(d["requires_modification"])

    def test_all_error_codes_have_fields(self) -> None:
        for ec in [NETWORK_ERROR, TIMEOUT, CONTRACT_VIOLATION, UNKNOWN_ERROR]:
            self.assertIsInstance(ec.code, str)
            self.assertIsInstance(ec.category, str)
            self.assertIsInstance(ec.recoverable, bool)
            self.assertIsInstance(ec.requires_modification, bool)


class TestStructuredLog(unittest.TestCase):

    def test_log_event_writes_json_to_stderr(self) -> None:
        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            log_event("test.event", request_id="req-1", status="ok")
        finally:
            sys.stderr = old_stderr

        output = captured.getvalue().strip()
        record = json.loads(output)
        self.assertEqual(record["event"], "test.event")
        self.assertEqual(record["request_id"], "req-1")
        self.assertEqual(record["status"], "ok")
        self.assertIn("timestamp", record)

    def test_log_event_omits_none_fields(self) -> None:
        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            log_event("minimal.event")
        finally:
            sys.stderr = old_stderr

        record = json.loads(captured.getvalue().strip())
        self.assertEqual(record["event"], "minimal.event")
        self.assertNotIn("request_id", record)
        self.assertNotIn("provider", record)

    def test_log_event_includes_extra_fields(self) -> None:
        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            log_event("custom.event", custom_field="value")
        finally:
            sys.stderr = old_stderr

        record = json.loads(captured.getvalue().strip())
        self.assertEqual(record["custom_field"], "value")

    def test_log_event_includes_cost(self) -> None:
        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            log_event("cost.event", cost_usd=0.0024, tokens=1245)
        finally:
            sys.stderr = old_stderr

        record = json.loads(captured.getvalue().strip())
        self.assertAlmostEqual(record["cost_usd"], 0.0024)
        self.assertEqual(record["tokens"], 1245)


class TestBridgeSecurity(unittest.TestCase):

    def test_config_has_max_body_bytes(self) -> None:
        from core.config import BRIDGE_MAX_BODY_BYTES
        self.assertIsInstance(BRIDGE_MAX_BODY_BYTES, int)
        self.assertGreater(BRIDGE_MAX_BODY_BYTES, 0)

    def test_default_max_body_is_10mb(self) -> None:
        from core.config import BRIDGE_MAX_BODY_BYTES
        self.assertEqual(BRIDGE_MAX_BODY_BYTES, 10 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
