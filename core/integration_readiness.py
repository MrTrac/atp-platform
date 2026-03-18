"""Bounded integration readiness categories for ATP v1.2.

This module defines signaling-only readiness state for ATP integration preparation.
It does NOT activate integration, open external surfaces, or change runtime behavior.
All values here are static definitions — no network calls, no persistence, no activation.
"""

from __future__ import annotations

from collections import OrderedDict

# Integration readiness scope: what this surface covers.
READINESS_SCOPE = "integration_preparation_signaling_only"

# Integration mode: ATP is NOT in an activated integration mode.
INTEGRATION_MODE = "not_activated"

# Features ATP currently supports for integration preparation.
SUPPORTED_FEATURES = [
    "repo_local_bounded_request_flow",
    "repo_local_execution_session_tracking",
    "operator_readable_outputs",
    "hardened_control_plane_commands",
    "human_gated_single_ai_handoff",
    "json_first_output_contract",
    "smoke_request_chain_verification",
]

# Features ATP does NOT support — explicit blockers by design at this phase.
UNSUPPORTED_FEATURES = [
    "external_api_endpoint",
    "webhook_consumer",
    "event_stream_consumer",
    "provider_abstraction_layer",
    "multi_ai_orchestration",
    "background_execution_engine",
    "scheduler_or_queue",
    "automated_ai_progression",
    "network_accessible_service",
    "persistent_state_store",
]

# Safe integration-prep entrypoints: existing CLI surfaces an integration caller can use.
SAFE_INTEGRATION_ENTRYPOINTS = [
    "request-flow",
    "request-bundle",
    "request-prompt",
    "execution-session",
    "smoke-request-chain",
]

# Actions that are explicitly blocked at this phase.
BLOCKED_ACTIONS = [
    "activate_external_integration",
    "open_network_endpoint",
    "start_background_daemon",
    "enable_automated_ai_progression",
    "bypass_human_gate",
    "merge_main_without_approval",
    "push_main_without_approval",
    "tag_release_without_approval",
]

# Next safe integration-prep action for an operator or reviewer.
NEXT_SAFE_PREP_ACTION = (
    "review bounded request-chain surfaces via ./atp help, "
    "then confirm integration readiness categories before proceeding to any integration-prep work"
)


def build_integration_readiness_summary() -> OrderedDict[str, object]:
    """Return a bounded, signaling-only integration readiness summary.

    This function returns static derived state only. It performs no network calls,
    no file writes, no external lookups, and no integration activation.
    The returned dict is suitable for inclusion in operator-facing output surfaces.
    """
    return OrderedDict(
        [
            ("readiness_scope", READINESS_SCOPE),
            ("integration_mode", INTEGRATION_MODE),
            ("supported_features", list(SUPPORTED_FEATURES)),
            ("unsupported_features", list(UNSUPPORTED_FEATURES)),
            ("safe_integration_entrypoints", list(SAFE_INTEGRATION_ENTRYPOINTS)),
            ("blocked_actions", list(BLOCKED_ACTIONS)),
            ("next_safe_prep_action", NEXT_SAFE_PREP_ACTION),
            (
                "notes",
                [
                    "This surface is signaling only. It does not activate integration.",
                    "ATP remains repo-local, human-gated, and bounded single-AI at this phase.",
                    "No external calls, background processes, or persistent state are introduced here.",
                ],
            ),
        ]
    )
