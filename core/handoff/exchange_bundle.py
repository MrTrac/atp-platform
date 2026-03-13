"""Exchange bundle seed model for ATP M1-M2."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class ExchangeBundle:
    """Shallow exchange bundle for provider-agnostic handoff contracts."""

    artifacts: list[str] = field(default_factory=list)
    provider: str = "unspecified"
    adapter: str = "unspecified"

    def to_dict(self) -> dict[str, object]:
        """Return a serializable handoff payload."""

        payload = asdict(self)
        payload["handoff_type"] = "exchange_bundle"
        return payload


def build_exchange_bundle(
    artifacts: list[str],
    provider: str = "unspecified",
    adapter: str = "unspecified",
) -> dict[str, object]:
    """Build a minimal exchange_bundle payload."""

    return ExchangeBundle(
        artifacts=list(artifacts),
        provider=provider,
        adapter=adapter,
    ).to_dict()
