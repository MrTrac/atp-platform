"""The environment of a child process that runs an LLM agent (`claude -p`, `codex exec`, `cursor-agent`).

An agent acts on prompts that came from outside ATP and can run commands, so whatever is in its environment it can print. Credentials that only ATP's own code needs
must not be there: `AIOS_FLOW_IDENTITY_SECRET` is the secret of the service account that starts aios-flow runs (adapters/aios_flow/identity_token.py). Keys the agent
itself needs (ANTHROPIC_API_KEY, OPENAI_API_KEY, PATH, ...) are passed through untouched.

This is defence in depth, not a boundary: the agent runs as the same OS user as ATP and could read the secret from elsewhere (the macOS login Keychain, the
parent's /proc entry on Linux). It removes the free read, and keeps the secret out of any log or transcript that records an agent's environment.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping

ATP_ONLY_SECRETS = ("AIOS_FLOW_IDENTITY_SECRET",)


def agent_environ(base: Mapping[str, str] | None = None, *, drop: Iterable[str] = ()) -> dict[str, str]:
    """A copy of `base` (default: this process's environment) without the ATP-only secrets and without the names in `drop`."""
    source = os.environ if base is None else base
    banned = set(ATP_ONLY_SECRETS) | set(drop)
    return {name: value for name, value in source.items() if name not in banned}
