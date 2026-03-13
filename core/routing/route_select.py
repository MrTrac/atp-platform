"""Route selection skeleton for ATP v0."""


def select_route(prepared_route: dict) -> dict:
    """Return a minimal routing decision."""
    # TODO: implement capability-based route selection.
    return {
        "decision": "non_llm_execution",
        "reason": "seed",
        "prepared_route": prepared_route,
    }
