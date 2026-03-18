"""Repo-local execution session tracking helpers for bounded ATP surfaces."""

from __future__ import annotations

import hashlib
from collections import OrderedDict


def build_execution_session_summary(
    *,
    request_files: list[str],
    request_ids: list[str],
) -> OrderedDict[str, object]:
    """Build a deterministic repo-local session summary from explicit request inputs."""

    normalized_request_ids = [str(request_id) for request_id in request_ids]
    session_mode = "single_request" if len(normalized_request_ids) == 1 else "multi_request"
    session_hash = hashlib.sha1("|".join(normalized_request_ids).encode("utf-8")).hexdigest()[:12]
    session_id = (
        f"session-single-{normalized_request_ids[0]}"
        if session_mode == "single_request"
        else f"session-multi-{len(normalized_request_ids)}-{session_hash}"
    )

    return OrderedDict(
        [
            ("session_id", session_id),
            ("session_mode", session_mode),
            ("session_scope", "repo_local_operator_controlled"),
            ("persistence_mode", "derived_in_memory_only"),
            ("request_count", len(normalized_request_ids)),
            ("request_files", [str(request_file) for request_file in request_files]),
            ("request_ids", normalized_request_ids),
            (
                "continuity_anchor",
                OrderedDict(
                    [
                        ("primary_request_id", normalized_request_ids[0]),
                        ("ordered_request_ids_hash", session_hash),
                    ]
                ),
            ),
            (
                "notes",
                [
                    "Session tracking here is derived from explicit request inputs only.",
                    "No background writer, daemon, service, or database is used.",
                ],
            ),
        ]
    )
