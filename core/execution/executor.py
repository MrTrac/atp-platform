"""Executor skeleton for ATP v0."""


def invoke_executor(command: str) -> dict:
    """Return a minimal executor output."""
    # TODO: invoke subprocess or remote adapter safely.
    return {"command": command, "exit_code": 0, "stdout": "", "stderr": ""}
