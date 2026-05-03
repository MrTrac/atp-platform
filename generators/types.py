"""Shared types for ATP generator stubs (Step 2 W9-10 staging).

Locked in here because the Z2 contract draft (D4.3, Step 4 W15-16)
hasn't landed yet and we don't want each stub to re-declare envelope
shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GeneratorRequest:
    request_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    consumer: str = "internal"


@dataclass
class GeneratorResult:
    request_id: str
    status: str  # "ok" | "error" | "partial"
    output: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
