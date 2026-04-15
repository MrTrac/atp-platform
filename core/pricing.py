"""Per-model cost calculation for ATP adapter manifests.

Reads ``registry/pricing/model_prices.json`` and provides a lookup
function for input/output token costs. Falls back to provider defaults
when model is not in the table. JSON used (not YAML) because ATP's
simple YAML loader does not support list-of-dicts nor dict-of-dicts.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple


PRICING_FILE = Path(__file__).resolve().parents[1] / "registry" / "pricing" / "model_prices.json"


class ModelPrice(NamedTuple):
    model: str
    provider: str
    input_per_mtok: float
    output_per_mtok: float


@lru_cache(maxsize=1)
def _load_pricing() -> tuple[dict[str, ModelPrice], dict[str, dict[str, float]]]:
    """Load and cache pricing table. Returns (model_lookup, provider_defaults)."""
    if not PRICING_FILE.is_file():
        return {}, {}

    try:
        data = json.loads(PRICING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, {}

    model_lookup: dict[str, ModelPrice] = {}
    for model_name, entry in (data.get("models") or {}).items():
        if isinstance(entry, dict):
            model_lookup[model_name] = ModelPrice(
                model=model_name,
                provider=entry.get("provider", "unknown"),
                input_per_mtok=float(entry.get("input_per_mtok", 0.0)),
                output_per_mtok=float(entry.get("output_per_mtok", 0.0)),
            )

    defaults: dict[str, dict[str, float]] = {}
    for provider, prices in (data.get("defaults") or {}).items():
        if isinstance(prices, dict):
            defaults[provider] = {
                "input_per_mtok": float(prices.get("input_per_mtok", 0.0)),
                "output_per_mtok": float(prices.get("output_per_mtok", 0.0)),
            }

    return model_lookup, defaults


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    provider: str | None = None,
) -> float:
    """Calculate total cost in USD for a request.

    Parameters
    ----------
    model : str
        Model name (e.g., "claude-sonnet-4-20250514").
    input_tokens : int
        Input token count.
    output_tokens : int
        Output token count.
    provider : str | None
        Provider name for fallback lookup if model not in table.

    Returns
    -------
    float
        Estimated cost in USD, rounded to 6 decimals. Returns 0.0 if
        no pricing available.
    """
    model_lookup, defaults = _load_pricing()

    price = model_lookup.get(model)
    if price is not None:
        cost = (input_tokens * price.input_per_mtok + output_tokens * price.output_per_mtok) / 1_000_000
        return round(cost, 6)

    # Fallback to provider defaults
    if provider and provider in defaults:
        d = defaults[provider]
        cost = (input_tokens * d["input_per_mtok"] + output_tokens * d["output_per_mtok"]) / 1_000_000
        return round(cost, 6)

    return 0.0


def get_model_price(model: str) -> ModelPrice | None:
    """Look up a model's pricing entry."""
    model_lookup, _ = _load_pricing()
    return model_lookup.get(model)


def list_priced_models() -> list[str]:
    """List all models with pricing entries."""
    model_lookup, _ = _load_pricing()
    return sorted(model_lookup.keys())
