# ATP Cloud Adapters

Cloud LLM inference adapters for ATP escalation from local to cloud providers.

## Anthropic Adapter

### Setup

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Input Contract

Same shape as the Ollama adapter (provider-agnostic interface):

```python
execute_anthropic({
    "model": "claude-sonnet-4-20250514",   # required
    "prompt": "Your question here",         # required (or "messages")
    "context": "System prompt",             # optional — becomes "system" field
    "options": {"temperature": 0.7, "max_tokens": 4096},  # optional
})
```

### Output Contract

```json
{
  "status": "success | failed",
  "route_type": "cloud",
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "output": "<response_text>",
  "manifest": {
    "timestamp": "<ISO8601>",
    "response_time_ms": 1234,
    "token_count": 42,
    "completion_validated": true
  },
  "escalation_triggered": true,
  "error": null
}
```

### Escalation Policy

ATP routes local-first. Cloud escalation triggers when:

| Trigger | Condition |
|---------|-----------|
| Local failure | `local_result["status"] == "failed"` |
| Validation failure | `manifest["completion_validated"] == False` |
| Force cloud | `request["force_cloud"] == True` |
| Named triggers | `request["escalation_trigger"]` in: `hard_reasoning`, `final_artifact`, `current_facts`, `low_confidence` |

### Testing

```bash
cd ~/SOURCE_DEV/platforms/ATP

# Adapter unit tests (mocked, no API key needed)
python3 -m pytest adapters/cloud/test_anthropic_adapter.py -v

# Escalation policy tests
python3 -m pytest tests/integration/test_escalation_policy.py -v
```

### Known Limitations

- No streaming support
- No retry logic — single attempt per request
- No OpenAI adapter yet (Anthropic only)
- Token count from Anthropic usage field (input + output)
- Timeout default: 120s (configurable via `timeout` parameter)
- API key must be set as environment variable (no config file support)
