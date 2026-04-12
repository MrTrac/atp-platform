"""Filesystem exchange helpers for ATP.

When ``ATP_PERSIST_ARTIFACTS`` is enabled, ``write_exchange_bundle()``
writes the bundle JSON to the workspace exchange zone.
"""

from __future__ import annotations

import os
from typing import Any


PERSIST_ARTIFACTS = os.environ.get("ATP_PERSIST_ARTIFACTS", "").lower() in ("1", "true", "yes")


def write_exchange_bundle(
    bundle: dict[str, Any],
    *,
    workspace_root: Any | None = None,
) -> dict[str, Any]:
    """Write an exchange bundle to workspace when enabled, or return metadata only."""

    bundle_id = bundle.get("bundle_id", "bundle-unknown")
    run_id = bundle.get("request_id", "run-unknown")

    if not PERSIST_ARTIFACTS and workspace_root is None:
        return {
            "bundle_id": bundle_id,
            "status": "in_memory_only",
            "notes": ["Exchange persistence disabled (set ATP_PERSIST_ARTIFACTS=true to enable)."],
        }

    from adapters.filesystem.workspace_writer import (
        _write_json,
        resolve_workspace_root,
    )
    from pathlib import Path

    ws = Path(workspace_root) if workspace_root else resolve_workspace_root()
    exchange_dir = ws / "exchange" / "current-task" / run_id
    exchange_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = _write_json(exchange_dir / "exchange-bundle.json", bundle)

    return {
        "bundle_id": bundle_id,
        "status": "persisted",
        "path": str(bundle_path),
        "notes": ["Exchange bundle persisted to workspace."],
    }
