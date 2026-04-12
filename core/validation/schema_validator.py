"""Lightweight JSON Schema validation for ATP — no external dependencies.

Validates data dicts against ATP schema YAML files using basic Draft-07
checks: required fields, type matching, and additionalProperties.
Validation is advisory — returns a report, never raises.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

from core.intake.loader import RequestLoadError, load_request


SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"

JSON_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


class ValidationReport(NamedTuple):
    """Result of schema validation."""
    valid: bool
    errors: list[str]
    schema_name: str


def _check_type(value: Any, expected_type: str) -> bool:
    """Check if value matches a JSON Schema type string."""
    python_types = JSON_TYPE_MAP.get(expected_type)
    if python_types is None:
        return True
    return isinstance(value, python_types)


def validate_against_schema(
    data: dict[str, Any],
    schema_path: str,
) -> ValidationReport:
    """Validate a data dict against an ATP schema YAML file.

    Parameters
    ----------
    data : dict
        The data to validate.
    schema_path : str
        Relative path from schemas/ root, e.g. ``"request/request.schema.yaml"``.

    Returns
    -------
    ValidationReport
        ``valid=True`` if no errors, otherwise ``valid=False`` with error list.
    """
    full_path = SCHEMA_ROOT / schema_path
    errors: list[str] = []

    try:
        schema = load_request(full_path)
    except RequestLoadError as exc:
        return ValidationReport(valid=False, errors=[f"Schema load failed: {exc}"], schema_name=schema_path)

    required_fields = schema.get("required", [])
    if isinstance(required_fields, list):
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for field_name, field_schema in properties.items():
            if field_name not in data:
                continue
            expected_type = field_schema.get("type") if isinstance(field_schema, dict) else None
            if expected_type and not _check_type(data[field_name], expected_type):
                actual = type(data[field_name]).__name__
                errors.append(
                    f"Type mismatch for '{field_name}': expected {expected_type}, got {actual}"
                )

    return ValidationReport(
        valid=len(errors) == 0,
        errors=errors,
        schema_name=schema_path,
    )
