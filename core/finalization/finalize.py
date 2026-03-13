"""Finalization skeleton for ATP v0."""


def finalize_run(run_state: dict) -> dict:
    """Return a minimal finalized run state."""
    # TODO: promote final artifacts and summaries.
    finalized = dict(run_state)
    finalized["status"] = "finalized"
    return finalized
