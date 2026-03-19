"""Bounded artifact export contract for ATP v1.3 — F-201.

This module defines the export contract: path convention, manifest schema,
bounded builder functions, and opt-in file write helpers (P2+).

Stdout remains the canonical primary output. File writes are opt-in secondary
via --export-dir flag only. No background write occurs without the flag.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

# Export contract version — bumped when schema changes.
EXPORT_CONTRACT_VERSION = "1.0"

# Export scope label — must remain honest and bounded.
EXPORT_SCOPE = "bounded_repo_local_artifact"

# Export mode — must never be "automatic" or "background".
EXPORT_MODE = "opt_in_human_initiated"

# Manifest filename — written alongside exported artifacts in each run directory.
MANIFEST_FILENAME = "export_manifest.json"

# Supported artifact types — one per CLI command covered by F-201.
SUPPORTED_ARTIFACT_TYPES = [
    "request_flow",
    "request_bundle",
    "request_prompt",
]

# Notes embedded in every manifest.
EXPORT_NOTES = [
    "Export is opt-in via --export-dir flag. Stdout remains the canonical primary output.",
    "No background write, event publish, or network upload occurs.",
    "ATP remains repo-local, human-gated, and bounded single-AI at this phase.",
]


def build_export_path(export_dir: str, run_id: str, artifact_type: str) -> str:
    """Return the deterministic export path for one artifact.

    Path convention: <export_dir>/<run_id>/<artifact_type>.json

    Does not perform any file I/O. Raises ValueError on invalid inputs.
    """
    if not export_dir:
        raise ValueError("export_dir must be a non-empty string.")
    if not run_id:
        raise ValueError("run_id must be a non-empty string.")
    if artifact_type not in SUPPORTED_ARTIFACT_TYPES:
        raise ValueError(
            f"artifact_type must be one of {SUPPORTED_ARTIFACT_TYPES}, got: {artifact_type!r}"
        )
    return f"{export_dir}/{run_id}/{artifact_type}.json"


def build_manifest_path(export_dir: str, run_id: str) -> str:
    """Return the deterministic manifest path for a run.

    Path convention: <export_dir>/<run_id>/export_manifest.json

    Does not perform any file I/O. Raises ValueError on invalid inputs.
    """
    if not export_dir:
        raise ValueError("export_dir must be a non-empty string.")
    if not run_id:
        raise ValueError("run_id must be a non-empty string.")
    return f"{export_dir}/{run_id}/{MANIFEST_FILENAME}"


def write_artifact(export_dir: str, run_id: str, artifact_type: str, data: object) -> str:
    """Write artifact JSON to the deterministic export path. Returns the path written.

    Creates parent directories as needed. Raises ValueError on invalid inputs.
    """
    path = build_export_path(export_dir, run_id, artifact_type)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))
    return path


def write_manifest(export_dir: str, run_id: str, manifest: object) -> str:
    """Write manifest JSON to the deterministic manifest path. Returns the path written.

    Creates parent directories as needed. Raises ValueError on invalid inputs.
    """
    path = build_manifest_path(export_dir, run_id)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2))
    return path


def build_export_manifest(
    *,
    run_id: str,
    command: str,
    request_file: str,
    artifact_type: str,
    artifact_path: str,
    session_id: str | None = None,
    artifact_continuity_anchors: OrderedDict[str, object] | None = None,
) -> OrderedDict[str, object]:
    """Build a bounded export manifest dict for one artifact export.

    Returns a deterministic manifest. Does not perform any file I/O.
    """
    manifest = OrderedDict(
        [
            ("export_contract_version", EXPORT_CONTRACT_VERSION),
            ("export_scope", EXPORT_SCOPE),
            ("export_mode", EXPORT_MODE),
            ("run_id", run_id),
            ("command", command),
            ("request_file", request_file),
            ("artifact_type", artifact_type),
            ("artifact_path", artifact_path),
        ]
    )
    if session_id is not None:
        manifest["session_id"] = session_id
    if artifact_continuity_anchors is not None:
        manifest["artifact_continuity_anchors"] = artifact_continuity_anchors
    manifest["notes"] = list(EXPORT_NOTES)
    return manifest
