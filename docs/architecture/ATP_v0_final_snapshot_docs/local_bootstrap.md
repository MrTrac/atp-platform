# ATP Local Bootstrap

## Purpose

This document describes the local bootstrap and verification path for ATP MVP v0 in its implemented baseline state.

## Working directory

Always operate ATP from:

```text
/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
```

## Recommended bootstrap steps

```bash
cd /Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
python3 -m compileall cli core tests
make test
```

## Quick functional checks

### Validate example request

```bash
./cli/atp validate tests/fixtures/requests/sample_request_atp.yaml
```

### Run safe local execution example

```bash
./cli/atp run tests/fixtures/requests/sample_request_exec_echo.yaml
```
