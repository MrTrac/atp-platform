#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CANONICAL_FIXTURE="tests/fixtures/requests/sample_request_slice02.yaml"
REQUEST_FILE="${1:-$CANONICAL_FIXTURE}"
CLI_PATH="./atp"

if [[ ! -f "$ROOT_DIR/$REQUEST_FILE" ]]; then
  printf 'ATP smoke-request-chain error: request file not found from repo root: %s\n' "$REQUEST_FILE" >&2
  printf 'Next step: rerun with the canonical fixture `%s`, or provide a valid repo-root request path.\n' "$CANONICAL_FIXTURE" >&2
  exit 2
fi

printf 'ATP v1.1 canonical smoke verification\n'
printf 'Repo root: %s\n' "$ROOT_DIR"
printf 'Request fixture: %s\n' "$REQUEST_FILE"
printf 'Canonical fixture policy: %s is the bounded help/example/smoke fixture for the current execution chain.\n' "$CANONICAL_FIXTURE"
printf '\n'

printf '[1/3] request-flow\n'
"$ROOT_DIR/atp" request-flow "$REQUEST_FILE"
printf '\n'

printf '[2/3] request-bundle\n'
"$ROOT_DIR/atp" request-bundle "$REQUEST_FILE"
printf '\n'

printf '[3/3] request-prompt\n'
"$ROOT_DIR/atp" request-prompt "$REQUEST_FILE"
