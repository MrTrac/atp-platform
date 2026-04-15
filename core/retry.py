"""Retry/backoff for transient errors in ATP cloud adapters.

Implements exponential backoff with jitter for 429 (rate limit) and
network errors. Cap on total wait time. Honors Retry-After header
when present.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar
from urllib.error import HTTPError, URLError


T = TypeVar("T")


DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 30.0  # seconds
DEFAULT_MAX_TOTAL_WAIT = 120.0  # seconds


def _is_retryable(exc: Exception) -> bool:
    """Determine if an exception represents a transient error worth retrying."""
    if isinstance(exc, HTTPError):
        # 429 = rate limit; 502/503/504 = transient gateway errors
        return exc.code in (429, 502, 503, 504)
    if isinstance(exc, URLError):
        # Network errors are transient (DNS, connection refused, timeout)
        return True
    return False


def _retry_after_seconds(exc: Exception) -> float | None:
    """Extract Retry-After header value (seconds) from HTTPError."""
    if not isinstance(exc, HTTPError):
        return None
    try:
        retry_after = exc.headers.get("Retry-After")
        if retry_after:
            return float(retry_after)
    except (AttributeError, ValueError, TypeError):
        pass
    return None


def _calculate_delay(attempt: int, base: float, max_delay: float, retry_after: float | None) -> float:
    """Calculate next backoff delay with jitter."""
    if retry_after is not None and retry_after > 0:
        return min(retry_after, max_delay)
    # Exponential: base * 2^attempt (attempt is 0-indexed)
    exp_delay = base * (2 ** attempt)
    jitter = random.uniform(0, exp_delay * 0.25)
    return min(exp_delay + jitter, max_delay)


def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    max_total_wait: float = DEFAULT_MAX_TOTAL_WAIT,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> T:
    """Execute fn with exponential backoff retry on transient errors.

    Parameters
    ----------
    fn : callable
        Zero-argument callable returning the result.
    max_attempts : int
        Total attempts including the first try (default 3).
    base_delay : float
        Base delay in seconds (default 1.0).
    max_delay : float
        Cap per-attempt delay (default 30.0s).
    max_total_wait : float
        Cap cumulative wait time (default 120s).
    sleep_fn : callable
        Sleep function (overridable for tests).

    Returns
    -------
    The result of fn() if successful.

    Raises
    ------
    The last exception if all retries exhausted, or if a non-retryable
    error is raised.
    """
    last_exc: Exception | None = None
    total_waited = 0.0

    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if not _is_retryable(exc):
                raise
            if attempt >= max_attempts - 1:
                # No more attempts
                break

            retry_after = _retry_after_seconds(exc)
            delay = _calculate_delay(attempt, base_delay, max_delay, retry_after)

            if total_waited + delay > max_total_wait:
                # Would exceed total budget
                break

            sleep_fn(delay)
            total_waited += delay

    assert last_exc is not None
    raise last_exc
