"""Workspace writer placeholder for ATP M7."""

from __future__ import annotations

from pathlib import Path


def workspace_path(run_id: str, area: str) -> str:
    """Return a repo-local placeholder path hint only."""

    return f"deferred-workspace/{area}/{run_id}"


def repo_local_serialization_path(run_id: str, area: str) -> Path:
    """Return a repo-local test-safe serialization path hint."""

    return Path("tests") / "fixtures" / "outputs" / area / run_id
