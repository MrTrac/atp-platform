"""Bounded composition contract for ATP v1.3 — F-202.

This module defines the compose-chain contract: stage sequencing model,
output envelope schema, and fail-stop semantics. CLI implementation
(cli/compose_chain.py) is added in P2 only.

P1 scope: contract definitions only — no CLI implementation or subprocess calls.
"""

from __future__ import annotations

from collections import OrderedDict

# Composition contract version — bumped when schema changes.
COMPOSITION_CONTRACT_VERSION = "1.0"

# Composition mode — must always remain synchronous and operator-initiated.
COMPOSITION_MODE = "synchronous_sequential_human_initiated"

# Ordered stage sequence — defines the canonical 3-stage pipeline.
COMPOSITION_STAGE_SEQUENCE = [
    "request_flow",
    "request_bundle",
    "request_prompt",
]

# Fail-stop model — composition halts on first stage failure.
FAIL_STOP_MODEL = "halt_on_first_stage_failure"

# Composition scope — bounded to single request file, single invocation.
COMPOSITION_SCOPE = "single_request_bounded_synchronous"

# Composition status values.
COMPOSITION_STATUS_OK = "all_stages_complete"
COMPOSITION_STATUS_FAIL = "halted_at_stage_failure"

# Non-goals explicit in contract — must not be implied by implementation.
COMPOSITION_NON_GOALS = [
    "parallel_stage_execution",
    "retry_on_failure",
    "background_execution",
    "async_mode",
    "dynamic_stage_ordering",
    "multi_request_composition",
]


def build_composition_envelope(
    *,
    request_file: str,
    run_id: str,
    composition_status: str,
    stages: list[dict],
    artifact_continuity_anchors: dict | None = None,
    fail_stage: str | None = None,
    fail_reason: str | None = None,
) -> OrderedDict[str, object]:
    """Build a bounded composition output envelope for one compose-chain run.

    Returns a deterministic envelope. Does not perform any file I/O or subprocess calls.
    Raises ValueError if composition_status is not a recognized value.
    """
    if composition_status not in (COMPOSITION_STATUS_OK, COMPOSITION_STATUS_FAIL):
        raise ValueError(
            f"composition_status must be one of "
            f"{(COMPOSITION_STATUS_OK, COMPOSITION_STATUS_FAIL)!r}, "
            f"got: {composition_status!r}"
        )
    if composition_status == COMPOSITION_STATUS_FAIL and fail_stage is None:
        raise ValueError("fail_stage must be provided when composition_status is failure.")

    payload: list[tuple[str, object]] = [
        ("command", "compose-chain"),
        ("composition_contract_version", COMPOSITION_CONTRACT_VERSION),
        ("composition_mode", COMPOSITION_MODE),
        ("composition_scope", COMPOSITION_SCOPE),
        ("request_file", request_file),
        ("run_id", run_id),
        ("composition_status", composition_status),
        ("stage_sequence", list(COMPOSITION_STAGE_SEQUENCE)),
        ("stages_executed", stages),
    ]
    if artifact_continuity_anchors is not None:
        payload.append(("artifact_continuity_anchors", artifact_continuity_anchors))
    if fail_stage is not None:
        payload.append(("fail_stage", fail_stage))
    if fail_reason is not None:
        payload.append(("fail_reason", fail_reason))

    return OrderedDict(payload)


def build_stage_result(
    *,
    stage: str,
    status: str,
    output: object,
) -> OrderedDict[str, object]:
    """Build a bounded stage result entry for inclusion in composition envelope.

    Does not perform any file I/O.
    """
    if stage not in COMPOSITION_STAGE_SEQUENCE:
        raise ValueError(
            f"stage must be one of {COMPOSITION_STAGE_SEQUENCE!r}, got: {stage!r}"
        )
    return OrderedDict(
        [
            ("stage", stage),
            ("status", status),
            ("output", output),
        ]
    )
