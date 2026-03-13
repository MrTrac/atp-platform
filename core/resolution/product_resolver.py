"""Product resolver skeleton for ATP v0."""


def resolve_product(product_hint: str) -> dict:
    """Return a minimal product resolution result."""
    # TODO: resolve ATP and TDF profiles from registry.
    return {"product": product_hint or "unknown", "status": "resolved_seed"}
