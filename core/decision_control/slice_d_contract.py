"""Compatibility shim for older Slice D imports.

Authority runtime implementation now lives in `core.decision_control.contract`.
Do not add authority logic here.
"""

from core.decision_control.contract import (
    DECISION_CLASSES,
    DECISION_RESULTS,
    TRANSITION_CLASSES,
    DecisionContractError,
    build_decision_record,
    build_transition_record,
    validate_decision_record,
    validate_transition_record,
)

__all__ = [
    "DecisionContractError",
    "DECISION_CLASSES",
    "DECISION_RESULTS",
    "TRANSITION_CLASSES",
    "build_decision_record",
    "build_transition_record",
    "validate_decision_record",
    "validate_transition_record",
]
