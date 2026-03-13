"""Validation skeleton for ATP v0."""


def validate_artifacts(artifacts: list) -> dict:
    """Return a minimal validation summary."""
    # TODO: validate selected and authoritative artifacts.
    return {"valid": True, "artifact_count": len(artifacts)}
