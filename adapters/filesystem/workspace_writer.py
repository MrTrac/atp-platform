"""Workspace writer placeholder for ATP M6."""

from __future__ import annotations


def workspace_path(run_id: str, area: str) -> str:
    """Return a repo-local placeholder path hint only."""

    return f"deferred-workspace/{area}/{run_id}"
