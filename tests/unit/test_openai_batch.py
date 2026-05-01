"""Unit tests for adapters/cloud/openai_batch.py — OpenAI Batch API adapter."""

from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from adapters.cloud.openai_batch import (
    cancel_batch,
    create_batch,
    dispatch,
    get_batch_results,
    get_batch_status,
    list_batches,
    wait_for_batch,
)


def _json_response(body: dict, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.headers = {"Content-Type": "application/json"}
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _bytes_response(body: bytes, status: int = 200, content_type: str = "application/jsonl") -> MagicMock:
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = body
    resp.headers = {"Content-Type": content_type}
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestCreateBatch(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_create_success(self, mock_urlopen: MagicMock) -> None:
        # First call uploads file, second creates batch.
        mock_urlopen.side_effect = [
            _json_response({"id": "file-abc", "object": "file"}),
            _json_response({"id": "batch_xyz", "status": "validating",
                           "endpoint": "/v1/chat/completions"}),
        ]
        result = create_batch(
            [{"custom_id": "r1", "body": {"model": "gpt-4o-mini",
                                          "messages": [{"role": "user", "content": "hi"}]}}],
            api_key="sk-test",
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_id"], "batch_xyz")
        self.assertEqual(result["input_file_id"], "file-abc")
        self.assertEqual(result["request_count"], 1)
        self.assertEqual(mock_urlopen.call_count, 2)

    def test_create_missing_api_key(self) -> None:
        with patch("adapters.cloud.openai_batch._get_api_key", return_value=None):
            result = create_batch(
                [{"custom_id": "r1", "body": {}}], api_key=None,
            )
        self.assertEqual(result["status"], "failed")
        self.assertIn("OPENAI_API_KEY", result["error"])

    def test_create_empty_requests(self) -> None:
        result = create_batch([], api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("non-empty", result["error"])

    def test_create_request_missing_custom_id(self) -> None:
        result = create_batch(
            [{"body": {"model": "gpt-4o-mini"}}],  # no custom_id
            api_key="sk-test",
        )
        self.assertEqual(result["status"], "failed")
        self.assertIn("custom_id", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_create_file_upload_http_error(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = HTTPError(
            url="http://x", code=401, msg="Unauthorized",
            hdrs=None, fp=BytesIO(b'{"error":{"message":"bad key"}}'),
        )
        result = create_batch(
            [{"custom_id": "r1", "body": {"model": "gpt-4o-mini"}}],
            api_key="sk-bad",
        )
        self.assertEqual(result["status"], "failed")
        self.assertIn("file upload failed", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_create_jsonl_serializes_correctly(self, mock_urlopen: MagicMock) -> None:
        captured: list[bytes] = []

        def fake(req, timeout=30):
            captured.append(req.data)
            # Return a different shape per call
            if len(captured) == 1:
                return _json_response({"id": "file-1"})
            return _json_response({"id": "batch_1", "status": "validating"})

        mock_urlopen.side_effect = fake
        create_batch(
            [
                {"custom_id": "a", "body": {"model": "gpt-4o-mini", "messages": []}},
                {"custom_id": "b", "body": {"model": "gpt-4o-mini", "messages": []}},
            ],
            api_key="sk-test",
        )
        # First captured body is multipart with JSONL inside
        self.assertIn(b'"custom_id": "a"', captured[0])
        self.assertIn(b'"custom_id": "b"', captured[0])
        self.assertIn(b'"url": "/v1/chat/completions"', captured[0])

        # Second call is JSON body for /batches
        batch_body = json.loads(captured[1].decode("utf-8"))
        self.assertEqual(batch_body["input_file_id"], "file-1")
        self.assertEqual(batch_body["completion_window"], "24h")
        self.assertEqual(batch_body["endpoint"], "/v1/chat/completions")


class TestGetBatchStatus(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_status_success(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "id": "batch_xyz",
            "status": "in_progress",
            "request_counts": {"total": 5, "completed": 2, "failed": 0},
        })
        result = get_batch_status("batch_xyz", api_key="sk-test")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_status"], "in_progress")
        self.assertEqual(result["request_counts"]["completed"], 2)

    def test_status_missing_batch_id(self) -> None:
        result = get_batch_status("", api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("batch_id", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_status_404(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = HTTPError(
            url="http://x", code=404, msg="Not Found",
            hdrs=None, fp=BytesIO(b'{"error":{"message":"batch not found"}}'),
        )
        result = get_batch_status("batch_missing", api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("404", result["error"])


class TestGetBatchResults(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_results_success(self, mock_urlopen: MagicMock) -> None:
        # First call: batch lookup returns completed; second: download JSONL.
        jsonl_body = (
            b'{"custom_id":"r1","response":{"status_code":200,"body":{"choices":[]}}}\n'
            b'{"custom_id":"r2","response":{"status_code":200,"body":{"choices":[]}}}\n'
        )
        mock_urlopen.side_effect = [
            _json_response({"id": "batch_x", "status": "completed",
                           "output_file_id": "file-out"}),
            _bytes_response(jsonl_body),
        ]
        result = get_batch_results("batch_x", api_key="sk-test")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_count"], 2)
        self.assertEqual(result["results"][0]["custom_id"], "r1")

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_results_not_completed_yet(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "id": "batch_x", "status": "in_progress",
        })
        result = get_batch_results("batch_x", api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("in_progress", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_results_no_output_file(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "id": "batch_x", "status": "completed", "output_file_id": None,
        })
        result = get_batch_results("batch_x", api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("output_file_id", result["error"])


class TestCancelBatch(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_cancel_success(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "id": "batch_x", "status": "cancelling",
        })
        result = cancel_batch("batch_x", api_key="sk-test")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_status"], "cancelling")

    def test_cancel_missing_batch_id(self) -> None:
        result = cancel_batch("", api_key="sk-test")
        self.assertEqual(result["status"], "failed")


class TestListBatches(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_list_success(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "data": [{"id": "b1", "status": "completed"},
                     {"id": "b2", "status": "in_progress"}],
            "has_more": False,
        })
        result = list_batches(api_key="sk-test", limit=10)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 2)
        self.assertFalse(result["has_more"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_list_passes_limit_param(self, mock_urlopen: MagicMock) -> None:
        captured = {}

        def fake(req, timeout=30):
            captured["url"] = req.full_url
            return _json_response({"data": [], "has_more": False})

        mock_urlopen.side_effect = fake
        list_batches(api_key="sk-test", limit=5, after="batch_42")
        self.assertIn("limit=5", captured["url"])
        self.assertIn("after=batch_42", captured["url"])


class TestDispatch(unittest.TestCase):

    @patch("adapters.cloud.openai_batch.create_batch")
    def test_dispatch_create(self, mock_create: MagicMock) -> None:
        mock_create.return_value = {"status": "success"}
        dispatch({
            "adapter": "openai-batch",
            "action": "create",
            "requests": [{"custom_id": "x", "body": {}}],
            "api_key": "sk-test",
            "completion_window": "24h",
        })
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["api_key"], "sk-test")
        self.assertEqual(kwargs["completion_window"], "24h")

    @patch("adapters.cloud.openai_batch.get_batch_status")
    def test_dispatch_status(self, mock_status: MagicMock) -> None:
        mock_status.return_value = {"status": "success"}
        dispatch({"adapter": "openai-batch", "action": "status",
                  "batch_id": "b1", "api_key": "sk"})
        mock_status.assert_called_once_with("b1", api_key="sk")

    def test_dispatch_unknown_action(self) -> None:
        result = dispatch({"adapter": "openai-batch", "action": "bogus"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("unknown action", result["error"])


class TestWaitForBatch(unittest.TestCase):
    """v2.5.0 — poll a batch until terminal state or timeout."""

    def test_wait_missing_batch_id(self) -> None:
        result = wait_for_batch("", api_key="sk-test")
        self.assertEqual(result["status"], "failed")
        self.assertIn("batch_id", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_wait_terminal_on_first_poll(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({
            "id": "b1", "status": "completed",
            "request_counts": {"total": 5, "completed": 5},
        })
        # Inject a deterministic clock so waited_s is stable.
        clock = [0.0]
        result = wait_for_batch(
            "b1", api_key="sk-test",
            sleep_fn=lambda _s: None,
            now_fn=lambda: clock[0],
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_status"], "completed")
        self.assertEqual(result["poll_count"], 1)
        self.assertFalse(result["timed_out"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_wait_polls_until_terminal(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = [
            _json_response({"id": "b1", "status": "validating"}),
            _json_response({"id": "b1", "status": "in_progress"}),
            _json_response({"id": "b1", "status": "completed"}),
        ]
        result = wait_for_batch(
            "b1", api_key="sk-test",
            poll_interval_s=1, timeout_s=60,
            sleep_fn=lambda _s: None,
            now_fn=lambda: 0.0,
        )
        self.assertEqual(result["batch_status"], "completed")
        self.assertEqual(result["poll_count"], 3)
        self.assertFalse(result["timed_out"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_wait_times_out(self, mock_urlopen: MagicMock) -> None:
        # Always return non-terminal status; simulated clock moves past timeout.
        mock_urlopen.return_value = _json_response({"id": "b1", "status": "in_progress"})
        clock = [0.0]
        # Each now() call advances the clock by 5s; timeout=10 means after 2 polls we exceed.
        def fake_now():
            t = clock[0]
            clock[0] += 5
            return t
        result = wait_for_batch(
            "b1", api_key="sk-test",
            timeout_s=10, poll_interval_s=1,
            sleep_fn=lambda _s: None,
            now_fn=fake_now,
        )
        self.assertEqual(result["status"], "timeout")
        self.assertTrue(result["timed_out"])
        self.assertIn("did not reach terminal", result["error"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_wait_short_circuits_on_status_error(self, mock_urlopen: MagicMock) -> None:
        # First poll returns HTTP 500 — wait_for_batch must return immediately
        # rather than spinning until timeout.
        from io import BytesIO
        mock_urlopen.side_effect = HTTPError(
            url="http://x", code=500, msg="Server Error",
            hdrs=None, fp=BytesIO(b'{"error":{"message":"down"}}'),
        )
        result = wait_for_batch(
            "b1", api_key="sk-test",
            sleep_fn=lambda _s: None,
            now_fn=lambda: 0.0,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["poll_count"], 1)
        self.assertFalse(result["timed_out"])

    @patch("adapters.cloud.openai_batch.urlopen")
    def test_wait_recognizes_failed_terminal(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _json_response({"id": "b1", "status": "failed"})
        result = wait_for_batch(
            "b1", api_key="sk-test",
            sleep_fn=lambda _s: None,
            now_fn=lambda: 0.0,
        )
        # API call succeeded; "failed" is a terminal batch state.
        self.assertEqual(result["batch_status"], "failed")
        self.assertFalse(result["timed_out"])


class TestDispatchWait(unittest.TestCase):
    """v2.5.0 — dispatch routes action='wait' to wait_for_batch."""

    @patch("adapters.cloud.openai_batch.wait_for_batch")
    def test_dispatch_wait(self, mock_wait: MagicMock) -> None:
        mock_wait.return_value = {"status": "success"}
        dispatch({
            "adapter": "openai-batch", "action": "wait",
            "batch_id": "b1", "api_key": "sk",
            "timeout_s": 120, "poll_interval_s": 5,
        })
        mock_wait.assert_called_once()
        kwargs = mock_wait.call_args.kwargs
        self.assertEqual(kwargs["api_key"], "sk")
        self.assertEqual(kwargs["timeout_s"], 120)
        self.assertEqual(kwargs["poll_interval_s"], 5)

    def test_dispatch_unknown_action_mentions_wait(self) -> None:
        result = dispatch({"adapter": "openai-batch", "action": "bogus"})
        self.assertIn("wait", result["error"])


if __name__ == "__main__":
    unittest.main()
