"""Execution output normalizer skeleton for ATP v0."""


def normalize_output(result: dict) -> dict:
    """Return a normalized execution output."""
    # TODO: normalize shell and adapter outputs into ATP artifacts.
    normalized = dict(result)
    normalized["normalized"] = True
    return normalized
