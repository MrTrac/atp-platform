"""Settings every test needs, whichever directory it lives in."""

from __future__ import annotations

import pytest

_AIOS_FLOW_IDENTITY_ENV = ("AIOS_FLOW_IDENTITY_URL", "AIOS_FLOW_IDENTITY_SECRET", "AIOS_FLOW_IDENTITY_USER")


@pytest.fixture(autouse=True)
def _no_ambient_aios_flow_identity(monkeypatch):
    """The aios-flow adapter authenticates when AIOS_FLOW_IDENTITY_URL is set. A developer's shell (or a CI job) that has it set must not make an unrelated test
    mint a real token or send a real secret, so every test starts with the variables unset and with no cached provider; tests that want authentication set them."""
    from adapters.aios_flow import identity_token

    for name in _AIOS_FLOW_IDENTITY_ENV:
        monkeypatch.delenv(name, raising=False)
    identity_token.reset_provider()
    yield
    identity_token.reset_provider()


@pytest.fixture(autouse=True)
def _never_write_the_real_g9_trace(monkeypatch, tmp_path):
    """`core.trace.record_trace` appends to ~/.aios/state/cross_module_trace.jsonl, the ecosystem's real cross-module trace. A test that calls it unmocked would add
    fake records there (14/10/2026: 2,200 fake `aios-identity` records from the first runs of the identity-token tests). Every test therefore writes to its own
    temporary file; the few tests that inspect the trace set `_TRACE_FILE` themselves and override this."""
    monkeypatch.setattr("core.trace._TRACE_FILE", tmp_path / "cross_module_trace.jsonl")
    yield
