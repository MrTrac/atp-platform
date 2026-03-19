"""Bounded operator review summary helpers for ATP v1.4 — F-301.

This module builds one compact, derived review summary for operators/reviewers.
It does NOT create a dashboard, live status board, registry, or control plane.
"""

from __future__ import annotations

from collections import OrderedDict

from core.artifact_export import EXPORT_MODE, EXPORT_SCOPE, SUPPORTED_ARTIFACT_TYPES

REVIEW_SUMMARY_CONTRACT_VERSION = "1.0"
REVIEW_MODE = "derived_static_review_summary"
REVIEW_SCOPE = "repo_local_human_gated_operator_review"
REVIEW_ENTRYPOINT = "./atp review-summary"
CANONICAL_CLI_ENTRYPOINT = "./atp"
CANONICAL_REQUEST_FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"
BLOCKED_ACTIONS = [
    "activate_background_monitoring",
    "open_network_endpoint",
    "start_scheduler_or_daemon",
    "enable_automated_progression",
    "bypass_human_gate",
    "deploy_to_external_target",
]
UNSUPPORTED_CAPABILITIES = [
    "live_status_board",
    "control_plane_dashboard",
    "provider_abstraction_layer",
    "persistent_registry_or_history",
    "external_integration_runtime",
    "deployment_runtime",
]


def build_operator_review_summary() -> OrderedDict[str, object]:
    """Return one bounded operator-facing review summary for ATP."""

    return OrderedDict(
        [
            ("review_summary_contract_version", REVIEW_SUMMARY_CONTRACT_VERSION),
            ("review_mode", REVIEW_MODE),
            ("review_scope", REVIEW_SCOPE),
            (
                "entrypoint_surface",
                OrderedDict(
                    [
                        ("cli_entrypoint", CANONICAL_CLI_ENTRYPOINT),
                        ("review_command", REVIEW_ENTRYPOINT),
                        ("canonical_request_fixture", CANONICAL_REQUEST_FIXTURE),
                    ]
                ),
            ),
            (
                "bounded_capabilities",
                OrderedDict(
                    [
                        (
                            "can_expose",
                            [
                                "bounded_request_chain_outputs",
                                "execution_session_summary",
                            ],
                        ),
                        (
                            "can_export",
                            list(SUPPORTED_ARTIFACT_TYPES),
                        ),
                        (
                            "can_project",
                            ["integration_contract_projection"],
                        ),
                        (
                            "can_assess",
                            ["deployability_readiness"],
                        ),
                    ]
                ),
            ),
            (
                "operator_review_path",
                OrderedDict(
                    [
                        ("start_with", "./atp review-summary"),
                        (
                            "review_chain",
                            [
                                "./atp smoke-request-chain",
                                "./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml",
                                "./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml",
                            ],
                        ),
                        (
                            "focused_supporting_surfaces",
                            [
                                "./atp execution-session tests/fixtures/requests/sample_request_slice02.yaml",
                                "./atp integration-contract",
                                "./atp deployability-check",
                            ],
                        ),
                    ]
                ),
            ),
            (
                "posture_constraints",
                OrderedDict(
                    [
                        ("repo_local", True),
                        ("human_gated", True),
                        ("json_first", True),
                        ("export_mode", EXPORT_MODE),
                        ("export_scope", EXPORT_SCOPE),
                    ]
                ),
            ),
            ("blocked_actions", list(BLOCKED_ACTIONS)),
            ("unsupported_capabilities", list(UNSUPPORTED_CAPABILITIES)),
            (
                "notes",
                [
                    "This review summary is descriptive only and exists for operator/reviewer interpretation.",
                    "It does not report live state, control ATP behavior, or create a registry/catalog of runtime activity.",
                    "Use it to understand ATP's bounded review, handoff, projection, and assessment surfaces more quickly.",
                ],
            ),
        ]
    )


def build_operator_review_scan_summary(
    review_summary: OrderedDict[str, object],
) -> OrderedDict[str, object]:
    """Return a compact first-scan summary for the operator review surface."""

    capabilities = review_summary["bounded_capabilities"]
    return OrderedDict(
        [
            ("primary_focus", "operator_review_summary"),
            ("review_mode", review_summary.get("review_mode")),
            (
                "capability_view",
                "expose_export_project_assess_with_explicit_non_capabilities",
            ),
            (
                "first_review_target",
                "operator_review_summary.bounded_capabilities",
            ),
            (
                "next_safe_bounded_action",
                "review blocked_actions and operator_review_path before any planning or handoff interpretation",
            ),
            ("export_count", len(capabilities["can_export"])),
        ]
    )
