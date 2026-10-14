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
