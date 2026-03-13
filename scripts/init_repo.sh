#!/usr/bin/env bash
# Name: init_repo.sh
# Purpose: Safe ATP repo initialization helper.
# Author: Nguyen Thanh Thu / ATM ManagAIR Technical Team
# Version: 0.1.0
# Updated: YYYY-MM-DDTHH:MM:SSZ
# Changelog:
# - 0.1.0: Initial skeleton.

set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$ROOT_DIR/.git" ]; then
  git init "$ROOT_DIR"
fi

printf 'ATP repo init check complete\n'
