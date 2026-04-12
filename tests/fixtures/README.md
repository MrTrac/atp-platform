# Test Fixtures

YAML and JSON fixtures used by ATP unit and integration tests.

## Request fixtures (`requests/`)

| Fixture | Purpose |
|---|---|
| `sample_request_slice02.yaml` | Canonical sample request (default for most tests) |
| `sample_request_slice02_b.yaml` | Secondary request for multi-request tests |
| `sample_request_atp.yaml` | ATP-targeted request |
| `sample_request_tdf.yaml` | TDF-targeted request |
| `sample_request_exec_echo.yaml` | Execution test (echo command) |
| `sample_request_exec_fail.yaml` | Execution test (expected failure) |
| `sample_request.yaml` | Minimal baseline request |

## Adding fixtures

- Use YAML format (ATP's loader supports YAML and JSON)
- Include `request_id`, `request_type`, `execution_intent`, `payload`, `metadata`
- Follow the `sample_request_slice02.yaml` canonical example
