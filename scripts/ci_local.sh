#!/usr/bin/env bash
# Name: ci_local.sh
# Purpose: Run the test suite the way .github/workflows/ci.yml does (a clean clone of one commit, in a scrubbed environment, once per
#          Python version of the CI matrix) so that "green here, red on CI" shows up before the push.
# Author: Nguyen Thanh Thu / ATM ManagAIR Technical Team
# Version: 1.0.0
# Updated: 2026-10-14
# Changelog:
# - 1.0.0: Initial version.
#
# Why: `make test` in a working copy sees things CI never has: the AI_OS install under $HOME, API keys and AIOS_* variables in the
# environment, whatever `python3` happens to be, and files that are untracked or git-ignored. CI went red twice that way while `make test`
# was green here (2.6.2: CI had no pytest and nothing declared jinja2, both present on the dev machine; c501335: a test that needed
# ~/AI_OS/30_RUNTIME/bin/aios-gate).
#
# What it controls:
#   code under test  a fresh `git clone` of --ref (default HEAD): untracked, ignored and uncommitted files are not there.
#   environment      `env -i` with an empty HOME, a PATH of system directories plus the venv, CI=true. Nothing from the caller's
#                    environment passes through, and HOME is not the real home, so Path.home() cannot reach ~/AI_OS.
#   interpreter      every version of the matrix in the ref's ci.yml, each in a fresh venv installed the way CI does (`pip install -e ".[dev]"`).
# What it cannot control: the OS (this may be macOS, CI is Ubuntu), absolute paths hardcoded to this machine, and network access.
#
# The file can be sourced (the tests do) without running anything.

set -euo pipefail

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CI_FILE=".github/workflows/ci.yml"

# What a test could pick up from the developer's machine by accident. The isolation probe fails when any of it is visible in the sandbox.
LEAK_VAR_RE='^(ATP_|AIOS|ANTHROPIC|OPENAI|CLAUDE|AWS_|GITHUB_TOKEN|SSH_AUTH_SOCK|VIRTUAL_ENV|PYTHON)'
LEAK_TOOLS=(aios aios-gate gsgr aios-deploy aios-publish)

SANDBOX=()   # the `env -i ...` prefix every sandboxed command runs under; filled by build_sandbox

usage() {
  cat <<'EOF'
Usage: scripts/ci_local.sh [options]        (or: make ci-local CI_LOCAL_ARGS="...")

Run the tests like CI does: clean clone of one commit, scrubbed environment, one venv per Python version of the CI matrix.

Options:
  --ref <ref>        commit to test (default: HEAD). Uncommitted and untracked files are never part of it.
  --python <list>    Python versions instead of the CI matrix, e.g. 3.12 or 3.11,3.12
  --strict           exit 3 when a matrix version is not installed, instead of testing only the ones that are
  --keep             keep the temp directory even when everything passes
  --print-matrix     print the Python versions of the CI matrix of --ref, one per line, and exit
  --self-check       only prove that the sandbox is isolated (no clone, no venv, no install), and exit
  -h, --help         this help

Exit codes: 0 all green | 1 a test run failed | 2 could not run (no interpreter, bad ref, install failed, sandbox leaks) | 3 --strict and a version is missing
EOF
}

die() {
  printf 'ci-local: %s\n' "$*" >&2
  exit 2
}

# Versions of strategy.matrix.python-version of $1's ci.yml, one per line. Only the inline form `python-version: ["3.11", "3.12"]` is read;
# any other layout yields nothing and the caller stops instead of guessing.
matrix_of() {
  git -C "$ROOT_DIR" show "$1:$CI_FILE" 2>/dev/null \
    | sed -n 's/.*python-version: *\[\(.*\)\].*/\1/p' | head -n 1 | tr -d '" ' | tr ',' '\n'
}

# Absolute path of a `python<version>`: on PATH first, then one that uv already manages (never downloads one).
find_python() {
  local v="$1" p=""
  p="$(command -v "python$v" 2>/dev/null || true)"
  if [[ -z "$p" ]] && command -v uv >/dev/null 2>&1; then
    p="$(uv python find --no-python-downloads "$v" 2>/dev/null || true)"
  fi
  if [[ -n "$p" && -x "$p" ]] && "$p" -c "import sys; sys.exit(0 if '%d.%d' % sys.version_info[:2] == '$v' else 1)" 2>/dev/null; then
    printf '%s\n' "$p"
  fi
}

# $1 = root of this run's sandbox, $2 = the venv it will use.
build_sandbox() {
  local root="$1" venv="$2"
  SANDBOX=(env -i
    "HOME=$root/home"
    "TMPDIR=$root/tmp"
    "PATH=$venv/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    "LANG=C.UTF-8"
    "CI=true"
    "GITHUB_ACTIONS=true"
    "PIP_DISABLE_PIP_VERSION_CHECK=1")
}

# Runs inside the sandbox and prints one line per check; non-zero when the sandbox is not isolated.
#   $1 = the caller's real HOME   $2 = sandbox parent directory   $3 = (optional) bin dir that must come first for python3
sandbox_probe() {
  local real_home="$1" parent="$2" want_bin="${3:-}"
  # The probe body is single-quoted on purpose: it must expand inside the sandbox shell, not here.
  # shellcheck disable=SC2016
  "${SANDBOX[@]}" /bin/bash -c '
    real_home=$1; parent=$2; want_bin=$3; leak_re=$4; shift 4
    status=0
    ok()  { printf "    ok    %s\n" "$1"; }
    bad() { printf "    LEAK  %s\n" "$1"; status=1; }

    vars="$(env | sed -n "s/=.*//p" | grep -E "$leak_re" | tr "\n" " " || true)"
    if [ -z "$vars" ]; then ok "no ATP_/AIOS*/API-key/ssh-agent/python variables in the environment"; else bad "variables visible: $vars"; fi

    case "$HOME" in
      "$real_home" | "$real_home"/*) bad "HOME is the real home or inside it ($HOME)" ;;
      *) ok "HOME is not the real home" ;;
    esac
    if [ -z "$(ls -A "$HOME" 2>/dev/null)" ]; then ok "HOME starts empty"; else bad "HOME is not empty: $(ls -A "$HOME" | tr "\n" " ")"; fi
    if [ ! -e "$HOME/AI_OS" ]; then ok "no ~/AI_OS"; else bad "~/AI_OS exists under the sandbox HOME"; fi

    leaked=""; old_ifs=$IFS; IFS=:
    for d in $PATH; do
      case "$d" in "$parent"/*) continue ;; esac
      case "$d" in "$real_home"/*) leaked="$leaked $d" ;; esac
    done
    IFS=$old_ifs
    if [ -z "$leaked" ]; then ok "no PATH entry under the real home"; else bad "PATH entries under the real home:$leaked"; fi

    found=""
    for t in "$@"; do
      if command -v "$t" >/dev/null 2>&1; then found="$found $t=$(command -v "$t")"; fi
    done
    if [ -z "$found" ]; then ok "no AI_OS tool on PATH"; else bad "tools visible:$found"; fi

    if [ -n "$want_bin" ]; then
      if [ "$(command -v python3 2>/dev/null)" = "$want_bin/python3" ]; then ok "python3 is the venv one"; else bad "python3 is $(command -v python3 2>/dev/null || echo missing), not $want_bin/python3"; fi
    fi
    exit $status
  ' _ "$real_home" "$parent" "$want_bin" "$LEAK_VAR_RE" "${LEAK_TOOLS[@]}"
}

# What a clean clone will NOT contain. A new file shown as `??` that a test needs must be committed, or CI will not have it either.
report_uncommitted() {
  local dirty n
  dirty="$(git -C "$1" status --porcelain 2>/dev/null || true)"
  if [[ -z "$dirty" ]]; then
    return 0
  fi
  n="$(printf '%s\n' "$dirty" | wc -l | tr -d ' ')"
  printf 'ci-local: %s change(s) in the working tree are NOT in the commit under test (CI will not see them either):\n' "$n" >&2
  printf '%s\n' "$dirty" | head -n 15 | sed 's/^/    /' >&2
  if (( n > 15 )); then
    printf '    ... and %d more\n' $(( n - 15 )) >&2
  fi
  printf '  A test that needs a new file shown with ?? passes here only if it is committed.\n' >&2
}

# Fresh clone of $2 into $1, without running any hook (a global core.hooksPath would otherwise fire on the clone).
clone_at() {
  git -c core.hooksPath=/dev/null clone --quiet --no-hardlinks "$ROOT_DIR" "$1" \
    && git -C "$1" -c core.hooksPath=/dev/null -c advice.detachedHead=false checkout --quiet --detach "$2"
}

# One matrix version. Sets VERSION_STATUS (PASS|FAIL|ERROR), VERSION_DETAIL and VERSION_SECS.
run_version() {
  local v="$1" py="$2" sha="$3" make_bin="$4" parent="$5" real_home="$6"
  local root="$parent/py$v" clone venv log rc started
  clone="$root/atp-platform"; venv="$root/venv"; log="$root/make-test.log"
  started=$SECONDS; VERSION_STATUS="ERROR"; VERSION_DETAIL=""; VERSION_SECS=0
  mkdir -p "$root/home" "$root/tmp"

  printf '\n== Python %s (%s, %s) ==\n' "$v" "$py" "$("$py" -c 'import platform; print(platform.python_version())')"
  if ! clone_at "$clone" "$sha" >"$root/clone.log" 2>&1; then
    VERSION_DETAIL="clone failed"; tail -n 5 "$root/clone.log" | sed 's/^/    /'; VERSION_SECS=$(( SECONDS - started )); return 0
  fi
  printf '  clone    %s -> %s\n' "${sha:0:8}" "$clone"

  build_sandbox "$root" "$venv"
  if ! "${SANDBOX[@]}" "$py" -m venv "$venv" >"$root/venv.log" 2>&1; then
    VERSION_DETAIL="venv creation failed"; tail -n 5 "$root/venv.log" | sed 's/^/    /'; VERSION_SECS=$(( SECONDS - started )); return 0
  fi
  printf '  isolation probe\n'
  if ! sandbox_probe "$real_home" "$parent" "$venv/bin"; then
    VERSION_DETAIL="the sandbox is not isolated (LEAK lines above); the result would not mean anything"; VERSION_SECS=$(( SECONDS - started )); return 0
  fi

  printf '  pip install -e ".[dev]" ... '
  if ! ( cd "$clone" && "${SANDBOX[@]}" "$venv/bin/python" -m pip install --quiet -e ".[dev]" ) >"$root/pip.log" 2>&1; then
    printf 'FAILED\n'; tail -n 15 "$root/pip.log" | sed 's/^/    /'
    VERSION_DETAIL="pip install failed (is PyPI reachable? the sandbox passes no proxy variables)"; VERSION_SECS=$(( SECONDS - started )); return 0
  fi
  printf 'ok\n'

  printf '  make test\n'
  set +e
  ( cd "$clone" && "${SANDBOX[@]}" "$make_bin" test ) 2>&1 | tee "$log" | sed 's/^/    /'
  rc=${PIPESTATUS[0]}
  set -e
  VERSION_SECS=$(( SECONDS - started ))
  VERSION_DETAIL="$(grep -E '[0-9]+ (passed|failed|error)' "$log" | sed -E 's/^[= ]+//; s/[= ]+$//' | awk 'NR>1{printf "; "} {printf "%s", $0} END{print ""}')"
  if (( rc != 0 )); then
    VERSION_STATUS="FAIL"; [[ -n "$VERSION_DETAIL" ]] || VERSION_DETAIL="make test exited $rc"
  elif [[ -z "$VERSION_DETAIL" ]]; then
    VERSION_DETAIL="make test exited 0 but printed no pytest summary, so nothing is known to have run"
  else
    VERSION_STATUS="PASS"
  fi
  return 0
}

main() {
  local ref="HEAD" pythons="" strict=0 keep=0 mode="run"
  while (( $# )); do
    case "$1" in
      --ref)          ref="${2:?--ref needs a value}"; shift 2 ;;
      --python)       pythons="${2:?--python needs a value}"; shift 2 ;;
      --strict)       strict=1; shift ;;
      --keep)         keep=1; shift ;;
      --print-matrix) mode="matrix"; shift ;;
      --self-check)   mode="selfcheck"; shift ;;
      -h|--help)      usage; return 0 ;;
      *)              usage >&2; die "unknown option: $1" ;;
    esac
  done

  local real_home="$HOME" sha versions v py
  if [[ "$mode" != "selfcheck" ]]; then
    sha="$(git -C "$ROOT_DIR" rev-parse --verify --quiet "$ref^{commit}")" || die "unknown ref: $ref"
    if [[ -n "$pythons" ]]; then
      # comma and space both separate; the second set repeats \n so tr behaves the same on BSD and GNU
      # shellcheck disable=SC2020
      versions="$(printf '%s\n' "$pythons" | tr ', ' '\n\n' | sed '/^$/d')"
    else
      versions="$(matrix_of "$sha" || true)"
      [[ -n "$versions" ]] || die "cannot read the Python matrix from $CI_FILE at $ref (inline form python-version: [\"3.11\", \"3.12\"] expected); pass --python"
    fi
    if [[ "$mode" == "matrix" ]]; then
      printf '%s\n' "$versions"; return 0
    fi
  fi

  local base="${TMPDIR:-/tmp}"; base="${base%/}"
  T="$(mktemp -d "$base/atp-ci-local.XXXXXX")"
  trap 'ci_local_cleanup $?' EXIT
  KEEP_TMP=$keep

  if [[ "$mode" == "selfcheck" ]]; then
    local probe_rc=0
    build_sandbox "$T" "$T/venv"
    printf 'ci-local self-check (sandbox under %s):\n' "$T"
    sandbox_probe "$real_home" "$T" "" || probe_rc=$?
    command rm -rf "$T"; T=""
    return $probe_rc
  fi

  local make_bin; make_bin="$(command -v make)" || die "make is not installed"
  printf 'ci-local: testing %s (%s) | clean clone, scrubbed environment\n' "${sha:0:8}" "$(git -C "$ROOT_DIR" log -1 --format=%s "$sha" | cut -c1-70)"
  # The working-tree warning only means something when the commit under test is the one this tree is built on.
  if [[ "$sha" == "$(git -C "$ROOT_DIR" rev-parse HEAD)" ]]; then
    report_uncommitted "$ROOT_DIR"
  fi

  local res_v=() res_status=() res_detail=() res_secs=() missing=()
  for v in $versions; do
    py="$(find_python "$v")"
    if [[ -z "$py" ]]; then
      missing+=("$v"); printf '\n== Python %s: not installed, skipped (try: uv python install %s)\n' "$v" "$v"; continue
    fi
    run_version "$v" "$py" "$sha" "$make_bin" "$T" "$real_home"
    res_v+=("$v"); res_status+=("$VERSION_STATUS"); res_detail+=("$VERSION_DETAIL"); res_secs+=("$VERSION_SECS")
  done

  if (( ${#res_v[@]} == 0 )); then
    die "none of the CI matrix versions (${versions//$'\n'/ }) is installed; nothing was tested"
  fi

  local i failed=0 errored=0
  printf '\n== Result for %s ==\n' "${sha:0:8}"
  for (( i = 0; i < ${#res_v[@]}; i++ )); do
    printf '  Python %-5s %-5s %s (%ds)\n' "${res_v[$i]}" "${res_status[$i]}" "${res_detail[$i]}" "${res_secs[$i]}"
    [[ "${res_status[$i]}" == "FAIL" ]] && failed=1
    [[ "${res_status[$i]}" == "ERROR" ]] && errored=1
  done
  if (( ${#missing[@]} )); then
    printf '  NOT TESTED: Python %s (not installed)\n' "${missing[*]}"
  fi
  if (( failed )); then
    printf 'ci-local: FAIL, CI would be red. The temp directory is kept for inspection.\n'; return 1
  elif (( errored )); then
    printf 'ci-local: could not run to the end (see ERROR above); nothing is proven.\n'; return 2
  elif (( ${#missing[@]} )); then
    printf 'ci-local: PASS on %s, but INCOMPLETE: not tested on %s.\n' "${res_v[*]}" "${missing[*]}"
    if (( strict )); then return 3; fi
    return 0
  fi
  printf 'ci-local: PASS on the whole CI matrix (Python %s).\n' "${res_v[*]}"
}

# Removes the temp directory unless the run failed or --keep was given.
ci_local_cleanup() {
  local rc="$1"
  if [[ -n "${T:-}" && -d "$T" && "$T" == */atp-ci-local.* ]]; then
    if (( rc != 0 )) || (( ${KEEP_TMP:-0} )); then
      printf 'ci-local: kept %s\n' "$T" >&2
    else
      command rm -rf "$T"
    fi
  fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
