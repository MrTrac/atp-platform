"""Approval gate skeleton for ATP v0."""


def require_approval(context: dict) -> dict:
    """Return a minimal approval decision."""
    # TODO: apply approval policy and human gate semantics.
    return {"approved": False, "mode": "human_gated", "context": context}
