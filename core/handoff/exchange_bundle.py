"""Exchange bundle handoff model for ATP M8."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class ExchangeBundle:
    """Basic exchange bundle for ATP-side handoff summary."""

    exchange_id: str
    request_id: str
    artifacts: list[str] = field(default_factory=list)
    provider: str = "unspecified"
    adapter: str = "unspecified"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["handoff_type"] = "exchange_bundle"
        return payload


def build_exchange_bundle(
    artifacts: list[str],
    request_id: str = "request-unknown",
    provider: str = "unspecified",
    adapter: str = "unspecified",
) -> dict[str, object]:
    """Build a basic exchange_bundle payload."""

    return ExchangeBundle(
        exchange_id=f"exchange-{request_id}",
        request_id=request_id,
        artifacts=list(artifacts),
        provider=provider,
        adapter=adapter,
        notes=["ATP v0 exchange bundle summary only. No production materialization."],
    ).to_dict()
