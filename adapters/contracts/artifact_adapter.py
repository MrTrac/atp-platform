"""Artifact adapter contract skeleton for ATP v0."""


class ArtifactAdapter:
    """Minimal artifact adapter contract."""

    # TODO: formalize artifact store contract.
    def persist(self, artifact: dict) -> dict:
        return {"artifact": artifact, "status": "not_implemented"}
