"""Workspace writer placeholder for ATP M7."""

from __future__ import annotations

from pathlib import Path


def workspace_path(run_id: str, area: str) -> str:
    """Return the deferred runtime workspace path hint for ATP v0."""

    return f"SOURCE_DEV/workspace/{area}/{run_id}"


def repo_local_serialization_path(run_id: str, area: str) -> Path:
    """Return a repo-local test-safe serialization path hint."""

    return Path("tests") / "fixtures" / "outputs" / area / run_id
