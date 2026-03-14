# ATP v0 Runbook

## Status

ATP MVP v0 is currently in implemented baseline state.

## Repository boundary

Operate ATP only from:

```text
SOURCE_DEV/platforms/ATP
```

Do not treat these locations as the ATP repo:

- `SOURCE_DEV/`
- `SOURCE_DEV/products/TDF`
- `SOURCE_DEV/workspace`

## Standard verification sequence

```bash
cd /Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
python3 -m compileall cli core tests
make test
```

## Standard request flow

### Validate a request

```bash
./cli/atp validate tests/fixtures/requests/sample_request_atp.yaml
```

### Run a safe local execution flow

```bash
./cli/atp run tests/fixtures/requests/sample_request_exec_echo.yaml
```

## Current MVP operating rule

ATP v0 should be operated as an architecture-locked baseline.
