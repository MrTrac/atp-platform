"""Bounded integration-contract projection helpers for ATP v1.3 — F-204.

This module builds a derived/static integration-facing contract projection.
It does NOT create a live API, endpoint, provider runtime, or active integration.
No network calls, persistence, or background behavior are introduced here.
"""

from __future__ import annotations

from collections import OrderedDict

from core.artifact_export import EXPORT_MODE, EXPORT_SCOPE, SUPPORTED_ARTIFACT_TYPES
from core.composition_contract import COMPOSITION_MODE, COMPOSITION_SCOPE, FAIL_STOP_MODEL
from core.integration_readiness import (
    BLOCKED_ACTIONS,
    INTEGRATION_MODE,
    UNSUPPORTED_FEATURES,
)

INTEGRATION_CONTRACT_VERSION = "1.0"
PROJECTION_MODE = "derived_static_projection"
PROJECTION_SCOPE = "repo_local_human_gated_contract_projection"
CONTINUITY_MODE = "derived_session_to_artifact"
CONTINUITY_SCOPE = "bounded_repo_local_within_invocation"
TERMINAL_HANDOFF_ARTIFACT_TYPE = "one_shot_ai_ready_execution_prompt"
TERMINAL_HANDOFF_MODE = "manual_single_ai_handoff"
PROJECTION_ENTRYPOINT = "./atp integration-contract"
REVIEW_ENTRYPOINT = "./atp review-summary"
CANONICAL_CLI_ENTRYPOINT = "./atp"
CANONICAL_SAMPLE_REQUEST = "tests/fixtures/requests/sample_request_slice02.yaml"


def build_integration_contract_projection() -> OrderedDict[str, object]:
    """Return a bounded, machine-readable integration contract projection."""

    return OrderedDict(
        [
            ("projection_contract_version", INTEGRATION_CONTRACT_VERSION),
            ("projection_mode", PROJECTION_MODE),
            ("projection_scope", PROJECTION_SCOPE),
            ("integration_mode", INTEGRATION_MODE),
            (
                "invocation_surface",
                OrderedDict(
                    [
                        ("cli_entrypoint", CANONICAL_CLI_ENTRYPOINT),
                        ("projection_command", PROJECTION_ENTRYPOINT),
                        ("canonical_request_fixture", CANONICAL_SAMPLE_REQUEST),
                    ]
                ),
            ),
            (
                "composition_projection",
                OrderedDict(
                    [
                        ("command", "./atp compose-chain"),
                        ("composition_mode", COMPOSITION_MODE),
                        ("composition_scope", COMPOSITION_SCOPE),
                        ("fail_stop_model", FAIL_STOP_MODEL),
                    ]
                ),
            ),
            (
                "artifact_projection",
                OrderedDict(
                    [
                        ("export_mode", EXPORT_MODE),
                        ("export_scope", EXPORT_SCOPE),
                        ("supported_export_artifact_types", list(SUPPORTED_ARTIFACT_TYPES)),
                        ("terminal_handoff_artifact_type", TERMINAL_HANDOFF_ARTIFACT_TYPE),
                        ("terminal_handoff_mode", TERMINAL_HANDOFF_MODE),
                    ]
                ),
            ),
            (
                "continuity_projection",
                OrderedDict(
                    [
                        ("continuity_mode", CONTINUITY_MODE),
                        ("continuity_scope", CONTINUITY_SCOPE),
                        ("continuity_surfaces", ["execution-session", "export_manifest", "compose-chain"]),
                    ]
                ),
            ),
            (
                "review_handoff_alignment",
                OrderedDict(
                    [
                        ("review_entrypoint", REVIEW_ENTRYPOINT),
                        (
                            "surface_role",
                            "integration_boundary_review_support",
                        ),
                        (
                            "operator_interpretation",
                            "Use after review-summary when checking integration-facing handoff boundaries only. This reference is interpretive only and does not create a planning controller.",
                        ),
                    ]
                ),
            ),
            ("blocked_actions", list(BLOCKED_ACTIONS)),
            ("unsupported_features", list(UNSUPPORTED_FEATURES)),
            (
                "notes",
                [
                    "This document is a derived/static projection of ATP's current integration-facing contract only.",
                    "It does not create a live API, endpoint, provider runtime, or active integration.",
                    "All invocation remains repo-local, human-gated, and bounded at this phase.",
                ],
            ),
        ]
    )


def build_integration_contract_operator_scan_summary(
    projection: OrderedDict[str, object],
) -> OrderedDict[str, object]:
    """Return a compact first-scan summary for the integration contract projection."""

    return OrderedDict(
        [
            ("primary_focus", "integration_contract_projection"),
            ("projection_mode", projection.get("projection_mode")),
            ("integration_mode", projection.get("integration_mode")),
            ("first_review_target", "integration_contract_projection.invocation_surface"),
            (
                "next_safe_bounded_action",
                "start with ./atp review-summary, then review invocation_surface and blocked_actions before any external integration planning",
            ),
        ]
    )
