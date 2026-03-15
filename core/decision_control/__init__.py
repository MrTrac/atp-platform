"""ATP v1.0 Slice D — Operational Decision / State Transition Control Contract.

Bounded runtime model for decision record and transition record shape.
Source-of-truth: docs/archive/reports/ATP_v1_0_Slice_D_*.md
"""

from core.decision_control.slice_d_contract import (
    DECISION_CLASSES,
    DECISION_RESULTS,
    TRANSITION_CLASSES,
    SliceDContractError,
    build_decision_record,
    build_transition_record,
    validate_decision_record,
    validate_transition_record,
)

__all__ = [
    "SliceDContractError",
    "DECISION_CLASSES",
    "DECISION_RESULTS",
    "TRANSITION_CLASSES",
    "build_decision_record",
    "build_transition_record",
    "validate_decision_record",
    "validate_transition_record",
]
