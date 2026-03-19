"""Bounded deployability-readiness assessment helpers for ATP v1.3 — F-205.

This module performs read-only repo-local assessment only. It does NOT deploy,
install, provision, synchronize, or control any external runtime.
"""

from __future__ import annotations

import sys
from collections import OrderedDict
from pathlib import Path

DEPLOYABILITY_CONTRACT_VERSION = "1.0"
ASSESSMENT_MODE = "derived_read_only_assessment"
ASSESSMENT_SCOPE = "repo_local_human_gated_deployability_review"
OVERALL_READINESS_SIGNAL = "assessment_only_not_operationally_deployable"
READINESS_ENTRYPOINT = "./atp deployability-check"
CANONICAL_CLI_ENTRYPOINT = "./atp"
CANONICAL_WORKSPACE_ROOT = "/Users/nguyenthanhthu/SOURCE_DEV/workspace"
CANONICAL_REQUEST_FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"
DEPENDENCY_MANIFEST_CANDIDATES = [
    "requirements.txt",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "Pipfile",
    "poetry.lock",
]
BLOCKED_ACTIONS = [
    "deploy_to_target_environment",
    "install_dependencies_automatically",
    "provision_external_runtime",
    "select_deployment_backend",
    "open_network_endpoint",
    "start_background_daemon",
    "bypass_human_gate",
]
BLOCKERS_BY_DESIGN = [
    "no_real_deployment_execution",
    "no_provider_or_target_abstraction",
    "no_background_worker_or_scheduler",
    "no_external_integration_activation",
]


def _detect_dependency_manifest_state(repo_root: Path) -> OrderedDict[str, object]:
    present_files = [
        name for name in DEPENDENCY_MANIFEST_CANDIDATES if (repo_root / name).exists()
    ]
    declaration_state = (
        "repo_dependency_manifest_present"
        if present_files
        else "no_repo_dependency_manifest_detected"
    )
    return OrderedDict(
        [
            ("declaration_state", declaration_state),
            ("present_files", present_files),
            (
                "operator_interpretation",
                "ATP can only describe dependency declaration state here; it does not install or resolve dependencies.",
            ),
        ]
    )


def build_deployability_readiness(repo_root: Path) -> OrderedDict[str, object]:
    """Return a bounded deployability-readiness assessment for the current repo."""

    launcher_path = repo_root / "atp"
    underlying_cli_path = repo_root / "cli" / "atp"
    return OrderedDict(
        [
            ("deployability_contract_version", DEPLOYABILITY_CONTRACT_VERSION),
            ("assessment_mode", ASSESSMENT_MODE),
            ("assessment_scope", ASSESSMENT_SCOPE),
            ("overall_readiness_signal", OVERALL_READINESS_SIGNAL),
            (
                "python_runtime_check",
                OrderedDict(
                    [
                        ("current_python_version", sys.version.split()[0]),
                        ("repo_declared_requirement", "not_declared_in_repo"),
                        (
                            "assessment",
                            "runtime_detected_but_repo_python_requirement_not_pinned",
                        ),
                    ]
                ),
            ),
            ("dependency_state", _detect_dependency_manifest_state(repo_root)),
            (
                "entry_point_check",
                OrderedDict(
                    [
                        ("cli_entrypoint", CANONICAL_CLI_ENTRYPOINT),
                        ("assessment_command", READINESS_ENTRYPOINT),
                        ("launcher_present", launcher_path.exists()),
                        ("launcher_executable", launcher_path.exists() and launcher_path.stat().st_mode & 0o111 != 0),
                        ("underlying_cli_present", underlying_cli_path.exists()),
                    ]
                ),
            ),
            (
                "workspace_path_requirements",
                OrderedDict(
                    [
                        ("runtime_workspace_root", CANONICAL_WORKSPACE_ROOT),
                        ("workspace_mode", "external_runtime_zone_required"),
                        (
                            "repo_boundary_rule",
                            "runtime_artifacts_must_not_be_written_inside_repo",
                        ),
                    ]
                ),
            ),
            (
                "assessed_artifact_classes",
                [
                    "single_ai_execution_package",
                    "reviewable_single_ai_output_bundle",
                    "one_shot_ai_ready_execution_prompt",
                    "integration_contract_projection",
                ],
            ),
            (
                "configuration_surface_gaps",
                [
                    "no_repo_declared_python_requirement",
                    "no_repo_dependency_manifest_detected",
                    "no_packaged_installer_contract",
                    "no_target_environment_contract",
                ],
            ),
            ("blocked_actions", list(BLOCKED_ACTIONS)),
            ("blockers_by_design", list(BLOCKERS_BY_DESIGN)),
            (
                "notes",
                [
                    "This readiness view is descriptive only. ATP does not deploy, install, provision, or manage external systems here.",
                    "Assessment remains repo-local, human-gated, and read-only except for optional export of this report itself.",
                    "Use this output for downstream review and handoff planning only, not as proof of operational deployment capability.",
                ],
            ),
        ]
    )


def build_deployability_operator_scan_summary(
    readiness: OrderedDict[str, object],
) -> OrderedDict[str, object]:
    """Return a compact first-scan summary for the deployability assessment."""

    return OrderedDict(
        [
            ("primary_focus", "deployability_readiness"),
            ("overall_readiness_signal", readiness.get("overall_readiness_signal")),
            (
                "first_review_target",
                "deployability_readiness.configuration_surface_gaps",
            ),
            (
                "next_safe_bounded_action",
                "review configuration_surface_gaps and blockers_by_design before any downstream deployment planning",
            ),
        ]
    )
