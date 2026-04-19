"""
ATP Adapter: claude-code-subprocess

Bridges AIOS-OC FlowView's claude-code-agent node to the Claude Code CLI
subprocess on the local Mac.

Architecture:
    AIOS-OC FlowView node
        → ATP bridge (POST /run)
            → ClaudeCodeAdapter.execute()
                → subprocess: claude -p <prompt> --model <model>
                    → stdout collected + optional SSE stream back to AIOS-OC
"""

from __future__ import annotations

import asyncio
import dataclasses
import os
import pathlib
import signal
from typing import Any, AsyncIterator


@dataclasses.dataclass
class AdapterResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    error: str | None = None
    outputs: dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "error": self.error,
            "outputs": self.outputs,
        }


class ClaudeCodeAdapterConfig:
    """Configuration for the claude-code adapter."""

    MODEL_MAP = {
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-7",
        "haiku": "claude-haiku-4-5-20251001",
    }

    def __init__(
        self,
        repo: str,
        template: str,
        model: str = "sonnet",
        timeout_seconds: int = 7200,
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

    @property
    def model_id(self) -> str:
        return self.MODEL_MAP.get(self.model, self.model)

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "template": self.template,
            "model": self.model,
            "model_id": self.model_id,
            "timeout_seconds": self.timeout_seconds,
            "branch": self.branch,
            "scope": self.scope,
            "playbooks_dir": self.playbooks_dir,
            "max_tokens": self.max_tokens,
        }


class ClaudeCodeAdapter:
    """ATP adapter for Claude Code subprocess execution."""

    ADAPTER_ID = "claude-code"
    VERSION = "0.1.0"

    def __init__(self, config: ClaudeCodeAdapterConfig) -> None:
        self.config = config
        self._process: asyncio.subprocess.Process | None = None
        self._stdout_lines: list[str] = []

    async def validate(self) -> tuple[bool, str]:
        """Validate adapter prerequisites."""
        # Check claude CLI
        proc = await asyncio.create_subprocess_exec(
            "claude", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode != 0:
            return False, "claude CLI not found in PATH"

        # Check repo exists
        repo_path = self._find_repo(self.config.repo)
        if not repo_path:
            return False, f"Repo not found: {self.config.repo}"

        # Check template exists
        tpl = self._resolve_template()
        if not tpl.exists():
            return False, f"Template not found: {tpl}"

        return True, "OK"

    async def execute(
        self,
        prompt_context: dict[str, Any] | None = None,
        approval_callback: Any | None = None,
    ) -> AdapterResult:
        """Execute Claude Code with the rendered prompt."""
        ok, msg = await self.validate()
        if not ok:
            return AdapterResult(success=False, error=msg)

        repo_path = self._find_repo(self.config.repo)
        assert repo_path is not None

        # Render template
        prompt = self._render_template(prompt_context or {})

        # Build command
        cmd = ["claude", "-p", prompt, "--model", self.config.model_id]
        if self.config.max_tokens:
            cmd += ["--max-tokens", str(self.config.max_tokens)]

        self._stdout_lines = []

        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ},
            )

            stdout_data, stderr_data = await asyncio.wait_for(
                self._process.communicate(),
                timeout=self.config.timeout_seconds,
            )

            stdout = stdout_data.decode(errors="replace")
            stderr = stderr_data.decode(errors="replace")
            self._stdout_lines = stdout.splitlines()
            rc = self._process.returncode or 0

            return AdapterResult(
                success=rc == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=rc,
                error=None if rc == 0 else f"claude exited with code {rc}",
            )

        except asyncio.TimeoutError:
            if self._process:
                self._process.kill()
            return AdapterResult(
                success=False,
                error=f"Timeout after {self.config.timeout_seconds}s",
                exit_code=-1,
            )
        except FileNotFoundError:
            return AdapterResult(success=False, error="claude CLI not found in PATH")
        except Exception as exc:
            return AdapterResult(success=False, error=str(exc))
        finally:
            self._process = None

    async def stream_stdout(self) -> AsyncIterator[str]:
        """Stream stdout lines from a running process.

        Must call execute() in a concurrent task while consuming this generator.
        Yields lines as they arrive from the process stdout.
        """
        if self._process is None or self._process.stdout is None:
            return
        async for line in self._process.stdout:
            decoded = line.decode(errors="replace").rstrip("\n")
            self._stdout_lines.append(decoded)
            yield decoded

    async def abort(self) -> None:
        """Terminate the running Claude Code process (SIGTERM → SIGKILL)."""
        if self._process is None:
            return
        try:
            self._process.send_signal(signal.SIGTERM)
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()
        except ProcessLookupError:
            pass

    async def pause(self) -> None:
        """Pause the Claude Code process (SIGSTOP)."""
        if self._process is None:
            return
        try:
            self._process.send_signal(signal.SIGSTOP)
        except ProcessLookupError:
            pass

    async def resume(self) -> None:
        """Resume a paused Claude Code process (SIGCONT)."""
        if self._process is None:
            return
        try:
            self._process.send_signal(signal.SIGCONT)
        except ProcessLookupError:
            pass

    def _find_repo(self, name: str) -> pathlib.Path | None:
        """Locate a repo by name under ~/SOURCE_DEV/."""
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

    def _render_template(self, context: dict[str, Any]) -> str:
        """Render the prompt template with context + optional scope injection."""
        from jinja2 import Environment, Undefined
        import datetime

        tpl_path = self._resolve_template()
        template_str = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""

        now = datetime.datetime.now()
        base_ctx: dict[str, Any] = {
            "now": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "repo": self.config.repo,
            "model": self.config.model,
            "branch": self.config.branch or "main",
            **context,
        }

        env = Environment(undefined=Undefined)
        rendered = env.from_string(template_str).render(**base_ctx)

        if self.config.scope:
            scope_rendered = env.from_string(self.config.scope).render(**base_ctx)
            rendered = f"{rendered}\n\n## Scope\n\n{scope_rendered}"

        return rendered
