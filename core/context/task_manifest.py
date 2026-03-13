"""Task manifest skeleton for ATP v0."""


def build_task_manifest(run_id: str) -> dict:
    """Return a minimal task manifest."""
    # TODO: materialize task manifest template.
    return {"run_id": run_id, "manifest_type": "task_manifest"}
