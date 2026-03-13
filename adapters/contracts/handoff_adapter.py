"""Handoff adapter contract skeleton for ATP v0."""


class HandoffAdapter:
    """Minimal handoff adapter contract."""

    # TODO: formalize handoff adapter interface.
    def handoff(self, payload: dict) -> dict:
        return {"payload": payload, "status": "not_implemented"}
