#!/usr/bin/env bash
# Load cloud-AI API keys from macOS Keychain into the environment, then exec
# the ATP bridge server. Keys already set in the environment are preserved.
#
# Keychain layout (one generic-password item per provider):
#   service = <PROVIDER>_API_KEY   (e.g. ANTHROPIC_API_KEY, OPENAI_API_KEY)
#   account = $USER
#
# Add a key manually (one-time, prompts for allow):
#   security add-generic-password -U -s OPENAI_API_KEY -a "$USER" \
#     -T /usr/bin/security -w "sk-..."
#
# This wrapper is a no-op on non-macOS hosts: it silently skips keychain
# lookup and starts the bridge with whatever env vars are already set.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

KEYCHAIN_SERVICES=(
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  GEMINI_API_KEY
  XAI_API_KEY
  GROQ_API_KEY
  CURSOR_API_KEY
)

loaded=0
kept=0
missing=0

if [[ "$(uname -s)" == "Darwin" ]] && command -v security >/dev/null 2>&1; then
  account="${USER:-$(id -un)}"
  for svc in "${KEYCHAIN_SERVICES[@]}"; do
    if [[ -n "${!svc:-}" ]]; then
      kept=$((kept + 1))
      continue
    fi
    if value=$(security find-generic-password -s "${svc}" -a "${account}" -w 2>/dev/null); then
      export "${svc}=${value}"
      loaded=$((loaded + 1))
    else
      missing=$((missing + 1))
    fi
  done
  printf '[bridge-keychain] loaded=%d kept_from_env=%d not_in_keychain=%d\n' \
    "${loaded}" "${kept}" "${missing}" >&2
else
  printf '[bridge-keychain] non-Darwin host — skipping keychain, using env only\n' >&2
fi

exec python3 "${REPO_ROOT}/bridge/bridge_server.py" "$@"
