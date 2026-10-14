"""core/child_env.py — the environment of a child process that runs an LLM agent must not carry ATP-only secrets (found by an independent review, 14/10/2026: the
agent adapters pass the whole environment, and AIOS_FLOW_IDENTITY_SECRET is now in it)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.child_env import ATP_ONLY_SECRETS, agent_environ

_ROOT = Path(__file__).resolve().parents[2]
_AGENT_ADAPTERS = ("adapters/claude_code.py", "adapters/codex.py", "adapters/cursor.py")


def test_the_identity_secret_is_not_handed_to_an_agent_but_everything_it_needs_is(monkeypatch):
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_SECRET", "must-not-reach-an-agent-0123456789")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-keep")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-keep-too")
    monkeypatch.setenv("AIOS_FLOW_IDENTITY_URL", "https://identity.example/identity")  # not a secret: stays
    env = agent_environ()
    assert "AIOS_FLOW_IDENTITY_SECRET" not in env
    assert env["ANTHROPIC_API_KEY"] == "sk-keep" and env["OPENAI_API_KEY"] == "sk-keep-too" and "PATH" in env
    assert env["AIOS_FLOW_IDENTITY_URL"] == "https://identity.example/identity"


def test_names_can_be_dropped_in_addition_and_an_explicit_base_is_respected(monkeypatch):
    assert agent_environ({"A": "1", "CLAUDECODE": "1", "AIOS_FLOW_IDENTITY_SECRET": "s"}, drop=("CLAUDECODE",)) == {"A": "1"}
    source = {"A": "1"}
    out = agent_environ(source)
    out["B"] = "2"
    assert source == {"A": "1"}  # a copy


@pytest.mark.parametrize("path", _AGENT_ADAPTERS)
def test_every_agent_adapter_builds_its_child_environment_through_the_helper(path):
    """A static guard, because a spawn that quietly goes back to `dict(os.environ)` would pass every behaviour test."""
    tree = ast.parse((_ROOT / path).read_text(encoding="utf-8"))
    assigned = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "child_env" for t in n.targets)]
    assert assigned, f"{path}: no `child_env =` assignment found: the guard would pass vacuously"
    for node in assigned:
        assert isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "agent_environ", f"{path}:{node.lineno} builds child_env without agent_environ()"


def test_the_list_names_the_identity_secret():
    assert "AIOS_FLOW_IDENTITY_SECRET" in ATP_ONLY_SECRETS
