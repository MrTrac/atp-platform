"""ATP synthesis-generator registry — Doctrine v6.0 Step 4 W15-16 (D4.3).

Pattern: each generator module imports `register_generator` and decorates
its `run()` function with metadata. Loading the package (`generators/__init__.py`)
imports every stub, which triggers the decorators, which populate the
module-level registry. /api/synthesis/generators reads from this registry
to advertise what's available; /api/synthesis/generate looks up the
named generator and dispatches.

Registry contract surface = `ATP_AIOS-OC_v3` (Z2 yaml in
~/AI_OS/40_INTEGRATIONS/contracts/ATP_AIOS-OC_v3.yaml).

Self-test:
    python3 -c "import generators; print(generators.list_generators())"
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from .types import GeneratorRequest, GeneratorResult

Lifecycle = str  # "draft" | "incubating" | "stable" | "deprecated"


@dataclass(frozen=True)
class Citation:
    artifact_id: str
    source_id: str
    snippet: str
    classification_path: tuple[str, ...] = ()
    relevance_score: float = 0.0
    rank: int = 0


@dataclass(frozen=True)
class GeneratorDescriptor:
    """Stable, contract-shaped metadata for one registered generator.

    Mirrors `GeneratorDescriptor` schema in ATP_AIOS-OC_v3.yaml so
    /api/synthesis/generators can serialize this dataclass directly.
    """

    name: str
    version: str
    lifecycle: Lifecycle
    description: str
    source_aokp_module: str | None = None
    params_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesisResult:
    """Companion to ATP_AIOS-OC_v3.SynthesisResult schema.

    Generators should return one of these from their `run()` body. The
    pre-existing `GeneratorResult` (in types.py) is kept as a thin
    fallback for legacy stubs that don't yet emit citations.
    """

    run_id: str
    generator: str
    status: str  # "success" | "partial" | "failed"
    answer: str = ""
    citations: list[Citation] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class _RegistryEntry:
    descriptor: GeneratorDescriptor
    handler: Callable[[GeneratorRequest], GeneratorResult | SynthesisResult]


_REGISTRY: dict[str, _RegistryEntry] = {}


def register_generator(
    *,
    name: str,
    version: str,
    lifecycle: Lifecycle,
    description: str,
    source_aokp_module: str | None = None,
    params_schema: dict[str, Any] | None = None,
) -> Callable[
    [Callable[[GeneratorRequest], GeneratorResult | SynthesisResult]],
    Callable[[GeneratorRequest], GeneratorResult | SynthesisResult],
]:
    """Decorator — registers a generator's run() handler under `name`.

    Re-registering an existing name overwrites silently (intentional —
    test fixtures + hot-reload-style replacement work without explicit
    unregister calls). The reset_registry() seam exists for unit tests
    that need a clean slate.
    """

    def decorator(
        fn: Callable[[GeneratorRequest], GeneratorResult | SynthesisResult],
    ) -> Callable[[GeneratorRequest], GeneratorResult | SynthesisResult]:
        descriptor = GeneratorDescriptor(
            name=name,
            version=version,
            lifecycle=lifecycle,
            description=description,
            source_aokp_module=source_aokp_module,
            params_schema=params_schema or {},
        )
        _REGISTRY[name] = _RegistryEntry(descriptor=descriptor, handler=fn)
        return fn

    return decorator


def get_generator(name: str) -> _RegistryEntry | None:
    return _REGISTRY.get(name)


def list_generators() -> list[GeneratorDescriptor]:
    return sorted(
        (entry.descriptor for entry in _REGISTRY.values()),
        key=lambda d: d.name,
    )


def iter_entries() -> Iterator[_RegistryEntry]:
    yield from _REGISTRY.values()


def registry_version() -> str:
    """SHA256 of the registry's serialised descriptor list — UI cache key."""
    payload = json.dumps(
        [
            {
                "name": d.name,
                "version": d.version,
                "lifecycle": d.lifecycle,
                "description": d.description,
                "source_aokp_module": d.source_aokp_module,
                "params_schema": d.params_schema,
            }
            for d in list_generators()
        ],
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def reset_registry() -> None:
    """Test-only: drop every registered generator. NOT for production use."""
    _REGISTRY.clear()
