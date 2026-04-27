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
import json as _json
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
        # Workspace isolation — keeps runtime artifacts OUT of the repo.
        #   workspace_dir: absolute path where prompt.md/stdout.log/stderr.log/
        #                  result.json are written. If None, artifacts are only
        #                  returned in the AdapterResult (legacy behaviour).
        #   isolation: direct (cwd=repo), read-only (cwd=workspace_dir),
        #              worktree (cwd=workspace_dir/worktree, git worktree add).
        self.workspace_dir = workspace_dir
        if isolation not in ("direct", "read-only", "worktree"):
            isolation = "direct"
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
            "workspace_dir": self.workspace_dir,
            "isolation": self.isolation,
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

        # Resolve cwd based on isolation mode. workspace_dir (if set) is the
        # per-stage artifacts root — we also write prompt.md / stdout.log /
        # stderr.log / result.json there regardless of isolation mode.
        ws_path: pathlib.Path | None = None
        if self.config.workspace_dir:
            ws_path = pathlib.Path(self.config.workspace_dir).expanduser()
            ws_path.mkdir(parents=True, exist_ok=True)
            (ws_path / "artifacts").mkdir(exist_ok=True)
            # Persist prompt up-front for post-mortem even if the run times out.
            (ws_path / "prompt.md").write_text(prompt, encoding="utf-8")

        cwd, worktree_path = await self._resolve_cwd(repo_path, ws_path)

        # Build command — claude CLI uses --model; --max-tokens is not a valid flag
        cmd = ["claude", "-p", prompt, "--model", self.config.model_id]

        self._stdout_lines = []

        # Strip CLAUDECODE so nested `claude -p` isn't blocked by the
        # nested-session guard that Claude Code sets on its own env.
        child_env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        result: AdapterResult
        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(cwd),
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

            result = AdapterResult(
                success=rc == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=rc,
                error=None if rc == 0 else f"claude exited with code {rc}",
            )

        except asyncio.TimeoutError:
            if self._process:
                self._process.kill()
            result = AdapterResult(
                success=False,
                error=f"Timeout after {self.config.timeout_seconds}s",
                exit_code=-1,
            )
        except FileNotFoundError:
            result = AdapterResult(success=False, error="claude CLI not found in PATH")
        except Exception as exc:
            result = AdapterResult(success=False, error=str(exc))
        finally:
            self._process = None

        # Persist full artifacts to workspace (if configured).
        if ws_path is not None:
            try:
                (ws_path / "stdout.log").write_text(result.stdout or "", encoding="utf-8")
                (ws_path / "stderr.log").write_text(result.stderr or "", encoding="utf-8")
                (ws_path / "result.json").write_text(
                    _json.dumps(result.to_dict(), indent=2, default=str)
                )
                if worktree_path is not None and result.success:
                    # Capture git diff for the worktree so caller can preview
                    # before merging back.
                    diff = await self._worktree_diff(worktree_path)
                    if diff:
                        (ws_path / "artifacts" / "worktree.diff").write_text(diff)
            except Exception:
                pass  # artifact write failures should not mask the primary result

        return result

    async def _resolve_cwd(
        self,
        repo_path: pathlib.Path,
        ws_path: pathlib.Path | None,
    ) -> tuple[pathlib.Path, pathlib.Path | None]:
        """Pick the subprocess cwd based on isolation mode.

        Returns (cwd, worktree_path). worktree_path is only set for worktree mode.
        """
        if self.config.isolation == "direct" or ws_path is None:
            return repo_path, None

        if self.config.isolation == "read-only":
            ro_repo = ws_path / "ro-repo"
            if not ro_repo.exists():
                try:
                    ro_repo.symlink_to(repo_path, target_is_directory=True)
                except OSError:
                    ro_repo.mkdir()  # fallback — agent only writes to ws_path
            return ws_path, None

        if self.config.isolation == "worktree":
            wt_path = ws_path / "worktree"
            if not wt_path.exists():
                wt_branch = self.config.branch or f"atp-run-{wt_path.parent.name[:16]}"
                args_existing = ["git", "-C", str(repo_path), "worktree", "add", str(wt_path), wt_branch]
                args_new = ["git", "-C", str(repo_path), "worktree", "add", "-b", wt_branch, str(wt_path)]
                proc = await asyncio.create_subprocess_exec(
                    *args_existing,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, err = await proc.communicate()
                if proc.returncode != 0:
                    proc = await asyncio.create_subprocess_exec(
                        *args_new,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    _, err2 = await proc.communicate()
                    if proc.returncode != 0:
                        raise RuntimeError(
                            f"git worktree add failed: {err.decode()} / {err2.decode()}"
                        )
            return wt_path, wt_path

        return repo_path, None

    async def _worktree_diff(self, worktree_path: pathlib.Path) -> str:
        proc = await asyncio.create_subprocess_exec(
            "git", "-C", str(worktree_path), "diff", "HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode(errors="replace")

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

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        """Remove YAML --- frontmatter so it isn't parsed as a CLI flag."""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                return content[end + 3:].lstrip("\n")
        return content

    def _render_template(self, context: dict[str, Any]) -> str:
        """Render the prompt template with context + optional scope injection."""
        from jinja2 import Environment, Undefined
        import datetime

        tpl_path = self._resolve_template()
        raw = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""
        template_str = self._strip_frontmatter(raw)

        now = datetime.datetime.now()
        base_ctx: dict[str, Any] = {
            # lowercase aliases (existing)
            "now": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "repo": self.config.repo,
            "model": self.config.model,
            "branch": self.config.branch or "main",
            # Uppercase convention used by templates under
            # ~/SOURCE_DEV/meta/claude-playbooks/prompts/*.md
            # (e.g. `{{REPO}}`, `{{BRANCH}}`, `{{YYYYMMDD}}`, `{{MODEL}}`).
            # Without these, Jinja raised `'YYYYMMDD' is undefined` and the
            # flow failed before invoking the model.
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
            # Composite helpers (Jinja treats `YYYYMMDD-HHMM` as subtraction,
            # so we expose a pre-joined canonical key as well).
            "YYYYMMDD_HHMM": now.strftime("%Y%m%d-%H%M"),
            **context,
        }

        env = Environment(undefined=Undefined)
        rendered = env.from_string(template_str).render(**base_ctx)

        if self.config.scope:
            scope_rendered = env.from_string(self.config.scope).render(**base_ctx)
            rendered = f"{rendered}\n\n## Scope\n\n{scope_rendered}"

        return rendered
