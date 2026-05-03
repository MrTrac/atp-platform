"""ATP generator stub: tot (Step 2 W9-10 staging).

Migration source (AOKP, TypeScript): src/runtime/reasoning/tot/ — Tree-of-Thought thought generator + evaluator

Status: STUB — actual port scheduled per tasks.json D5.x (Step 4 W17-W20).
"""

from __future__ import annotations

from generators.types import GeneratorRequest, GeneratorResult


GENERATOR_NAME = "tot"


def run(req: GeneratorRequest) -> GeneratorResult:
    raise NotImplementedError(
        f"ATP generator '{GENERATOR_NAME}' is a Step 2 W9-10 staging stub. "
        f"Port from AOKP scheduled for D5.x (Doctrine v6.0 Step 4 W17-W20)."
    )
