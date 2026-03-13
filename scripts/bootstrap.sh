#!/usr/bin/env bash
# Name: bootstrap.sh
# Purpose: Safe local bootstrap helper for ATP M1-M2.

set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

printf 'ATP bootstrap root: %s\n' "$ROOT_DIR"
printf 'Recommended next steps:\n'
printf '  1. make help\n'
printf '  2. make smoke\n'
printf '  3. make test\n'
