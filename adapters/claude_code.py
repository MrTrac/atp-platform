"""
ATP Adapter: claude-code-subprocess

Stub implementation — skeleton only. NOT registered, NOT functional.
Full implementation deferred to Session 2-3 (Gate 2).

Purpose:
    Bridge between AIOS-OC FlowView's claude-code-agent node type and
    actual Claude Code CLI subprocess execution on the local Mac (or RHEL).

Architecture:
    AIOS-OC FlowView node
        → ATP bridge (POST /run)
            → ClaudeCodeAdapter.execute()
                → subprocess: claude -p <prompt> --model <model>
                    → stdout streamed via SSE back to AIOS-OC

Registration (DO NOT UNCOMMENT until Gate 2):
    # from .claude_code import ClaudeCodeAdapter
    # registry.register("claude-code", ClaudeCodeAdapter)
"""

from __future__ import annotations

import asyncio
import pathlib
from typing import Any, AsyncIterator

# Imports for future implementation — may need adjustment at impl time
# from ..core.base_adapter import BaseAdapter, AdapterResult
# from ..core.governance import GovernanceGuard
# from ..registry import AdapterRegistry


class ClaudeCodeAdapterConfig:
    """Configuration schema for the claude-code adapter.

    Defined here so FlowView node config validation can import this
    without requiring full adapter to be operational.
    """

    def __init__(
        self,
        repo: str,
        template: str,
        model: str = "sonnet",
        timeout_seconds: int = 7200,  # 2h default
        branch: str | None = None,
        scope: str | None = None,
        playbooks_dir: str = "~/SOURCE_DEV/meta/claude-playbooks",
        max_tokens: int = 200_000,
    ) -> None:
        self.repo = repo
        self.template = template
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.branch = branch
        self.scope = scope
        self.playbooks_dir = playbooks_dir
        self.max_tokens = max_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "template": self.template,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "branch": self.branch,
            "scope": self.scope,
            "playbooks_dir": self.playbooks_dir,
            "max_tokens": self.max_tokens,
        }


class ClaudeCodeAdapter:
    """ATP adapter for Claude Code subprocess execution.

    STUB — method signatures + docstrings only.
    All methods raise NotImplementedError until Session 2-3.
    """

    ADAPTER_ID = "claude-code"
    VERSION = "0.0.0-stub"

    def __init__(self, config: ClaudeCodeAdapterConfig) -> None:
        self.config = config
        self._process: asyncio.subprocess.Process | None = None

    async def validate(self) -> tuple[bool, str]:
        """Validate that adapter prerequisites are met.

        Checks:
        - claude CLI available in PATH
        - repo exists at expected path
        - template file exists in playbooks_dir
        - aios-gate passes validate_project(repo)

        Returns:
            (ok: bool, message: str)
        """
        raise NotImplementedError("Implement in Session 2-3")

    async def execute(
        self,
        prompt_context: dict[str, Any],
        approval_callback: Any | None = None,
    ) -> "AdapterResult":  # type: ignore[name-defined]
        """Execute Claude Code with the given prompt context.

        Steps:
        1. Resolve repo path (find_repo)
        2. Load + render template via Jinja2
        3. Optionally checkout/create branch
        4. Spawn: claude -p <rendered_prompt> --model <model>
        5. Stream stdout via SSE to AIOS-OC
        6. On completion: run aios-gate validate_project(repo)
        7. Return AdapterResult with stdout, exit_code, outputs

        Args:
            prompt_context: Jinja2 variables available in template
            approval_callback: Optional async callable for mid-run approvals

        Returns:
            AdapterResult with success, stdout, stderr, exit_code, outputs
        """
        raise NotImplementedError("Implement in Session 2-3")

    async def stream_stdout(self) -> AsyncIterator[str]:
        """Stream stdout lines from running Claude Code process.

        Yields lines as they arrive. Used by AIOS-OC SSE endpoint.

        Usage:
            async for line in adapter.stream_stdout():
                await sse_queue.put(line)
        """
        raise NotImplementedError("Implement in Session 2-3")
        yield  # make it a generator

    async def abort(self) -> None:
        """Abort the running Claude Code process.

        Sends SIGTERM, waits 5s, then SIGKILL.
        Updates agent_sessions record status to 'aborted'.
        """
        raise NotImplementedError("Implement in Session 2-3")

    async def pause(self) -> None:
        """Pause the Claude Code process (SIGSTOP).

        Updates agent_sessions.status to 'paused'.
        Note: Claude Code may not handle SIGSTOP gracefully — verify.
        """
        raise NotImplementedError("Implement in Session 2-3")

    async def resume(self) -> None:
        """Resume a paused Claude Code process (SIGCONT).

        Updates agent_sessions.status to 'active'.
        """
        raise NotImplementedError("Implement in Session 2-3")

    def _find_repo(self, name: str) -> pathlib.Path | None:
        """Locate repo by name under ~/SOURCE_DEV/."""
        base = pathlib.Path.home() / "SOURCE_DEV"
        for sub in ("platforms", "products", "meta"):
            p = base / sub / name
            if p.is_dir():
                return p
        return None

    def _resolve_template(self) -> pathlib.Path:
        """Resolve template path relative to playbooks_dir."""
        playbooks = pathlib.Path(self.config.playbooks_dir).expanduser()
        return playbooks / self.config.template
