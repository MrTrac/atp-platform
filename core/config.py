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
OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
OLLAMA_BASE_URL: str = os.environ.get("ATP_OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT: int = int(os.environ.get("ATP_OLLAMA_TIMEOUT", "120"))
ANTHROPIC_TIMEOUT: int = int(os.environ.get("ATP_ANTHROPIC_TIMEOUT", "120"))
OPENAI_TIMEOUT: int = int(os.environ.get("ATP_OPENAI_TIMEOUT", "300"))  # higher for o1 reasoning models

# Per-model timeout overrides (comma-separated key=value pairs).
# Example: ATP_MODEL_TIMEOUTS="o1=600,o1-preview=600,gpt-5=300"
MODEL_TIMEOUTS: dict[str, int] = {}
_raw_timeouts = os.environ.get("ATP_MODEL_TIMEOUTS", "")
if _raw_timeouts.strip():
    for pair in _raw_timeouts.split(","):
        if "=" in pair:
            k, _, v = pair.partition("=")
            try:
                MODEL_TIMEOUTS[k.strip()] = int(v.strip())
            except ValueError:
                pass


def get_timeout_for_model(model: str, default: int) -> int:
    """Return the configured timeout for a specific model, or the default."""
    return MODEL_TIMEOUTS.get(model, default)

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
        warnings.append(ConfigWarning("ANTHROPIC_API_KEY", "Not set — Anthropic cloud calls will require api_key in request"))

    if not OPENAI_API_KEY:
        warnings.append(ConfigWarning("OPENAI_API_KEY", "Not set — OpenAI cloud calls will require api_key in request"))

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
        "openai_api_key_set": OPENAI_API_KEY is not None,
        "ollama_base_url": OLLAMA_BASE_URL,
        "ollama_timeout": OLLAMA_TIMEOUT,
        "anthropic_timeout": ANTHROPIC_TIMEOUT,
        "openai_timeout": OPENAI_TIMEOUT,
        "model_timeouts": MODEL_TIMEOUTS,
        "model_allowlist": MODEL_ALLOWLIST,
    }
