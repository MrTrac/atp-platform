#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

command="${1:-help}"

ensure_git_repo() {
  if ! git -C "${REPO_ROOT}" rev-parse --show-toplevel >/dev/null 2>&1; then
    printf 'ERROR: ATP repo root is not a Git repository: %s\n' "${REPO_ROOT}" >&2
    exit 1
  fi
}

repo_root() {
  printf '%s\n' "${REPO_ROOT}"
}

git_root() {
  git -C "${REPO_ROOT}" rev-parse --show-toplevel
}

current_branch() {
  git -C "${REPO_ROOT}" branch --show-current 2>/dev/null || true
}

current_head() {
  git -C "${REPO_ROOT}" rev-parse --short HEAD
}

latest_tag() {
  git -C "${REPO_ROOT}" describe --tags --abbrev=0 2>/dev/null || printf 'none\n'
}

worktree_state() {
  if [ -n "$(git -C "${REPO_ROOT}" status --short)" ]; then
    printf 'dirty\n'
  else
    printf 'clean\n'
  fi
}

print_context() {
  printf 'repo_root=%s\n' "$(repo_root)"
  printf 'git_root=%s\n' "$(git_root)"
  printf 'branch=%s\n' "$(current_branch)"
  printf 'head=%s\n' "$(current_head)"
  printf 'latest_tag=%s\n' "$(latest_tag)"
  printf 'worktree=%s\n' "$(worktree_state)"
}

print_status() {
  print_context
  printf 'status_short_begin\n'
  git -C "${REPO_ROOT}" status --short
  printf 'status_short_end\n'
}

print_authority() {
  printf 'governance_root=%s\n' "${REPO_ROOT}/docs/governance"
  printf 'operators_root=%s\n' "${REPO_ROOT}/docs/operators"
  printf 'archive_reports_root=%s\n' "${REPO_ROOT}/docs/archive/reports"
  printf 'aios_integration_doc=%s\n' "${REPO_ROOT}/docs/operators/ai_os_thin_integration.md"
  printf 'bridge_file=%s\n' "${REPO_ROOT}/AGENTS.md"
  printf 'bridge_file=%s\n' "${REPO_ROOT}/AI_OS_CONTEXT.md"
  printf 'bridge_file=%s\n' "${REPO_ROOT}/CLAUDE.md"
  printf 'bridge_file=%s\n' "${REPO_ROOT}/.cursorrules"
  printf 'bridge_file=%s\n' "${REPO_ROOT}/.github/copilot-instructions.md"
  printf 'git_safe_rule=%s\n' "${REPO_ROOT}/docs/governance/Global_Safe_Git_Branch_Guard_Rule.md"
  printf 'shorthand_reference=%s\n' "${REPO_ROOT}/docs/governance/reference/ATP_Global_Shorthand_and_Alias_Rules.md"
}

verify_paths() {
  local missing=0
  local path
  for path in \
    "${REPO_ROOT}/docs/governance" \
    "${REPO_ROOT}/docs/archive/reports" \
    "${REPO_ROOT}/docs/operators/ai_os_thin_integration.md" \
    "${REPO_ROOT}/AGENTS.md" \
    "${REPO_ROOT}/AI_OS_CONTEXT.md" \
    "${REPO_ROOT}/CLAUDE.md" \
    "${REPO_ROOT}/.cursorrules" \
    "${REPO_ROOT}/.github/copilot-instructions.md"
  do
    if [ ! -e "${path}" ]; then
      printf 'missing=%s\n' "${path}" >&2
      missing=1
    fi
  done

  if [ "${missing}" -ne 0 ]; then
    exit 1
  fi
}

verify_repo() {
  ensure_git_repo
  verify_paths
  print_context
  print_authority
}

print_help() {
  cat <<'EOF'
Usage: scripts/aios_bridge.sh <command>

Commands:
  help       Show available ATP-side AI_OS bridge commands
  context    Print ATP repo identity and current Git context
  status     Print ATP repo context plus `git status --short`
  authority  Print ATP authority and bridge paths for AI_OS discovery
  verify     Verify required ATP-side bridge paths and print context
EOF
}

ensure_git_repo

case "${command}" in
  help)
    print_help
    ;;
  context)
    print_context
    ;;
  status)
    print_status
    ;;
  authority)
    print_authority
    ;;
  verify)
    verify_repo
    ;;
  *)
    printf 'ERROR: unknown command: %s\n' "${command}" >&2
    print_help >&2
    exit 1
    ;;
esac
