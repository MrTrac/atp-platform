"""AI_OS governance hook for ATP execution artifacts.

Thin wrapper that invokes aios-gate after each ATP execution to classify,
review, and gate artifacts based on AI_OS change control tiers.

Usage:
    from bridge.governance_hook import run_governance_review
    result = run_governance_review(artifact_dict)
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from typing import Any

AIOS_GATE = os.path.expanduser("~/AI_OS/30_RUNTIME/bin/aios-gate")


def run_governance_review(artifact: dict[str, Any]) -> dict[str, Any]:
    """Run aios-gate review on an ATP execution artifact.

    Saves the artifact to a temp file, invokes aios-gate review, and parses
    the JSON output into a governance result dict.

    Returns
    -------
    dict with keys:
        governance_class    : str   — "A"|"B"|"C"|"D"|"E"
        governance_status   : str   — "approved"|"rejected"|"pending_human"
        governance_reason   : str   — human-readable reason
        requires_human      : bool  — True if human gate needed
    """
    request_id = artifact.get("request_id", "unknown")

    # Write artifact to temp file for aios-gate
    fd, artifact_path = tempfile.mkstemp(
        prefix=f"aios_artifact_{request_id}_",
        suffix=".json",
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(artifact, f, indent=2)

        # Invoke aios-gate review
        proc = subprocess.run(
            [AIOS_GATE, "review", artifact_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if proc.returncode != 0:
            return {
                "governance_class": "E",
                "governance_status": "error",
                "governance_reason": f"aios-gate failed: {proc.stderr.strip()}",
                "requires_human": False,
            }

        # Parse the JSON output from aios-gate
        gate_result = json.loads(proc.stdout)

        return {
            "governance_class": gate_result.get("governance_class", "E"),
            "governance_status": gate_result.get("governance_status", "error"),
            "governance_reason": gate_result.get("governance_reason", ""),
            "requires_human": gate_result.get("requires_human", False),
        }

    except subprocess.TimeoutExpired:
        return {
            "governance_class": "E",
            "governance_status": "error",
            "governance_reason": "aios-gate timed out",
            "requires_human": False,
        }
    except (json.JSONDecodeError, KeyError) as exc:
        return {
            "governance_class": "E",
            "governance_status": "error",
            "governance_reason": f"Failed to parse aios-gate output: {exc}",
            "requires_human": False,
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(artifact_path)
        except OSError:
            pass
