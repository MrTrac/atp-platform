#!/usr/bin/env bash
# Regenerate golden.json.gz from the REAL AOKP TypeScript. NOT part of the test suite (CI has no AOKP checkout): run it by hand when the port or AOKP's synthesis code changes.
#   AOKP_DIR=~/SOURCE_DEV/platforms/AOKP ./run_golden.sh
# Needs: node >= 20, AOKP's node_modules (tsx), python3. Writes golden.json.gz next to this file and prints AOKP's commit so the fixture says what it came from.
set -euo pipefail
HERE="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
AOKP_DIR="${AOKP_DIR:-$HOME/SOURCE_DEV/platforms/AOKP}"
[ -x "$AOKP_DIR/node_modules/.bin/tsx" ] || { echo "no tsx under $AOKP_DIR/node_modules" >&2; exit 2; }
TMP="$(mktemp -d "${TMPDIR:-/tmp}/synth-golden.XXXXXX")"; trap 'command rm -rf "$TMP"' EXIT
python3 "$HERE/make_inputs.py"
# tsconfig: AOKP's own, with ONE extra mapping so the LLM import resolves to the scripted stub (the specific pattern wins over "@/*").
cat > "$TMP/tsconfig.json" <<EOF
{ "extends": "$AOKP_DIR/tsconfig.json",
  "compilerOptions": { "baseUrl": "$AOKP_DIR", "paths": { "@/src/runtime/platform/llm-chat": ["$HERE/llm_chat_stub.ts"], "@/*": ["./*"] } },
  "include": [] }
EOF
AOKP_COMMIT="$(git -C "$AOKP_DIR" rev-parse HEAD)" AOKP_DIR="$AOKP_DIR" HERE="$HERE" OUT="$TMP/golden.json" \
  "$AOKP_DIR/node_modules/.bin/tsx" --tsconfig "$TMP/tsconfig.json" "$HERE/make_golden.ts"
gzip -9 -n -c "$TMP/golden.json" > "$HERE/golden.json.gz"
command rm -f "$HERE/inputs.json"   # generated, 800 KB; make_inputs.py recreates it (seeded) when needed
ls -l "$HERE/golden.json.gz" | awk '{print "golden.json.gz:", $5, "byte"}'
