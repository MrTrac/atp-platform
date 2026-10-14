"""Unit tests for ClaudeCodeAdapter (L3 integration)."""
from __future__ import annotations

import asyncio
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from adapters.claude_code import (
    AdapterResult,
    ClaudeCodeAdapter,
    ClaudeCodeAdapterConfig,
)


class TestClaudeCodeAdapterConfig(unittest.TestCase):
    def test_model_id_sonnet(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="AOKP", template="prompts/01.md", model="sonnet")
        assert cfg.model_id == "claude-sonnet-4-6"

    def test_model_id_opus(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="AOKP", template="prompts/01.md", model="opus")
        assert cfg.model_id == "claude-opus-4-7"

    def test_model_id_passthrough(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="AOKP", template="prompts/01.md", model="claude-custom-x")
        assert cfg.model_id == "claude-custom-x"

    def test_to_dict_contains_keys(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="AOKP", template="t.md", branch="feat/x")
        d = cfg.to_dict()
        assert d["repo"] == "AOKP"
        assert d["branch"] == "feat/x"
        assert "model_id" in d


class TestClaudeCodeAdapterValidate(unittest.TestCase):
    def test_repo_not_found(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="NONEXISTENT_REPO_XYZ", template="t.md")
        adapter = ClaudeCodeAdapter(cfg)

        async def _run() -> tuple[bool, str]:
            # Patch claude --version to succeed
            with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
                proc = MagicMock()
                proc.returncode = 0
                proc.communicate = AsyncMock(return_value=(b"1.0", b""))
                mock_proc.return_value = proc
                return await adapter.validate()

        ok, msg = asyncio.run(_run())
        assert not ok
        assert "not found" in msg

    def test_template_not_found(self) -> None:
        cfg = ClaudeCodeAdapterConfig(
            repo="ATP",
            template="prompts/DOES_NOT_EXIST.md",
        )
        adapter = ClaudeCodeAdapter(cfg)

        async def _run() -> tuple[bool, str]:
            # The repo must RESOLVE for validate() to reach the template check. Resolving "ATP" by name only works on a machine that has an ATP checkout
            # in the expected place (the author's Mac); on CI it gave "Repo not found: ATP". Make the test hermetic.
            with tempfile.TemporaryDirectory() as repo_dir, \
                    patch.object(ClaudeCodeAdapter, "_find_repo", return_value=pathlib.Path(repo_dir)), \
                    patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
                proc = MagicMock()
                proc.returncode = 0
                proc.communicate = AsyncMock(return_value=(b"1.0", b""))
                mock_proc.return_value = proc
                return await adapter.validate()

        ok, msg = asyncio.run(_run())
        assert not ok
        assert "Template not found" in msg


class TestClaudeCodeAdapterExecute(unittest.TestCase):
    def test_execute_success(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="ATP", template="prompts/01.md")
        adapter = ClaudeCodeAdapter(cfg)

        async def _run() -> AdapterResult:
            with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
                proc = MagicMock()
                proc.returncode = 0
                proc.stdout = None
                proc.communicate = AsyncMock(return_value=(b"agent output ok", b""))
                mock_exec.return_value = proc
                with patch.object(adapter, "_find_repo", return_value=pathlib.Path("/tmp")):
                    with patch.object(adapter, "_render_template", return_value="rendered prompt"):
                        with patch.object(adapter, "validate", new_callable=AsyncMock, return_value=(True, "OK")):
                            return await adapter.execute()

        result = asyncio.run(_run())
        assert result.success
        assert "agent output ok" in result.stdout

    def test_execute_validate_fail(self) -> None:
        cfg = ClaudeCodeAdapterConfig(repo="NONEXISTENT", template="t.md")
        adapter = ClaudeCodeAdapter(cfg)

        async def _run() -> AdapterResult:
            with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
                proc = MagicMock()
                proc.returncode = 1
                proc.communicate = AsyncMock(return_value=(b"", b"not found"))
                mock_proc.return_value = proc
                return await adapter.execute()

        result = asyncio.run(_run())
        assert not result.success
        assert result.error is not None

    def test_execute_timeout(self) -> None:
        """A hung `claude` process must be killed and reported as a timeout, through the REAL asyncio.wait_for.

        The first version patched asyncio.wait_for to raise TimeoutError at once. That skipped the timeout mechanism altogether: it never checked that
        `timeout_seconds` reaches it, never asserted the process is killed (default timeout is 7200 s, so a missing kill() leaves an orphan `claude`
        running for hours and the test stayed green — measured 14/10/2026 by removing the kill), and left the `communicate()` coroutine un-awaited, which is
        the RuntimeWarning that showed in every run (KD-ATP-008). Here wait_for is real, so the hung coroutine is cancelled and awaited like in production.
        """
        import time

        # A float is fine at runtime (the annotation says int); 0.05 s keeps the test fast while still going through a real timeout.
        cfg = ClaudeCodeAdapterConfig(repo="ATP", template="t.md", timeout_seconds=0.05)
        adapter = ClaudeCodeAdapter(cfg)
        communicate_started = []

        proc = MagicMock()
        proc.returncode = None
        proc.kill = MagicMock()

        async def _hang(*args: object, **kwargs: object) -> None:
            communicate_started.append(True)
            await asyncio.sleep(999)

        proc.communicate = _hang

        async def _run() -> AdapterResult:
            with patch.object(adapter, "validate", new_callable=AsyncMock, return_value=(True, "OK")):
                with patch.object(adapter, "_find_repo", return_value=pathlib.Path("/tmp")):
                    with patch.object(adapter, "_render_template", return_value="prompt text"):
                        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=proc):
                            return await adapter.execute()

        started = time.monotonic()
        result = asyncio.run(_run())
        elapsed = time.monotonic() - started

        assert not result.success
        assert result.error == "Timeout after 0.05s"
        assert result.exit_code == -1
        assert communicate_started == [True], "communicate() was never awaited: the timeout path was not really exercised"
        proc.kill.assert_called_once_with()
        assert elapsed < 5, f"took {elapsed:.1f}s: timeout_seconds did not reach asyncio.wait_for"


class TestRunClaudeCodeAdapterDispatch(unittest.TestCase):
    """Test the bridge dispatch function _run_claude_code_adapter."""

    def test_missing_repo_returns_failed(self) -> None:
        from bridge.bridge_server import _run_claude_code_adapter
        result = _run_claude_code_adapter({"adapter": "claude-code", "config": {"template": "t.md"}})
        assert result["status"] == "failed"
        assert "repo" in result["error"]

    def test_missing_template_returns_failed(self) -> None:
        from bridge.bridge_server import _run_claude_code_adapter
        result = _run_claude_code_adapter({"adapter": "claude-code", "config": {"repo": "ATP"}})
        assert result["status"] == "failed"

    def test_successful_dispatch(self) -> None:
        import asyncio
        from bridge.bridge_server import _run_claude_code_adapter
        from adapters.claude_code import AdapterResult

        with patch("adapters.claude_code.ClaudeCodeAdapter.execute", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = AdapterResult(success=True, stdout="done", exit_code=0)
            result = _run_claude_code_adapter({
                "adapter": "claude-code",
                "config": {"repo": "ATP", "template": "prompts/01.md", "model": "sonnet"},
                "context": {},
            })
        assert result["status"] == "ok"
        assert result["adapter"] == "claude-code"
        assert result["stdout"] == "done"


if __name__ == "__main__":
    unittest.main()
