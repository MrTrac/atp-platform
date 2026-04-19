"""
ATP Adapter: codex-subprocess

Bridges AIOS-OC FlowView's `codex-agent` node to the OpenAI `codex` CLI
subprocess on the local Mac.

Architecture (mirrors claude_code.py):
    AIOS-OC FlowView `codex-agent` node
        → ATP bridge (POST /run, adapter="codex")
            → CodexAdapter.execute()
                → subprocess: codex exec --model <model> <prompt>
                    → stdout collected back to AIOS-OC

Requires:
- `codex` CLI on PATH (install via `npm i -g @openai/codex`).
- `OPENAI_API_KEY` in the ATP bridge environment (launchd plist).
"""

from __future__ import annotations

import asyncio
import dataclasses
import os
import pathlib
import signal
from typing import Any

from .claude_code import AdapterResult  # shared dataclass


class CodexAdapterConfig:
    """Configuration for the codex adapter."""

    # Identity-mapping by default — templates use the model id as shipped.
    MODEL_MAP = {
        "gpt-5-pro": "gpt-5-pro",
        "gpt-5-thinking": "gpt-5-thinking",
        "gpt-4o": "gpt-4o",
    }

    def __init__(
        self,
        repo: str,
        template: str,
        model: str = "gpt-5-pro",
        timeout_seconds: int = 7200,
        branch: str | None = None,
        scope: str | None = None,
        playbooks_dir: str = "~/SOURCE_DEV/meta/claude-playbooks",
        max_tokens: int = 200_000,
        workspace_dir: str | None = None,
        isolation: str = "direct",
    ) -> None:
        self.repo = repo
        self.template = template
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.branch = branch
        self.scope = scope
        self.playbooks_dir = playbooks_dir
        self.max_tokens = max_tokens
        # Accepted for interface parity with ClaudeCodeAdapter — not yet used
        # by the Codex CLI subprocess flow, but captured so the dispatcher
        # doesn't need adapter-specific conditionals.
        self.workspace_dir = workspace_dir
        self.isolation = isolation

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


class CodexAdapter:
    """ATP adapter for OpenAI `codex` CLI subprocess execution."""

    ADAPTER_ID = "codex"
    VERSION = "0.1.0"
    CLI_BIN = "codex"

    def __init__(self, config: CodexAdapterConfig) -> None:
        self.config = config
        self._process: asyncio.subprocess.Process | None = None
        self._stdout_lines: list[str] = []

    async def validate(self) -> tuple[bool, str]:
        """Validate adapter prerequisites."""
        # Check codex CLI
        try:
            proc = await asyncio.create_subprocess_exec(
                self.CLI_BIN, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            if proc.returncode != 0:
                return False, f"{self.CLI_BIN} CLI not found in PATH (install via `npm i -g @openai/codex`)"
        except FileNotFoundError:
            return False, f"{self.CLI_BIN} CLI not found in PATH (install via `npm i -g @openai/codex`)"

        # Require OPENAI_API_KEY
        if not os.environ.get("OPENAI_API_KEY"):
            return False, "OPENAI_API_KEY not set in ATP bridge environment"

        repo_path = self._find_repo(self.config.repo)
        if not repo_path:
            return False, f"Repo not found: {self.config.repo}"

        tpl = self._resolve_template()
        if not tpl.exists():
            return False, f"Template not found: {tpl}"

        return True, "OK"

    async def execute(
        self,
        prompt_context: dict[str, Any] | None = None,
        approval_callback: Any | None = None,
    ) -> AdapterResult:
        """Execute Codex CLI with the rendered prompt."""
        ok, msg = await self.validate()
        if not ok:
            return AdapterResult(success=False, error=msg)

        repo_path = self._find_repo(self.config.repo)
        assert repo_path is not None

        prompt = self._render_template(prompt_context or {})

        # `codex exec` runs a single-shot agent non-interactively. Adjust
        # subcommand if the installed `codex` CLI uses different syntax.
        cmd = [self.CLI_BIN, "exec", "--model", self.config.model_id, prompt]

        self._stdout_lines = []
        child_env = dict(os.environ)  # inherit OPENAI_API_KEY + PATH

        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=child_env,
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
                error=None if rc == 0 else f"{self.CLI_BIN} exited with code {rc}",
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
            return AdapterResult(success=False, error=f"{self.CLI_BIN} CLI not found in PATH")
        except Exception as exc:
            return AdapterResult(success=False, error=str(exc))
        finally:
            self._process = None

    async def abort(self) -> None:
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

    # ---- helpers (identical shape to ClaudeCodeAdapter) ----

    def _find_repo(self, name: str) -> pathlib.Path | None:
        base = pathlib.Path.home() / "SOURCE_DEV"
        for sub in ("platforms", "products", "meta"):
            p = base / sub / name
            if p.is_dir():
                return p
        return None

    def _resolve_template(self) -> pathlib.Path:
        playbooks = pathlib.Path(self.config.playbooks_dir).expanduser()
        return playbooks / self.config.template

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                return content[end + 3:].lstrip("\n")
        return content

    def _render_template(self, context: dict[str, Any]) -> str:
        from jinja2 import Environment, Undefined
        import datetime

        tpl_path = self._resolve_template()
        raw = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""
        template_str = self._strip_frontmatter(raw)

        now = datetime.datetime.now()
        base_ctx: dict[str, Any] = {
            "now": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "repo": self.config.repo,
            "model": self.config.model,
            "branch": self.config.branch or "main",
            "REPO": self.config.repo,
            "BRANCH": self.config.branch or "main",
            "MODEL": self.config.model,
            "SCOPE_SUMMARY": self.config.scope or "(no scope specified)",
            "ISO_TIMESTAMP": now.isoformat(),
            "NOW": now.isoformat(),
            "TIMESTAMP": now.strftime("%Y%m%d-%H%M%S"),
            "YYYYMMDD": now.strftime("%Y%m%d"),
            "YYYY": now.strftime("%Y"),
            "MM": now.strftime("%m"),
            "DD": now.strftime("%d"),
            "HHMM": now.strftime("%H%M"),
            "HH": now.strftime("%H"),
            "YYYYMMDD_HHMM": now.strftime("%Y%m%d-%H%M"),
            **context,
        }

        env = Environment(undefined=Undefined)
        rendered = env.from_string(template_str).render(**base_ctx)
        if self.config.scope:
            scope_rendered = env.from_string(self.config.scope).render(**base_ctx)
            rendered = f"{rendered}\n\n## Scope\n\n{scope_rendered}"
        return rendered
