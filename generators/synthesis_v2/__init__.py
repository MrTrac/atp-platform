"""Port of AOKP `src/runtime/synthesis/*` (structured, grounded, quality-checked answers) — KD-ATP-006 Phase 2a/2b.

Pure Python, standard library only, no network: the model is injected as a `chat(messages) -> str` function. Behaviour is pinned to AOKP by golden vectors produced from the real
TypeScript (`tests/fixtures/synthesis_v2/`), see `tests/unit/test_synthesis_v2_golden.py`.
"""

from .synthesizer import DEFAULT_SYNTHESIS_CONFIG, synthesize_answer

__all__ = ["DEFAULT_SYNTHESIS_CONFIG", "synthesize_answer"]
