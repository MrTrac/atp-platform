"""Knowledge adapter contract for ATP.

Defines the Protocol and typed shapes for knowledge retrieval
adapters (e.g., AOKP). Knowledge adapters are context sources,
not executors — they enrich requests before execution.
"""

from __future__ import annotations

from typing import Any, Protocol, TypedDict


class KnowledgeQuery(TypedDict, total=False):
    """Input shape for knowledge retrieval queries."""
    query: str
    filters: dict[str, Any]
    top_k: int


class KnowledgeResult(TypedDict, total=False):
    """Output shape from knowledge retrieval queries."""
    status: str
    provider: str
    hits: list[dict[str, Any]]
    total: int
    context_text: str
    manifest: dict[str, Any]
    error: str


class GraphQuery(TypedDict, total=False):
    """Input shape for knowledge graph queries."""
    term: str
    entity_id: str


class GraphResult(TypedDict, total=False):
    """Output shape from knowledge graph queries."""
    status: str
    provider: str
    entities: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    manifest: dict[str, Any]
    error: str


class KnowledgeAdapter(Protocol):
    """Knowledge adapters retrieve context from knowledge platforms."""

    def query(self, knowledge_query: dict[str, Any]) -> dict[str, Any]:
        """Query the knowledge base for relevant context."""

    def check_health(self) -> dict[str, Any]:
        """Check if the knowledge source is available."""
