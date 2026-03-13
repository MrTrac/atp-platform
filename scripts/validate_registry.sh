#!/usr/bin/env bash
# Name: validate_registry.sh
# Purpose: Safe seed registry validation for ATP v0.
# Author: Nguyen Thanh Thu / ATM ManagAIR Technical Team
# Version: 0.1.0
# Updated: YYYY-MM-DDTHH:MM:SSZ
# Changelog:
# - 0.1.0: Initial skeleton.

set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

test -f "$ROOT_DIR/registry/products/ATP.yaml"
test -f "$ROOT_DIR/registry/products/TDF.yaml"
test -f "$ROOT_DIR/registry/providers/non_llm_execution.yaml"
test -f "$ROOT_DIR/registry/nodes/local_mac.yaml"

printf 'ATP registry seed validation: OK\n'
