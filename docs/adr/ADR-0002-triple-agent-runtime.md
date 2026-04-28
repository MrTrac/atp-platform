# ADR-0002: triple-agent-runtime

- **Status:** Accepted
- **Date:** 2026-04-19 (v2.0.3+ ATP adapter parity; backfilled 2026-04-28)
- **Author(s):** anh Thu + Claude Code
- **Module(s):** ATP (Transformation Plane)
- **Governance:** AI_OS Doctrine §3.9.1 + DP#78
- **Decision tier:** Tier 3 (new entity — 3 sister adapters + isolation contract)

---

## 1. Context

aios-flow runners support `claude-code-agent` node (Anthropic Claude Code CLI). Anh's vision: parallel exploration with 3 different code agent vendors → pick winner. Required ATP adapter parity for OpenAI Codex CLI + Cursor agent CLI.

---

## 2. Decision

3 sister CLI agent adapters in ATP:

| Adapter | CLI tool | Default model | Auth |
|---|---|---|---|
| `claude_code.py` | `claude` (Anthropic CLI) | claude-sonnet-4-6 | ANTHROPIC_API_KEY (Keychain inject) |
| `codex.py` | `codex exec` (OpenAI CLI) | gpt-5-pro | OPENAI_API_KEY (Keychain inject) |
| `cursor.py` | `cursor-agent -p` | auto | CURSOR_API_KEY (Keychain inject) |

Workspace isolation contract (3 modes):
- `direct` (default Phase 1) — agent writes to repo directly
- `read-only` — symlink mount of repo, agent reads only
- `worktree` — git worktree under per-run workspace, edits diff-able + cherry-pick-able before merge

Single dispatcher `_run_cli_agent_adapter(adapter_kind)` in `bridge_server.py` to avoid code duplication.

---

## 3. Alternatives considered

| # | Alternative | Pros | Cons | Rejected |
|---|---|---|---|---|
| A | Claude-only (existing) | Simplest | Anh wants vendor diversity (vendor risk hedging) |
| B | Build Codex + Cursor adapters but skip isolation | Quick to ship | Direct write = race conditions across parallel agents |
| C (chosen) | 3 adapters + 3 isolation modes | Full vendor parity + safe parallel | Complex test matrix |
| D | Generic "shell-agent" adapter parameterized by CLI command | DRY | CLI-specific quirks (output parsing, env injection) leak through |

---

## 4. Consequences

### 4.1 Positive
- aios-flow can run 3 agents in parallel (Fork pattern §7.5)
- Workspace isolation prevents race conditions
- Keychain injection eliminates env var leak in launchd plists

### 4.2 Negative / trade-offs
- 3 CLI tools must be installed on dev machine (Brew formulas)
- API keys × 3 — each vendor has separate billing (Phase 2+ cost tracking via DP#97 G10)
- CLI output parsing fragile (vendors change output format between versions)

### 4.3 Risks accepted
- Cursor `cursor-agent` is newest (~2026-Q1) — adapter may need updates as CLI matures

---

## 5. Implementation
- `adapters/claude_code.py` (existing, refactored shared code)
- `adapters/codex.py` (new 2026-04-19 v2.0.3)
- `adapters/cursor.py` (new 2026-04-19 v2.0.3)
- `bridge/bridge_server.py` `_run_cli_agent_adapter(adapter_kind)` dispatcher
- `atp-bridge-start.sh` — Keychain → env injection wrapper for launchd

## 6. References
- AIOS-OC ADR-0003 sister decision (Flow Canvas exposes 3 agent types in palette)
- AI_OS Doctrine §7.5 sub-agent patterns (Fork future implementation)
- aios-flow `runners/{claude_code,codex,cursor}.py` consumer
