"""Minimal artifact adapter contract for ATP M6."""

from __future__ import annotations

from typing import Any, Protocol


class ArtifactAdapter(Protocol):
    """Artifact adapters accept ATP artifact-like dictionaries."""

    def persist(self, artifact: dict[str, Any]) -> dict[str, Any]:
        """Persist or shape an ATP artifact payload."""

