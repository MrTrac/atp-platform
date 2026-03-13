"""Routing result skeleton for ATP v0."""


def build_routing_result(decision: dict) -> dict:
    """Wrap a minimal routing result."""
    # TODO: persist routing result artifact.
    return {"routing_result": decision}
