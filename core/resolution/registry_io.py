"""Small file-loading helpers for ATP M3 resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.intake.loader import RequestLoadError, load_request

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml_mapping(relative_path: str) -> dict[str, Any]:
    """Load a YAML mapping from a repo-relative path."""

    path = REPO_ROOT / relative_path
    if not path.is_file():
        raise RequestLoadError(f"Missing file: {relative_path}")
    return load_request(path)
