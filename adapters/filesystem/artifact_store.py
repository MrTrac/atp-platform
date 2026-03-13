"""Filesystem artifact store skeleton for ATP v0."""


def store_artifact(artifact: dict) -> dict:
    """Return a minimal artifact store result."""
    # TODO: persist artifact metadata in runtime zone.
    return {"artifact": artifact, "stored": False}
