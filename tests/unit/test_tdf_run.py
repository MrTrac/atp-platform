"""Unit tests for ATP tdf-run bridge provider (mocked HTTP)."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from bridge.tdf_run import TdfBridgeError, _governance_class, dispatch


def _mock_response(body: dict) -> MagicMock:
    """Build a mock urlopen response returning JSON."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestDispatchValidation(unittest.TestCase):

    def test_missing_target_tool_raises(self) -> None:
        with self.assertRaises(TdfBridgeError) as ctx:
            dispatch({"target": {}})
        self.assertIn("target.tool", str(ctx.exception))

    def test_empty_target_raises(self) -> None:
        with self.assertRaises(TdfBridgeError):
            dispatch({})


class TestDispatchSuccess(unittest.TestCase):

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_dry_run_default_returns_class_c(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "status": "ok",
            "message": "validated",
            "data": {
                "job_id": "job_123",
                "exit_code": 0,
                "stdout_preview": "ok",
                "stderr_preview": "",
            },
        })
        result = dispatch({"target": {"tool": "ops/checkos", "partition": "OPS"}})

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_provider"], "tdf-run")
        self.assertEqual(result["governance"]["preliminary_class"], "C")
        self.assertFalse(result["governance"]["requires_human"])
        self.assertEqual(result["tdf"]["data"]["job_id"], "job_123")

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_dispatch_passes_correlation_id(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"status": "ok", "data": {}})
        dispatch({
            "target": {"tool": "ops/checkos"},
            "correlation_id": "abc-123",
        })
        sent_body = json.loads(mock_urlopen.call_args[0][0].data)
        self.assertEqual(sent_body["correlation_id"], "abc-123")

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_dispatch_uses_request_id_when_no_correlation_id(
        self, mock_urlopen: MagicMock
    ) -> None:
        mock_urlopen.return_value = _mock_response({"status": "ok", "data": {}})
        result = dispatch({"target": {"tool": "ops/checkos"}})
        sent_body = json.loads(mock_urlopen.call_args[0][0].data)
        # Falls back to internally-generated request_id
        self.assertTrue(sent_body["correlation_id"].startswith("bridge-tdf-"))
        self.assertEqual(result["request_id"], sent_body["correlation_id"])

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_envelope_includes_bridge_metadata(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "status": "accepted",
            "message": "queued",
            "data": {"job_id": "job_456"},
        })
        result = dispatch({"target": {"tool": "ops/checkos"}})

        self.assertEqual(result["bridge"]["resolved_provider"], "tdf-run")
        self.assertEqual(result["bridge"]["resolved_model"], "tdf")
        self.assertIn("/api/exec/execute", result["bridge"]["tdf_endpoint"])
        self.assertIn("bridge_timestamp", result["bridge"])


class TestDispatchFailure(unittest.TestCase):

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_tdf_error_status_marks_failure(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({
            "status": "error",
            "message": "WEB_TOOL_FORMAT: unknown tool",
            "data": {},
        })
        result = dispatch({"target": {"tool": "bogus/tool"}})

        self.assertEqual(result["status"], "failed")
        self.assertIn("WEB_TOOL_FORMAT", result["error"])

    @patch("bridge.tdf_run.urllib.request.urlopen", side_effect=OSError("refused"))
    def test_unreachable_tdf_raises(self, mock_urlopen: MagicMock) -> None:
        with self.assertRaises(TdfBridgeError) as ctx:
            dispatch({"target": {"tool": "ops/checkos"}})
        self.assertIn("Cannot reach TDF", str(ctx.exception))

    @patch("bridge.tdf_run.urllib.request.urlopen")
    def test_non_json_response_raises(self, mock_urlopen: MagicMock) -> None:
        bad_resp = MagicMock()
        bad_resp.read.return_value = b"<html>500 error</html>"
        bad_resp.__enter__ = lambda s: s
        bad_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = bad_resp
        with self.assertRaises(TdfBridgeError) as ctx:
            dispatch({"target": {"tool": "ops/checkos"}})
        self.assertIn("non-JSON", str(ctx.exception))


class TestGovernanceClass(unittest.TestCase):

    def test_dry_run_is_c(self) -> None:
        self.assertEqual(_governance_class({"dry_run": True}, {}), "C")

    def test_real_validate_is_c(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "validate"}),
            "C",
        )

    def test_real_deploy_is_b(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "deploy.tool"}),
            "B",
        )

    def test_real_install_is_b(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "install.package"}),
            "B",
        )

    def test_real_rollback_is_a(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "rollback.tool"}),
            "A",
        )

    def test_real_uninstall_is_a(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "uninstall.package"}),
            "A",
        )

    def test_real_undeploy_is_a(self) -> None:
        self.assertEqual(
            _governance_class({"dry_run": False}, {"operation": "undeploy.tool"}),
            "A",
        )


if __name__ == "__main__":
    unittest.main()
