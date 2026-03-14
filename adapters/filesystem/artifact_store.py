"""Filesystem artifact shaping helpers for ATP M6."""

from __future__ import annotations

from typing import Any


def store_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Shape an execution result into an ATP artifact-like payload without persistence."""

    return {
        "artifact_id": artifact.get("artifact_id", "artifact-unknown"),
        "artifact_type": artifact.get("artifact_type", "execution_result"),
        "stored": False,
        "notes": ["Artifact persistence is deferred in M6."],
    }
