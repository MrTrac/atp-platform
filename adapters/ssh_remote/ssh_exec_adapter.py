"""SSH execution adapter skeleton for ATP v0."""


def execute_remote(command: str, node: str) -> dict:
    """Return a minimal remote execution result."""
    # TODO: implement node-portable remote execution semantics.
    return {"command": command, "node": node, "status": "seed"}
