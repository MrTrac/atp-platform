# Integration Tests

ATP integration tests covering end-to-end flows through the control-plane.

## Test paths

| Test | Flow |
|---|---|
| `test_happy_path.py` | Normal request → execution → validation → approval |
| `test_continue_pending_path.py` | Request → CONTINUE_PENDING state handling |
| `test_reject_path.py` | Request → rejection/escalation |
| `test_escalation_policy.py` | Ollama → escalation check → cloud fallback |
| `test_inspect_current_task.py` | Inspection surface for current task state |
| `test_ollama_integration.py` | Live Ollama adapter (requires Ollama running) |
| `test_openclaw_bridge.py` | OpenClaw → ATP bridge flow |
| `test_aokp_integration.py` | AOKP knowledge adapter (requires AOKP at :3002) |

## Requirements

- Some tests require external services (Ollama, AOKP)
- Gated tests use `@unittest.skipUnless` to skip when services are unavailable
- All tests can be run with: `PYTHONPATH=. python3 -m unittest discover -s tests/integration -p 'test_*.py'`
