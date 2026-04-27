<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=CLAUDE -->
AIOS7L CONTEXT
Project: ATP
GeneratedAtUTC: 20260427T054736Z

## Project Context (excerpt)
File: 20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md
SHA256: fdf8af54828e954987d4425eb6716ac5c100a011f9fd39c28b474c8a268d1f7e
----
# AI Project Context — ATP
## Autonomous Task Platform

- **Project:** ATP (Autonomous Task Platform)
- **Repo path:** ~/SOURCE_DEV/platforms/ATP
- **Stable baseline on `main`:** **v2.0.0** (tag) — HEAD `7100f0b`
- **Last updated:** 2026-04-15

---

## 1. ATP là gì

ATP là một platform repository có governance-first discipline, phục vụ bounded execution, review, handoff, và planning support theo repo-local model. ATP phục vụ trục:

```
requested user ⇄ ATP ⇄ products
```

ATP là **Transformation Plane** trong 6-plane multi-AI ecosystem. Current execution reality trên `main` (v2.0.0):

- repo-local, JSON-first, human-gated, bounded
- **provider-abstracted** — 4 execution providers:
  - Ollama local LLM (qwen3:14b/8b, deepseek-r1:8b)
  - Anthropic cloud (chat + tool_use + json_mode + vision + streaming)
  - OpenAI cloud (gpt-4o/5, o1, o3 + tool_use + json_mode + vision + streaming)
  - Subprocess (local shell/git/build)
- **bridge-enabled** — HTTP bridge server tại localhost:8765, 12 endpoints
  - POST /run (blocking) + POST /run/stream (SSE)
  - DELETE /runs/<id> (cancellation)
  - GET /status, /providers, /capabilities, /runs, /runs/active, /runs/<id>
- **knowledge-integrated** — AOKP adapter (opt-in, v2.3.x, 6 endpoints)
- **governance-gated** — aios-gate phân loại artifacts tier A–E
- **production-resilient** — retry/backoff for 429/5xx/network, per-model timeout, per-model pricing
- **agentic-ready** — tool use, JSON mode, vision (cloud providers)
- **streaming-capable** — SSE streaming + request cancellation via threading.Event
- **observable** — central config, structured JSON logging, 7 typed error codes
- non-persistent runtime by default (artifacts optional via ATP_PERSIST_RUNS)
- non-orchestrating (không có scheduler hay graph execution)
- non-daemonized (bridge server là opt-in, không auto-start)

Current accepted line status (v2.0.0):
- v1.6.0 observability baseline frozen
- v1.7.0 cloud API key passthrough + AOKP v2.3.x frozen
- **v1.8.0 Cloud Foundations released** (OpenAI adapter, retry, pricing, timeout)
- **v1.9.0 Agentic Capabilities released** (tool use, JSON mode, vision, capabilities matrix)
- **v2.0.0 Streaming & Cancellation released** (SSE streaming, DELETE /runs/<id>, in-flight tracker)
- PRs #19, #20, #21 merged 2026-04-15; tagged v1.8.0 / v1.9.0 / v2.0.0

---

## 2. Authority order
**Cross-project governance pointers:**
Để tra cứu auto-integration và execution model cho agent AI, xem thêm:
	- `00_AUTHORITY/Global_Auto_Integration_and_Execution_Rule.md`
Khi làm việc trong ATP repo và có mâu thuẫn giữa tài liệu, ưu tiên theo thứ tự:

1. human-approved current task instruction
2. repo-local governance/authority files trong ATP repo, đặc biệt `AGENTS.md` và freeze decision record hiện hành
3. active repo-local execution docs / implementation plan / architecture docs
4. AI_OS project files như continuity/planning context
5. repo state thực tế nếu phù hợp với các authority docs trên

Nếu AI_OS projected planning wording mâu thuẫn với accepted repo-local execution reality → không dùng AI_OS projection để override repo-local accepted truth; phải surface mismatch và cập nhật projection wording theo bounded governance pass.

---

## 3. Development doctrine

- **Governance-first**: mọi thay đổi phải bám architecture doctrine trước khi implementation
- **Slice-based bounded development**: mỗi slice narrow, testable, verifiable, traceable
- **Review → consolidation → freeze chain**: bắt buộc trước khi version được coi là done
- **Không mở scope mới** khi chưa có evidence justify
- **Không nhảy version/minor line** khi major intent hiện tại chưa đủ dày
- **Stable core** không được thay đổi tùy tiện — thay đổi core cần human-approved architectural decision

Stable core của ATP bao gồm tối thiểu:
- repo/workspace boundary
- control-plane shape
- artifact lifecycle discipline
- human-gated flow

## Current Baseline (excerpt)
File: 20_PROJECTS/ATP/AI_CURRENT_BASELINE.md
SHA256: e2bce1d184a84d346ea90c86046180ed11f2a82434f1fcf220560acfaa55a2a8
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.0.4
- **Last synced:** 2026-04-25 (via aios sync reverse)

## Status


## Runtime modules
  (none detected)

## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: 52a5c1f6218d075706b18c74484970a8e5fa6725f56e35a24fd8cb2722299228
----
# AI Next Step — ATP

- **Last updated:** 2026-04-25
- **Phase:** v2.0.4 — `tdf-run` bridge provider (P3 ATP↔TDF integration)
- **Current state:** v2.0.4 implemented locally; commits + push + tag pending human approval.

---

## 1. Current state

ATP v2.0.0 released. Full cloud AI production stack now present:
- **v1.8.0:** OpenAI adapter + retry/backoff + per-model cost/timeout
- **v1.9.0:** Tool use + JSON mode + vision + capabilities matrix
- **v2.0.0:** SSE streaming + request cancellation + in-flight tracker

AIOS-OC v2.9.1's abort feature now has end-to-end ATP integration via `DELETE /runs/<id>`.

---

## 2. ATP architectural status: MATURE

All critical cloud AI gaps closed:
- ✅ OpenAI + Anthropic (end-to-end, not just auto-detection)
- ✅ Retry/backoff on 429/5xx/network
- ✅ Per-model pricing (13 models) + per-model timeout
- ✅ Tool use / function calling (both providers)
- ✅ JSON mode / structured outputs (both providers)
- ✅ Vision (image inputs, cloud only)
- ✅ SSE streaming with token/tool/manifest events
- ✅ Request cancellation via DELETE /runs/<id>
- ✅ In-flight tracking for monitoring

Remaining stubs (not blockers):
- SSH remote execution (no use case)
- 4 placeholder adapter dirs (architectural slots, no roadmap)
- Streaming not yet supported for Ollama adapter

---

## 3. Possible next steps (all require human approval)

1. **Commit + push + tag v2.0.4** — tdf-run provider locally implemented and tested (16/16 unit tests pass); requires explicit approval per GSGR before push/tag
2. **End-to-end test** with TDF Web Panel running tại `:4180` — `curl -X POST http://localhost:8765/run -d '{"provider":"tdf-run","target":{"tool":"ops/checkos"},"mode":{"dry_run":true}}'`
3. **AIOS-OC UI integration of streaming + cancellation**
   - Wire `/run/stream` into AIOS-OC analyze node
   - Wire `DELETE /runs/<id>` for true abort UX
4. **Streaming for Ollama adapter** — current v2.0.x is cloud-only
5. **Batch API support** — OpenAI batch endpoints
6. **AOKP v2.4+ enrichments** — deeper knowledge integration
7. **Agentic multi-tool loop** — server-side tool execution

---

## 4. Out-of-scope

- Không mở bounded line mới khi chưa có human approval
- Không reopen frozen feature chains
- Không merge/push/tag khi chưa có explicit approval

---

## 5. Version consistency rule (`uv` — Global_Post_Dev_Version_Bump_Rule.md)

Khi bump version / tag release cho ATP, PHẢI update đồng bộ tất cả 7 files:

1. `VERSION` — bump to new version
2. `pyproject.toml` — version field
3. `CHANGELOG.md` — new entry with date and changes
4. `README.md` — baseline version reference
5. `AGENTS.md` — version in identity section
6. `~/AI_OS/20_PROJECTS/ATP/AI_CURRENT_BASELINE.md` — version, commit, lineage
7. `~/AI_OS/20_PROJECTS/ATP/AI_NEXT_STEP.md` — phase, current state

**Enforcement:** CLAUDE.md and AGENTS.md in ATP repo explicitly reference this rule and block `git tag` if any of the 7 files still shows old version.

## Cross-Session Context (CTX-P0)
Workspace ID: `f557573632b576e4` (SHA-256 first-16-hex of canonical repo path)
Active WIPs in this workspace: 0

Live cross-session context (active WIPs detail, recent decisions, last handoff snippet,
parent session linkage) is available via MCP-CTX-P0 tools — not embedded here to keep
CLAUDE.md stable for commits. Call from any Claude Code session:

- `get_session_context(workspace=<this repo path>)` — full hydration block
- `bind_session(claude_session_id, workspace)` — register this chat in session log
- `get_last_handoff(project)` — fetch full AI_HANDOFF_LATEST.md (4 KB cap)
- `mark_continuation(parent, child)` — link this chat to a prior one

Audit log: `~/AI_OS/30_RUNTIME/state/ctx_audit.jsonl` (every CTX call recorded).
Workspace registry: `~/AI_OS/30_RUNTIME/state/workspace_index.json` (workspace_id → metadata).


## AI_OS Multi-AI Ecosystem — READ FIRST (for any AI agent)

**Primer canonical:** `~/AI_OS/00_AUTHORITY/AI_OS_ECOSYSTEM_PRIMER.md` — 6-plane model, non-negotiable rules, boot checklist. Mọi AI agent (Claude Code / ChatGPT / Cursor / Copilot / Codex / …) đọc file này trước khi viết dòng code đầu tiên trong ecosystem.

**Drift guard automation đã kích hoạt:**
- `aios drift` — scan toàn ecosystem (repo VERSION vs pack baseline).
- Git `post-commit` hook: commit đổi `VERSION` → tự chạy `aios sync reverse <PROJECT> --apply` (step 4 của rule `uv`).
- Claude Code `SessionStart` hook: mọi chat mới in primer + `aios drift` status ngay đầu phiên. Skill `/uv` có sẵn.

Shorthand `uv` = 5 bước (`01_PERSONAL/GLOBAL_SHORTHAND_RULES.md:124`). Step 4 (reverse-sync pack) là **bắt buộc, không được skip**.

---

## AI_OS — Portable operating-context / onboarding gate (V4)

Output này do lệnh runtime `aios pr context <TARGET>` sinh ra (stdout hoặc `--copy` / `--copy-clipboard`).
Target **AI_OS** = self repo → trích từ `30_RUNTIME/self_project_pack/` (**không** qua `20_PROJECTS/AI_OS/`). Target khác → `20_PROJECTS/<PROJECT>/`.
Đây là **portable operating-context excerpt**, **không** thay thế pack `pr-con*` đầy đủ khi cần onboarding + shorthand + section GSGR theo spec export.

### Executor (AI nhận paste) — bắt buộc trước task quan trọng

1. Tuân `00_AUTHORITY/Global_AI_OS_Portable_Onboarding_Rule.md`: **acknowledgment** (6 mục §3) + **comprehension gate** (7 câu §4).
2. **Fail-closed:** thiếu file/context/authority → nêu rõ thiếu gì; **không** bịa repo state, branch, approval.
3. Chỉ dán block này **không** = đã onboard nếu chưa làm bước (1).

### Git-safe / GSGR (khi task có thể chạm Git repo)

- Luồng: **Check → Switch → Re-check → Execute**.
- **Ưu tiên** `gsgr ...` thay vì `git` raw, trừ khi authority chỉ rõ khác.
- **Không** giả định branch hiện tại đã đúng.
- Doctrine: `00_AUTHORITY/Global_Safe_Git_Branch_Guard_Rule.md`; neo repo-local: `START_HERE.md` (mục GSGR).

### Gói paste đầy đủ hơn

- Workspace/shorthand: `pr-con <PROJECT>` / `pr-con-copy <PROJECT>` — `01_PERSONAL/AI_OS_PR_CON_SYSTEM_SPEC.md`.
- Handoff phiên: `aios pr handoff <PROJECT>` hoặc `AI_HANDOFF_LATEST.md` trong pack.

AIOS7L HANDOFF
Project: ATP
File: 20_PROJECTS/ATP/AI_HANDOFF_LATEST.md
SHA256: 3db7e1da7ae56377d373ac976f14ce7de44a053b7da2c048d920d59cbe9c4f1d
----
# AI_HANDOFF_LATEST — ATP

## Handoff: v2.0.4 — reverse sync from source repo
**Date**: 2026-04-25

### What changed in v2.0.4
## [2.0.4] — 2026-04-25

### Added — `tdf-run` bridge provider (P3 ATP↔TDF integration)

- `bridge/tdf_run.py` — new non-LLM provider that dispatches structured
  execution tasks to TDF Web Control Panel's `/api/exec/execute` endpoint
  (port `:4180`). Pass-through pattern: ATP owns task envelope + governance
  classification; TDF owns bounded execution + RBAC + audit trail.
- Routing in `bridge/openclaw_bridge.py`: requests with explicit
  `provider="tdf-run"` short-circuit BEFORE the `text`/`model` parser
  (TDF tasks carry structured target/params/mode envelopes, not prompts).
- Governance class mapping (per `~/SOURCE_DEV/products/TDF/tdf/docs/integrations/ATP_BRIDGE_INTEGRATION.md`):
    - `dry_run: true` → class **C** (auto-approved, preview only)
    - `validate` / non-destructive ops real → class **C**
    - `deploy.*` / `install.*` real → class **B** (requires human gate)
    - `rollback.*` / `uninstall.*` / `undeploy.*` real → class **A** (strict review)
- Env var: `TDF_WEB_URL` (default `http://localhost:4180`)
- 16 unit tests in `tests/unit/test_tdf_run.py`: validation, success path,
  failure modes (HTTP error, unreachable TDF, non-JSON response),
  governance class mapping for all op types.

### Why
Closes the P3 connection point in the AI_OS ecosystem roadmap. TDF v6.7.0
shipped a contract + reference Python skeleton in October 2025; this
release wires the ATP side. AOKP and AIOS-OC remain independent of this
provider — it only affects ATP's bridge dispatch table.

---


## Handoff: v2.0.3 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.3
## [2.0.3] — 2026-04-19

### Added — codex + cursor CLI-agent adapters (parity with claude-code)

- `adapters/codex.py` — `CodexAdapter` spawns OpenAI `codex` CLI in the
  target repo. Template rendering + same base_ctx helpers as
  claude_code (uppercase REPO / BRANCH / YYYYMMDD / etc.). Validates
  `codex --version` + `OPENAI_API_KEY` at execute().
- `adapters/cursor.py` — `CursorAdapter` spawns Cursor `cursor-agent`
  CLI. Same config shape; Cursor's own auth handles credentials (no
  API key env needed). `FileNotFoundError` caught with install hint
  pointing to cursor.com/docs/cli.
- `bridge/bridge_server.py` — router refactored: new
  `_run_cli_agent_adapter(incoming, adapter_kind)` handles all 3
  (`claude-code` | `codex` | `cursor`) so adding a 4th adapter is a
  one-branch change. Back-compat shim `_run_claude_code_adapter` still
  exports the old name.
- CodexAdapterConfig + CursorAdapterConfig accept `workspace_dir` +
  `isolation` for interface parity with ClaudeCodeAdapterConfig, even
  though the CLI flow doesn't use them yet.

### Added — launchd wrapper reads Keychain for API keys

- `~/AI_OS/30_RUNTIME/agents/launchd/atp-bridge-start.sh` — resolves
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `CURSOR_API_KEY` from macOS
  Keychain (service names match env-var names — same service names
  AIOS-OC `/api/keys` writes to). Explicit PATH + full-path python3
  ensures Homebrew Python 3.14 (with jinja2) instead of
  CommandLineTools 3.9. plist now execs this wrapper.

---


## Handoff: v2.0.3 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.3
## [2.0.3] — 2026-04-19

### Added — codex + cursor CLI-agent adapters (parity with claude-code)

- `adapters/codex.py` — `CodexAdapter` spawns OpenAI `codex` CLI in the
  target repo. Template rendering + same base_ctx helpers as
  claude_code (uppercase REPO / BRANCH / YYYYMMDD / etc.). Validates
  `codex --version` + `OPENAI_API_KEY` at execute().
- `adapters/cursor.py` — `CursorAdapter` spawns Cursor `cursor-agent`
  CLI. Same config shape; Cursor's own auth handles credentials (no
  API key env needed). `FileNotFoundError` caught with install hint
  pointing to cursor.com/docs/cli.
- `bridge/bridge_server.py` — router refactored: new
  `_run_cli_agent_adapter(incoming, adapter_kind)` handles all 3
  (`claude-code` | `codex` | `cursor`) so adding a 4th adapter is a
  one-branch change. Back-compat shim `_run_claude_code_adapter` still
  exports the old name.
- CodexAdapterConfig + CursorAdapterConfig accept `workspace_dir` +
  `isolation` for interface parity with ClaudeCodeAdapterConfig, even
  though the CLI flow doesn't use them yet.

### Added — launchd wrapper reads Keychain for API keys

- `~/AI_OS/30_RUNTIME/agents/launchd/atp-bridge-start.sh` — resolves
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `CURSOR_API_KEY` from macOS
  Keychain (service names match env-var names — same service names
  AIOS-OC `/api/keys` writes to). Explicit PATH + full-path python3
  ensures Homebrew Python 3.14 (with jinja2) instead of
  CommandLineTools 3.9. plist now execs this wrapper.

---


## Handoff: v2.0.2 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.2
## [2.0.2] — 2026-04-19

### Fixed — claude-code adapter template ctx + bridge persist silent-fail

- **`adapters/claude_code.py` `_render_template`** — base Jinja context now
  includes uppercase aliases (`REPO`, `BRANCH`, `MODEL`, `SCOPE_SUMMARY`,
  `ISO_TIMESTAMP`, `NOW`, `TIMESTAMP`, `YYYYMMDD`, `YYYY`, `MM`, `DD`,
  `HHMM`, `HH`, `YYYYMMDD_HHMM`) in addition to the existing lowercase
  keys. Fixes `'YYYYMMDD' is undefined` Jinja errors when rendering
  playbook templates under `~/SOURCE_DEV/meta/claude-playbooks/prompts/`.
- **`bridge/bridge_server.py` persistence reporting** — when
  `persist_bridge_run` returns `{persisted: False, reason: "…"}`, the
  bridge response now surfaces the reason (as
  `persistence: {persisted: false, reason}`) and emits a structured
  `bridge.persist.error` log event, instead of the previous silent drop
  that made `persistence: null` responses indistinguishable from
  "persistence disabled". Unchanged for `reason == "disabled"` (benign).
- Verified end-to-end with AIOS-OC v3.8.0 Flow Canvas — a full
  `claude-code-agent` run (AOKP repo, prompts/01-uv-version-bump.md,
  sonnet) now persists to `~/SOURCE_DEV/workspace/atp-runs/<req_id>/`
  with request/routing/executor-outputs zones + run-summary.json.

---


## Handoff: v2.0.2 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.2
## [2.0.2] — 2026-04-19

### Fixed — claude-code adapter template ctx + bridge persist silent-fail

- **`adapters/claude_code.py` `_render_template`** — base Jinja context now
  includes uppercase aliases (`REPO`, `BRANCH`, `MODEL`, `SCOPE_SUMMARY`,
  `ISO_TIMESTAMP`, `NOW`, `TIMESTAMP`, `YYYYMMDD`, `YYYY`, `MM`, `DD`,
  `HHMM`, `HH`, `YYYYMMDD_HHMM`) in addition to the existing lowercase
  keys. Fixes `'YYYYMMDD' is undefined` Jinja errors when rendering
  playbook templates under `~/SOURCE_DEV/meta/claude-playbooks/prompts/`.
- **`bridge/bridge_server.py` persistence reporting** — when
  `persist_bridge_run` returns `{persisted: False, reason: "…"}`, the
  bridge response now surfaces the reason (as
  `persistence: {persisted: false, reason}`) and emits a structured
  `bridge.persist.error` log event, instead of the previous silent drop
  that made `persistence: null` responses indistinguishable from
  "persistence disabled". Unchanged for `reason == "disabled"` (benign).
- Verified end-to-end with AIOS-OC v3.8.0 Flow Canvas — a full
  `claude-code-agent` run (AOKP repo, prompts/01-uv-version-bump.md,
  sonnet) now persists to `~/SOURCE_DEV/workspace/atp-runs/<req_id>/`
  with request/routing/executor-outputs zones + run-summary.json.

---


## Handoff: v2.0.1 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.1
## [2.0.1] — 2026-04-19

### Chore — ecosystem alignment bump
- Administrative patch bump as part of `uv all` (option B) across managed projects. ATP's `/run` and governance-hook behaviour unchanged; no new provider adapters added in this release.
- aios-flow (§5.4.1) is now a formal Transformation subsystem that consumes ATP `/run` per step — reconfirms the boundary that **every LLM / adapter call still flows through ATP**; aios-flow never calls providers directly.
- Pack hydrated via `aios sync reverse ATP --apply`.

---


## Handoff: v2.0.1 — reverse sync from source repo
**Date**: 2026-04-19

### What changed in v2.0.1
## [2.0.1] — 2026-04-19

### Chore — ecosystem alignment bump
- Administrative patch bump as part of `uv all` (option B) across managed projects. ATP's `/run` and governance-hook behaviour unchanged; no new provider adapters added in this release.
- aios-flow (§5.4.1) is now a formal Transformation subsystem that consumes ATP `/run` per step — reconfirms the boundary that **every LLM / adapter call still flows through ATP**; aios-flow never calls providers directly.
- Pack hydrated via `aios sync reverse ATP --apply`.

---


## Handoff: v2.0.0 — reverse sync from source repo
**Date**: 2026-04-18

### What changed in v2.0.0
## [2.0.0] — 2026-04-15

### Added — Streaming & Cancellation (BREAKING)
- **SSE streaming endpoint** `POST /run/stream` — Server-Sent Events streaming for cloud adapters
  - Events: `start`, `token`, `tool_call`, `manifest`, `error`, `done`, `aborted`
  - Supported by Anthropic and OpenAI (Ollama/local not supported in v2.0.0)
  - Optional `request_id` in body; auto-generated `stream-<hash>` if omitted
  - Respects `MODEL_ALLOWLIST` + `MAX_BODY_BYTES` security checks
- **Request cancellation** `DELETE /runs/<id>` — abort in-flight request
  - Sets abort event on in-flight tracker; adapter checks between SSE chunks
  - Adapter yields `aborted` event and stops when flag set
  - Returns 200 `{cancelled: true}` for active requests, 404 otherwise
- **In-flight tracker** (`core/in_flight_tracker.py`) — thread-safe request registry
  - `register(request_id, provider, model)` → `threading.Event`
  - `cancel(request_id)` → bool
  - `list_active()` → snapshot of active requests
  - `GET /runs/active` lists in-flight requests for AIOS-OC monitoring
- **SSE formatter** (`core/streaming.py`) — canonical event emission
- **Anthropic streaming** (`execute_anthropic_stream`) — uses `stream=true` Messages API
  - Parses `content_block_delta`, `content_block_start/stop`, `message_delta`
  - Streams text deltas + accumulated tool_use input JSON
  - Captures `stop_reason`, token usage at stream end
- **OpenAI streaming** (`execute_openai_stream`) — uses `stream=true` + `stream_options.include_usage`
  - Aggregates tool_calls piecewise (OpenAI streams function arguments as partial strings)
  - Captures `finish_reason`, token usage from final chunk

### Changed
- Bridge server docstring updated for 3 new endpoints
- AIOS-OC v2.9.1 abort feature now has end-to-end ATP integration (finally wire-compatible)

---


## Handoff: v2.0.0 — reverse sync from source repo
**Date**: 2026-04-15

### What changed in v2.0.0
## [2.0.0] — 2026-04-15

### Added — Streaming & Cancellation (BREAKING)
- **SSE streaming endpoint** `POST /run/stream` — Server-Sent Events streaming for cloud adapters
  - Events: `start`, `token`, `tool_call`, `manifest`, `error`, `done`, `aborted`
  - Supported by Anthropic and OpenAI (Ollama/local not supported in v2.0.0)
  - Optional `request_id` in body; auto-generated `stream-<hash>` if omitted
  - Respects `MODEL_ALLOWLIST` + `MAX_BODY_BYTES` security checks
- **Request cancellation** `DELETE /runs/<id>` — abort in-flight request
  - Sets abort event on in-flight tracker; adapter checks between SSE chunks
  - Adapter yields `aborted` event and stops when flag set
  - Returns 200 `{cancelled: true}` for active requests, 404 otherwise
- **In-flight tracker** (`core/in_flight_tracker.py`) — thread-safe request registry
  - `register(request_id, provider, model)` → `threading.Event`
  - `cancel(request_id)` → bool
  - `list_active()` → snapshot of active requests
  - `GET /runs/active` lists in-flight requests for AIOS-OC monitoring
- **SSE formatter** (`core/streaming.py`) — canonical event emission
- **Anthropic streaming** (`execute_anthropic_stream`) — uses `stream=true` Messages API
  - Parses `content_block_delta`, `content_block_start/stop`, `message_delta`
  - Streams text deltas + accumulated tool_use input JSON
  - Captures `stop_reason`, token usage at stream end
- **OpenAI streaming** (`execute_openai_stream`) — uses `stream=true` + `stream_options.include_usage`
  - Aggregates tool_calls piecewise (OpenAI streams function arguments as partial strings)
  - Captures `finish_reason`, token usage from final chunk

### Changed
- Bridge server docstring updated for 3 new endpoints
- AIOS-OC v2.9.1 abort feature now has end-to-end ATP integration (finally wire-compatible)

---


- **Last updated:** 2026-04-13
- **Suggested chat name:** `ATP v1.6.0 released — all gaps closed`

---

## HANDOFF BLOCK — copy this block into a new chat if needed

You are joining an active project workflow.

**Project:** ATP
**Repo:** ~/SOURCE_DEV/platforms/ATP
**Branch:** `main` (stable, HEAD = a4f8bbd)
**Baseline:** `v1.6.0` — **RELEASED** (tagged + pushed 2026-04-13)

**Phase:** Complete — all architectural gaps closed
**Current state:**
- v1.6.0 released: observability & hardening (config, structured logging, error codes, cost tracking, security)
- 375+ tests PASS
- Full lineage: v0.7.0 → v1.0.0–v1.0.4 → v1.1.0 → v1.2.0 → v1.3.0 → v1.4.0 → v1.5.0 → v1.6.0
- PR #15 merged (feature/v1.6-observability-hardening)

**Next step:** Requires human approval — possible directions:
1. AIOS-OC deep ATP integration
2. AOKP improvements
3. New product target

**Open gates (approval required):**
- Any new bounded line / feature work
- merge/push/tag on main

**Rules in effect:**
- GSGR: Check → Switch → Re-check → Execute
- Auto-Integration: `00_AUTHORITY/Global_Auto_Integration_and_Execution_Rule.md`
- Version bump: `00_AUTHORITY/Global_Post_Dev_Version_Bump_Rule.md`
- Approval required for: merge `main`, push `main`, tag release, new bounded line

**Context files:**
- `20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md`
- `20_PROJECTS/ATP/AI_NEXT_STEP.md`
- `20_PROJECTS/ATP/AI_CURRENT_BASELINE.md`

---

## Lineage summary

```text
v0.7.0  <- final v0 baseline (frozen)
  ->
v1.0.0–v1.0.4  <- Slices A–E (all frozen)
  ->
v1.1.0  <- Ollama + Anthropic + bridge + governance gate (frozen)
  ->
v1.2.0  <- Structural hardening (frozen)
  ->
v1.3.0  <- AOKP Phase 1 knowledge integration (frozen)
  ->
v1.4.0  <- Gaps closure: schema validation, bridge introspection, docs (frozen)
  ->
v1.5.0  <- Artifact persistence M8 (frozen)
  ->
v1.6.0  <- Observability & hardening: config, logging, error codes, cost, security
           PR #15 merged, tagged v1.6.0, pushed (2026-04-13) ✅
```
<!-- AI_OS:END MANAGED BLOCK -->
