#!/usr/bin/env bash
# Name: smoke_run.sh
# Purpose: Safe ATP M1-M8 smoke flow.

set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REQUEST_FILE="$ROOT_DIR/tests/fixtures/requests/sample_request_exec_echo.yaml"

test -f "$ROOT_DIR/cli/run.py"
test -f "$ROOT_DIR/cli/validate.py"
test -f "$ROOT_DIR/cli/inspect.py"
test -f "$REQUEST_FILE"

python3 "$ROOT_DIR/cli/validate.py" "$REQUEST_FILE" >/dev/null
python3 "$ROOT_DIR/cli/run.py" "$REQUEST_FILE" >/dev/null
python3 "$ROOT_DIR/cli/inspect.py" >/dev/null

printf 'ATP M1-M8 smoke: OK\n'
