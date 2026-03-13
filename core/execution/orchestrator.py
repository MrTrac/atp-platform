"""Execution orchestrator skeleton for ATP v0."""


def execute_run(route: dict) -> dict:
    """Return a minimal execution result."""
    # TODO: hand off to the selected execution adapter.
    return {"route": route, "status": "executed_seed"}
