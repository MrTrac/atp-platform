"""Local subprocess adapter skeleton for ATP v0."""


def execute_local(command: str) -> dict:
    """Return a minimal local execution result."""
    # TODO: implement safe local command execution.
    return {"command": command, "mode": "local", "status": "seed"}
