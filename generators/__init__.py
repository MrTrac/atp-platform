"""ATP generators — staging package (Doctrine v6.0 Step 2 W9-10, D1.9).

Hosts 8 generator stubs (in `generators/stubs/`) that will receive
ported logic from AOKP runtime modules during Step 4 W17-W20 (D5.x).
Until then, every stub `run()` raises NotImplementedError so any caller
that lands before D5.x fails loud rather than silently mis-routing.

Located at `generators/` (top level) rather than `atp/generators/`
because the `atp` repo entry is a symlink to `cli/atp` (the launcher
script), not a Python package — so `atp/generators/` is not a
creatable subpath without breaking the launcher tests.

| Stub          | AOKP source module                       | First port (D5.x) |
|---------------|------------------------------------------|-------------------|
| react         | src/runtime/agents/react/                | D5.x stretch      |
| tot           | src/runtime/reasoning/tot/               | D5.x stretch      |
| graphrag_synth| src/runtime/graph/graphrag/              | D5.x stretch      |
| federation    | src/runtime/federation/                  | v6.1 deferred     |
| temporal      | src/runtime/graph/temporal/              | v6.1 deferred     |
| report        | src/runtime/synthesis/                   | D5.2 must-ship    |
| analyze       | src/runtime/eval/ragas/                  | D5.3 must-ship    |
| transform     | src/runtime/retrieval/ (CRAG/Self-RAG)   | D5.4 must-ship    |

AOKP unaffected — sources stay in `~/SOURCE_DEV/platforms/AOKP/src/runtime/*`
per the per-module migration spec ("AOKP keeps generators in Step 2").
"""

from .registry import (
    Citation,
    GeneratorDescriptor,
    SynthesisResult,
    get_generator,
    iter_entries,
    list_generators,
    register_generator,
    registry_version,
    reset_registry,
)
from .types import GeneratorRequest, GeneratorResult

# Eagerly import stubs so their @register_generator decorators populate
# the registry. When real ports land in W17-W20 (D5.x), this import list
# stays the same — bodies get replaced, descriptors stay stable.
from .stubs import (  # noqa: F401  (import-side-effect for registration)
    analyze,
    federation,
    graphrag_synth,
    react,
    report,
    temporal,
    tot,
    transform,
)

__all__ = [
    "Citation",
    "GeneratorDescriptor",
    "GeneratorRequest",
    "GeneratorResult",
    "SynthesisResult",
    "get_generator",
    "iter_entries",
    "list_generators",
    "register_generator",
    "registry_version",
    "reset_registry",
]
