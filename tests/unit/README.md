# Unit Tests

ATP unit tests covering core modules, adapters, CLI, and contracts.

## Naming conventions

Tests use two naming schemes:
- `test_slice<NN>_*.py` — Tests aligned with development slices (02–10)
- `test_feature<NNN>_*.py` — Tests aligned with feature programs (F-001 to F-303)
- `test_<domain>.py` — Domain-focused tests (execution_flow, route_selection, etc.)

## Running

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/unit -p 'test_*.py'
```

Or via Makefile: `make test` (runs both unit and integration).

## Adding tests

- Place new tests in this directory as `test_<name>.py`
- Use `unittest.TestCase` as base class
- Fixtures are in `tests/fixtures/`
- For mocked HTTP adapters, use `unittest.mock.patch("...urlopen")`
