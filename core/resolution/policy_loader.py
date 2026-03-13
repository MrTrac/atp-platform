"""Policy loader skeleton for ATP v0."""


def load_policy(policy_name: str) -> dict:
    """Return a minimal policy reference."""
    # TODO: load policy documents from registry.
    return {"policy": policy_name, "status": "loaded_seed"}
