"""Validation result skeleton for ATP v0."""


def build_validation_result(summary: dict) -> dict:
    """Return a minimal validation result artifact."""
    # TODO: persist validation state and evidence.
    return {"validation": summary}
