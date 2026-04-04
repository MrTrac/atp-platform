# ATP Ollama Adapter

Local LLM inference adapter connecting ATP to Ollama.

## Input Contract

```python
execute_ollama({
    "model": "qwen3:14b",           # required — Ollama model name
    "prompt": "Your question here",  # required (or "messages")
    "context": "System prompt",      # optional — injected as system message
    "options": {"temperature": 0.7}, # optional — Ollama model params
})
```

Alternatively pass `messages` (list of `{"role", "content"}` dicts) instead of `prompt`.

## Output Contract

```json
{
  "status": "success | failed",
  "route_type": "local",
  "provider": "ollama",
  "model": "<model_name>",
  "output": "<response_text>",
  "manifest": {
    "timestamp": "<ISO8601>",
    "response_time_ms": 1234,
    "token_count": 42,
    "completion_validated": true
  },
  "escalation_triggered": false,
  "error": null
}
```

## Pilot v1 Gaps Addressed

| # | Gap | How |
|---|-----|-----|
| 1 | Execution contract | Validates model + prompt/messages before calling Ollama |
| 2 | Artifact manifest | Returns timestamp, response_time_ms, token_count, status |
| 3 | Completion validation | Checks response is non-empty with real content |
| 4 | Routing metadata | Includes route_type, provider, escalation_triggered |
| 5 | Freeze/handoff protocol | Structured JSON-serializable result |

## Testing

```bash
cd ~/SOURCE_DEV/platforms/ATP
python -m pytest adapters/ollama/test_ollama_adapter.py -v
```

Unit tests mock the Ollama API. No running Ollama instance required.

## Known Limitations

- Streaming responses not supported (stream=False)
- No automatic model fallback / escalation (escalation_triggered always False)
- Token count depends on Ollama reporting eval_count (may be null for some models)
- No retry logic — single attempt per request
- Timeout default: 120s (configurable via `timeout` parameter)
