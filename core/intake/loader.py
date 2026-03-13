"""Load ATP request files for the M1-M2 intake flow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RequestLoadError(ValueError):
    """Raised when a request file cannot be loaded."""


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None

    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)

    try:
        return float(value)
    except ValueError:
        pass

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {'"', "'"}
    ):
        return value[1:-1]

    return value


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a small YAML subset used by ATP seed fixtures."""

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        container = stack[-1][1]

        if stripped.startswith("- "):
            if not isinstance(container, list):
                raise RequestLoadError(
                    f"Unsupported YAML structure near line {line_number}: list item without list parent."
                )
            container.append(_parse_scalar(stripped[2:].strip()))
            continue

        if ":" not in stripped:
            raise RequestLoadError(
                f"Unsupported YAML structure near line {line_number}: expected key/value pair."
            )

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value:
            parsed_value = _parse_scalar(value)
            if isinstance(container, dict):
                container[key] = parsed_value
            else:
                raise RequestLoadError(
                    f"Unsupported YAML structure near line {line_number}: cannot assign key inside list."
                )
            continue

        next_container: Any = {}
        if isinstance(container, dict):
            container[key] = next_container
        else:
            raise RequestLoadError(
                f"Unsupported YAML structure near line {line_number}: cannot nest key inside list."
            )
        stack.append((indent, next_container))

    return root


def load_request(source: str | Path) -> dict[str, Any]:
    """Load a request file from JSON or a small YAML subset."""

    path = Path(source)
    if not path.is_file():
        raise RequestLoadError(f"Request file not found: {path}")

    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    try:
        if suffix == ".json":
            payload = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            payload = _parse_simple_yaml(text)
        else:
            raise RequestLoadError(
                f"Unsupported request file format: {path.suffix or '<no suffix>'}"
            )
    except json.JSONDecodeError as exc:
        raise RequestLoadError(f"Invalid JSON request: {exc}") from exc

    if not isinstance(payload, dict):
        raise RequestLoadError("Request payload must be an object at the top level.")

    return payload
