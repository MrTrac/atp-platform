"""Workspace writer skeleton for ATP v0."""


def workspace_path(run_id: str, area: str) -> str:
    """Return a relative workspace path hint."""
    # TODO: resolve runtime workspace path outside the repo.
    return f"workspace/{area}/{run_id}"
