"""Bundle materializer skeleton for ATP v0."""


def materialize_bundle(bundle_type: str, items: list) -> dict:
    """Return a minimal bundle description."""
    # TODO: create EvidenceBundle and ExchangeBundle payloads.
    return {"bundle_type": bundle_type, "items": list(items)}
