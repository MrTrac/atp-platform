# Model Pricing Registry

Per-model USD pricing for cost tracking in adapter manifests.

- **File:** `model_prices.json`
- **Used by:** `core/pricing.py` → adapter manifests
- **Update when:** providers publish new pricing
- **Format:** USD per 1M tokens, split into input vs output
- **Why JSON (not YAML):** ATP's simple YAML loader does not support nested dict-of-dicts or list-of-dicts; JSON is universal.

When a model is not in the table, the provider default (`defaults.<provider>`) is used.

## Adding a new model

Edit `model_prices.json`:
```json
"models": {
  "new-model-name": {"provider": "anthropic", "input_per_mtok": 2.5, "output_per_mtok": 10.0}
}
```

Cache is loaded once at first call (lru_cache); restart bridge to pick up changes.
