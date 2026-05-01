"""OpenAI Batch API adapter — async LLM jobs at 50% cost discount.

Supports the 5 Batch API operations:
  - create_batch()      — upload JSONL + create batch (returns batch_id)
  - get_batch_status()  — poll batch state (validating | in_progress | completed | …)
  - get_batch_results() — download + parse output JSONL when completed
  - cancel_batch()      — cancel an in-flight batch
  - list_batches()      — list recent batches

Each request item must be a dict with shape:
    {"custom_id": str, "method": "POST", "url": "/v1/chat/completions",
     "body": {"model": str, "messages": [...]}}

Stdlib only (urllib). Returns structured dicts with status/error fields,
matching the cloud-adapter result protocol.
"""

from __future__ import annotations

import io
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPENAI_API_BASE = "https://api.openai.com/v1"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_COMPLETION_WINDOW = "24h"
_TERMINAL_BATCH_STATES = {"completed", "failed", "expired", "cancelled", "canceling"}
_DEFAULT_WAIT_TIMEOUT_S = 600  # 10 min default; max 24h, but typical batches take minutes
_DEFAULT_POLL_INTERVAL_S = 30


class OpenAIBatchAdapterError(ValueError):
    """Raised when the Batch adapter cannot fulfil a request."""


def _get_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _multipart_body(file_bytes: bytes, file_name: str, purpose: str) -> tuple[bytes, str]:
    """Build a minimal multipart/form-data body for /v1/files upload."""
    boundary = f"----ATPBoundary{uuid.uuid4().hex}"
    crlf = b"\r\n"
    parts: list[bytes] = []

    parts.append(f"--{boundary}".encode())
    parts.append(b'Content-Disposition: form-data; name="purpose"')
    parts.append(b"")
    parts.append(purpose.encode())

    parts.append(f"--{boundary}".encode())
    parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"'.encode()
    )
    parts.append(b"Content-Type: application/jsonl")
    parts.append(b"")
    parts.append(file_bytes)

    parts.append(f"--{boundary}--".encode())
    parts.append(b"")

    body = crlf.join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def _request_json(
    url: str,
    *,
    api_key: str,
    method: str = "GET",
    json_body: dict[str, Any] | None = None,
    raw_body: bytes | None = None,
    extra_headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[int, dict[str, Any] | bytes]:
    """Issue an HTTP request, return (status_code, parsed_or_raw_body).

    Returns the parsed JSON dict on success, raw bytes for non-JSON downloads
    (use ``raw_body`` to override and the caller can decide).
    """
    headers = {**_auth_headers(api_key)}
    data: bytes | None = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif raw_body is not None:
        data = raw_body
    if extra_headers:
        headers.update(extra_headers)

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            payload = resp.read()
            content_type = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if content_type == "application/json":
                return resp.status, json.loads(payload.decode("utf-8"))
            return resp.status, payload
    except HTTPError as exc:
        body_text = ""
        try:
            body_text = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        try:
            return exc.code, json.loads(body_text) if body_text else {"error": {"message": exc.reason}}
        except json.JSONDecodeError:
            return exc.code, {"error": {"message": body_text or exc.reason}}


def _error_result(message: str, timestamp: str, start_time: float) -> dict[str, Any]:
    return {
        "status": "failed",
        "provider": "openai-batch",
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": int((time.monotonic() - start_time) * 1000),
        },
        "error": message,
    }


def _success_result(payload: dict[str, Any], timestamp: str, start_time: float,
                    extra: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {
        "status": "success",
        "provider": "openai-batch",
        "batch": payload,
        "manifest": {
            "timestamp": timestamp,
            "response_time_ms": int((time.monotonic() - start_time) * 1000),
        },
        "error": None,
    }
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------------------


def create_batch(
    requests: list[dict[str, Any]],
    *,
    api_key: str | None = None,
    completion_window: str = DEFAULT_COMPLETION_WINDOW,
    endpoint: str = "/v1/chat/completions",
    metadata: dict[str, Any] | None = None,
    api_base: str = OPENAI_API_BASE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Upload a JSONL of requests and create a batch.

    Each item in ``requests`` must contain ``custom_id`` and ``body``. ``method``
    defaults to ``POST`` and ``url`` to ``endpoint`` if not present.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = api_key or _get_api_key()
    if not api_key:
        return _error_result("OPENAI_API_KEY not set", timestamp, start_time)
    if not requests:
        return _error_result("'requests' must be a non-empty list", timestamp, start_time)

    # Build JSONL
    lines: list[str] = []
    for idx, item in enumerate(requests):
        if "custom_id" not in item or "body" not in item:
            return _error_result(
                f"requests[{idx}] missing 'custom_id' or 'body'", timestamp, start_time
            )
        line_obj = {
            "custom_id": item["custom_id"],
            "method": item.get("method", "POST"),
            "url": item.get("url", endpoint),
            "body": item["body"],
        }
        lines.append(json.dumps(line_obj))
    file_bytes = ("\n".join(lines) + "\n").encode("utf-8")

    # 1) Upload file
    body, content_type = _multipart_body(file_bytes, "atp-batch.jsonl", "batch")
    code, file_resp = _request_json(
        f"{api_base}/files",
        api_key=api_key,
        method="POST",
        raw_body=body,
        extra_headers={"Content-Type": content_type},
        timeout=timeout,
    )
    if code >= 400 or not isinstance(file_resp, dict):
        msg = file_resp.get("error", {}).get("message", str(file_resp)) if isinstance(file_resp, dict) else "non-JSON response"
        return _error_result(f"file upload failed (HTTP {code}): {msg}", timestamp, start_time)
    file_id = file_resp.get("id")
    if not file_id:
        return _error_result("file upload returned no id", timestamp, start_time)

    # 2) Create batch
    batch_body: dict[str, Any] = {
        "input_file_id": file_id,
        "endpoint": endpoint,
        "completion_window": completion_window,
    }
    if metadata:
        batch_body["metadata"] = metadata

    code, batch_resp = _request_json(
        f"{api_base}/batches",
        api_key=api_key,
        method="POST",
        json_body=batch_body,
        timeout=timeout,
    )
    if code >= 400 or not isinstance(batch_resp, dict):
        msg = batch_resp.get("error", {}).get("message", str(batch_resp)) if isinstance(batch_resp, dict) else "non-JSON response"
        return _error_result(f"batch create failed (HTTP {code}): {msg}", timestamp, start_time)

    return _success_result(batch_resp, timestamp, start_time, extra={
        "batch_id": batch_resp.get("id"),
        "input_file_id": file_id,
        "request_count": len(requests),
    })


def get_batch_status(
    batch_id: str,
    *,
    api_key: str | None = None,
    api_base: str = OPENAI_API_BASE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch a batch's current state."""
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = api_key or _get_api_key()
    if not api_key:
        return _error_result("OPENAI_API_KEY not set", timestamp, start_time)
    if not batch_id:
        return _error_result("'batch_id' is required", timestamp, start_time)

    code, resp = _request_json(
        f"{api_base}/batches/{batch_id}", api_key=api_key, timeout=timeout,
    )
    if code >= 400 or not isinstance(resp, dict):
        msg = resp.get("error", {}).get("message", str(resp)) if isinstance(resp, dict) else "non-JSON response"
        return _error_result(f"batch status failed (HTTP {code}): {msg}", timestamp, start_time)

    return _success_result(resp, timestamp, start_time, extra={
        "batch_id": resp.get("id"),
        "batch_status": resp.get("status"),
        "request_counts": resp.get("request_counts", {}),
    })


def get_batch_results(
    batch_id: str,
    *,
    api_key: str | None = None,
    api_base: str = OPENAI_API_BASE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Download and parse the output JSONL for a completed batch."""
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = api_key or _get_api_key()
    if not api_key:
        return _error_result("OPENAI_API_KEY not set", timestamp, start_time)
    if not batch_id:
        return _error_result("'batch_id' is required", timestamp, start_time)

    # 1) Get the batch to find output_file_id
    code, batch = _request_json(
        f"{api_base}/batches/{batch_id}", api_key=api_key, timeout=timeout,
    )
    if code >= 400 or not isinstance(batch, dict):
        msg = batch.get("error", {}).get("message", str(batch)) if isinstance(batch, dict) else "non-JSON response"
        return _error_result(f"batch lookup failed (HTTP {code}): {msg}", timestamp, start_time)

    if batch.get("status") != "completed":
        return _error_result(
            f"batch status is '{batch.get('status')}' (expected 'completed')",
            timestamp, start_time,
        )

    output_file_id = batch.get("output_file_id")
    if not output_file_id:
        return _error_result("batch has no output_file_id", timestamp, start_time)

    # 2) Download the output JSONL
    code, raw = _request_json(
        f"{api_base}/files/{output_file_id}/content",
        api_key=api_key, timeout=timeout,
    )
    if code >= 400:
        msg = raw.get("error", {}).get("message", str(raw)) if isinstance(raw, dict) else "non-JSON response"
        return _error_result(f"output download failed (HTTP {code}): {msg}", timestamp, start_time)

    if isinstance(raw, dict):
        return _error_result("output endpoint returned JSON instead of file", timestamp, start_time)

    parsed: list[dict[str, Any]] = []
    for line in io.BytesIO(raw):
        text = line.decode("utf-8", errors="replace").strip()
        if not text:
            continue
        try:
            parsed.append(json.loads(text))
        except json.JSONDecodeError:
            continue

    return _success_result(batch, timestamp, start_time, extra={
        "batch_id": batch.get("id"),
        "output_file_id": output_file_id,
        "results": parsed,
        "result_count": len(parsed),
    })


def cancel_batch(
    batch_id: str,
    *,
    api_key: str | None = None,
    api_base: str = OPENAI_API_BASE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Cancel an in-flight batch."""
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = api_key or _get_api_key()
    if not api_key:
        return _error_result("OPENAI_API_KEY not set", timestamp, start_time)
    if not batch_id:
        return _error_result("'batch_id' is required", timestamp, start_time)

    code, resp = _request_json(
        f"{api_base}/batches/{batch_id}/cancel",
        api_key=api_key, method="POST", timeout=timeout,
    )
    if code >= 400 or not isinstance(resp, dict):
        msg = resp.get("error", {}).get("message", str(resp)) if isinstance(resp, dict) else "non-JSON response"
        return _error_result(f"batch cancel failed (HTTP {code}): {msg}", timestamp, start_time)

    return _success_result(resp, timestamp, start_time, extra={
        "batch_id": resp.get("id"),
        "batch_status": resp.get("status"),
    })


def list_batches(
    *,
    api_key: str | None = None,
    limit: int = 20,
    after: str | None = None,
    api_base: str = OPENAI_API_BASE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """List recent batches (newest first)."""
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    api_key = api_key or _get_api_key()
    if not api_key:
        return _error_result("OPENAI_API_KEY not set", timestamp, start_time)

    url = f"{api_base}/batches?limit={int(limit)}"
    if after:
        url += f"&after={after}"
    code, resp = _request_json(url, api_key=api_key, timeout=timeout)
    if code >= 400 or not isinstance(resp, dict):
        msg = resp.get("error", {}).get("message", str(resp)) if isinstance(resp, dict) else "non-JSON response"
        return _error_result(f"batch list failed (HTTP {code}): {msg}", timestamp, start_time)

    data = resp.get("data", [])
    return _success_result(resp, timestamp, start_time, extra={
        "batches": data,
        "count": len(data),
        "has_more": resp.get("has_more", False),
    })


def wait_for_batch(
    batch_id: str,
    *,
    api_key: str | None = None,
    timeout_s: int = _DEFAULT_WAIT_TIMEOUT_S,
    poll_interval_s: int = _DEFAULT_POLL_INTERVAL_S,
    api_base: str = OPENAI_API_BASE,
    sleep_fn: "callable | None" = None,
    now_fn: "callable | None" = None,
) -> dict[str, Any]:
    """Poll a batch until terminal state or ``timeout_s`` elapses (v2.5.0).

    Terminal states: ``completed | failed | expired | cancelled | canceling``.

    ``sleep_fn`` and ``now_fn`` are injectable for deterministic testing.

    Returns the final ATP-shaped envelope plus:
      - ``waited_s``   total wall-clock seconds waited
      - ``poll_count`` number of GET /v1/batches/{id} calls issued
      - ``timed_out``  True if the wait hit ``timeout_s`` first
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    if not batch_id:
        return _error_result("'batch_id' is required", timestamp, start_time)

    sleep = sleep_fn or time.sleep
    now = now_fn or time.monotonic
    wait_start = now()
    poll_count = 0
    last_result: dict[str, Any] = {}

    while True:
        poll_count += 1
        last_result = get_batch_status(batch_id, api_key=api_key,
                                       api_base=api_base, timeout=DEFAULT_TIMEOUT_SECONDS)
        if last_result.get("status") == "failed":
            last_result["waited_s"] = round(now() - wait_start, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = False
            return last_result

        batch_status = (last_result.get("batch_status") or "").lower()
        if batch_status in _TERMINAL_BATCH_STATES:
            last_result["waited_s"] = round(now() - wait_start, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = False
            return last_result

        elapsed = now() - wait_start
        if elapsed >= timeout_s:
            last_result["status"] = "timeout"
            last_result["error"] = (
                f"openai-batch wait: batch {batch_id} did not reach terminal "
                f"state within {timeout_s}s (last status: {batch_status})"
            )
            last_result["waited_s"] = round(elapsed, 3)
            last_result["poll_count"] = poll_count
            last_result["timed_out"] = True
            return last_result
        sleep(poll_interval_s)


# ---------------------------------------------------------------------------
# Bridge dispatcher: routes incoming["action"] to the right function
# ---------------------------------------------------------------------------


def dispatch(incoming: dict[str, Any]) -> dict[str, Any]:
    """Route ``adapter='openai-batch'`` bridge requests by ``action``."""
    action = (incoming.get("action") or "").strip()
    api_key = incoming.get("api_key")

    if action == "create":
        return create_batch(
            incoming.get("requests") or [],
            api_key=api_key,
            completion_window=incoming.get("completion_window", DEFAULT_COMPLETION_WINDOW),
            endpoint=incoming.get("endpoint", "/v1/chat/completions"),
            metadata=incoming.get("metadata"),
        )
    if action == "status":
        return get_batch_status(incoming.get("batch_id", ""), api_key=api_key)
    if action == "results":
        return get_batch_results(incoming.get("batch_id", ""), api_key=api_key)
    if action == "cancel":
        return cancel_batch(incoming.get("batch_id", ""), api_key=api_key)
    if action == "list":
        return list_batches(api_key=api_key, limit=incoming.get("limit", 20),
                            after=incoming.get("after"))
    if action == "wait":
        return wait_for_batch(
            incoming.get("batch_id", ""),
            api_key=api_key,
            timeout_s=int(incoming.get("timeout_s", _DEFAULT_WAIT_TIMEOUT_S)),
            poll_interval_s=int(incoming.get("poll_interval_s", _DEFAULT_POLL_INTERVAL_S)),
        )
    return {
        "status": "failed",
        "provider": "openai-batch",
        "error": f"unknown action '{action}' (expected: create | status | results | cancel | list | wait)",
    }
