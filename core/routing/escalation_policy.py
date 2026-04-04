"""ATP escalation policy — decide when to route from local to cloud inference.

Policy: local-first, cloud only when there is an explicit escalation trigger.
"""

from __future__ import annotations

from typing import Any


ESCALATION_TRIGGERS = frozenset({
    "hard_reasoning",
    "final_artifact",
    "current_facts",
    "low_confidence",
})


def should_escalate(
    request: dict[str, Any],
    local_result: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    """Decide whether a request should escalate from local to cloud.

    Parameters
    ----------
    request : dict
        The incoming request (may contain ``force_cloud`` or ``escalation_trigger``).
    local_result : dict or None
        The result from the local adapter, if available.

    Returns
    -------
    tuple[bool, str]
        ``(should_escalate, reason)`` — reason is empty string when no escalation.
    """
    # Explicit force
    if request.get("force_cloud") is True:
        return True, "force_cloud requested"

    # Named escalation trigger
    trigger = request.get("escalation_trigger", "")
    if trigger and trigger in ESCALATION_TRIGGERS:
        return True, f"escalation_trigger={trigger}"

    # Local result failures — but not contract violations (would fail on cloud too)
    if local_result is not None:
        error_msg = local_result.get("error") or ""
        is_contract_violation = "contract violated" in error_msg.lower()

        if local_result.get("status") == "failed" and not is_contract_violation:
            return True, "local execution failed"

        manifest = local_result.get("manifest", {})
        if manifest.get("completion_validated") is False and not is_contract_violation:
            return True, "local completion validation failed"

    return False, ""
