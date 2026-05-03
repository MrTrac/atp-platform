"""ATP generator stub: federation (D1.9 staging + D4.3 registry wired).

Migration source (AOKP, TypeScript): src/runtime/federation/

Status: STUB — actual port scheduled per tasks.json D5.x (Step 4 W17-W20).
The registry decorator is live so /api/synthesis/generators can advertise
the descriptor immediately; /api/synthesis/generate dispatch raises
NotImplementedError until the body is filled in.
"""

from __future__ import annotations

from generators.registry import (
    GeneratorRequest,
    GeneratorResult,
    SynthesisResult,
    register_generator,
)


@register_generator(
    name="federation",
    version="0.1.0",
    lifecycle="draft",
    description="Cross-facility federation rank fusion",
    source_aokp_module="src/runtime/federation/",
    params_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "context": {"type": "object", "additionalProperties": True},
        },
        "required": ["query"],
    },
)
def run(req: GeneratorRequest) -> SynthesisResult:
    raise NotImplementedError(
        f"ATP generator 'federation' is a Step 2 W9-10 staging stub. "
        f"Port from AOKP scheduled for D5.x (Doctrine v6.0 Step 4 W17-W20)."
    )
