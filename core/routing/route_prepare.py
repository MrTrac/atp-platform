"""Route preparation skeleton for ATP v0."""


def prepare_route(request_context: dict) -> dict:
    """Return a minimal routing preparation artifact."""
    # TODO: combine capability, provider, node, and policy context.
    return {"prepared": True, "request_context": request_context}
