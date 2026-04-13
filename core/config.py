"""Central configuration for ATP — single source of truth for all env vars.

All modules should import config values from here instead of reading
``os.environ`` directly. Call ``validate()`` at startup to catch missing
required values early.
"""

from __future__ import annotations

import os
from typing import NamedTuple


def _bool_env(key: str) -> bool:
    return os.environ.get(key, "").lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# Bridge server
# ---------------------------------------------------------------------------
BRIDGE_PORT: int = int(os.environ.get("ATP_BRIDGE_PORT", "8765"))
BRIDGE_CORS_ORIGIN: str = os.environ.get("ATP_BRIDGE_CORS_ORIGIN", "http://localhost:3000")
BRIDGE_MAX_BODY_BYTES: int = int(os.environ.get("ATP_BRIDGE_MAX_BODY", str(10 * 1024 * 1024)))  # 10 MB

# ---------------------------------------------------------------------------
# AOKP knowledge integration
# ---------------------------------------------------------------------------
AOKP_ENABLED: bool = _bool_env("ATP_AOKP_ENABLED")
AOKP_BASE_URL: str = os.environ.get("ATP_AOKP_URL", "http://localhost:3002")

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
PERSIST_ARTIFACTS: bool = _bool_env("ATP_PERSIST_ARTIFACTS")
PERSIST_RUNS: bool = _bool_env("ATP_PERSIST_RUNS")

# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
OLLAMA_BASE_URL: str = os.environ.get("ATP_OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT: int = int(os.environ.get("ATP_OLLAMA_TIMEOUT", "120"))
ANTHROPIC_TIMEOUT: int = int(os.environ.get("ATP_ANTHROPIC_TIMEOUT", "120"))

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
MODEL_ALLOWLIST: list[str] | None = None
_raw_allowlist = os.environ.get("ATP_MODEL_ALLOWLIST", "")
if _raw_allowlist.strip():
    MODEL_ALLOWLIST = [m.strip() for m in _raw_allowlist.split(",") if m.strip()]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ConfigWarning(NamedTuple):
    key: str
    message: str


def validate() -> list[ConfigWarning]:
    """Validate configuration at startup. Returns warnings for missing optional values."""
    warnings: list[ConfigWarning] = []

    if BRIDGE_PORT < 1 or BRIDGE_PORT > 65535:
        warnings.append(ConfigWarning("ATP_BRIDGE_PORT", f"Invalid port: {BRIDGE_PORT}"))

    if not ANTHROPIC_API_KEY:
        warnings.append(ConfigWarning("ANTHROPIC_API_KEY", "Not set — cloud escalation will fail"))

    if AOKP_ENABLED and not AOKP_BASE_URL:
        warnings.append(ConfigWarning("ATP_AOKP_URL", "AOKP enabled but URL not set"))

    return warnings


def summary() -> dict[str, object]:
    """Return config summary for /status endpoint and logging."""
    return {
        "bridge_port": BRIDGE_PORT,
        "bridge_cors_origin": BRIDGE_CORS_ORIGIN,
        "bridge_max_body_bytes": BRIDGE_MAX_BODY_BYTES,
        "aokp_enabled": AOKP_ENABLED,
        "aokp_base_url": AOKP_BASE_URL if AOKP_ENABLED else None,
        "persist_artifacts": PERSIST_ARTIFACTS,
        "persist_runs": PERSIST_RUNS,
        "anthropic_api_key_set": ANTHROPIC_API_KEY is not None,
        "ollama_base_url": OLLAMA_BASE_URL,
        "model_allowlist": MODEL_ALLOWLIST,
    }
