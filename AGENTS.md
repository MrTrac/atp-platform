# AGENTS.md

This file is the mandatory governance file for AI agents operating in ATP. These rules are binding unless a human explicitly overrides them for the current task.

## Repository identity

ATP is a platform repository at `SOURCE_DEV/platforms/ATP`.

ATP is a governance-first platform at v2.6.4 baseline. Preserve its frozen boundary discipline, control-plane shape, registry shape, adapter shape, artifact lifecycle, and human-gated flow.

Current runtime components (v2.6.4):
- **Anthropic adapter:** cloud + retry + pricing + tool use + JSON mode + vision + streaming
- **OpenAI adapter:** gpt-4o/5 + o1/o3 + retry + pricing + tool use + JSON mode + vision + streaming + **Batch API** (v2.3.0) + **batch wait helper** (v2.5.0)
- **AOKP adapter (v2.3.x):** 6 endpoints — health, search, graph, chat, graph-rag, temporal (opt-in)
- **tdf-run bridge provider:** structured task dispatch to TDF Web Panel :4180 (governance-classified A–C)
- **aios-flow adapter:** DAG workflow dispatch + **status + wait actions** (v2.4.0) for full lifecycle (:7700)
- **Bridge server:** stdlib HTTP (no framework) at localhost:8765 (12 endpoints incl. /run/stream, /runs/active, DELETE /runs/<id>)
- **SSE streaming:** `POST /run/stream` emits event-stream (start/token/tool_call/manifest/done/aborted)
- **Request cancellation:** `DELETE /runs/<id>` aborts in-flight via threading.Event
- **In-flight tracker:** core/in_flight_tracker.py (thread-safe registry)
- **Evaluator:** core/evaluator.py — post-run validation (http-probe native; llm-judge/visual-diff → aios-flow stub)
- **G9 observability:** core/trace.py — W3C traceparent headers + cross_module_trace.jsonl (ATP→AOKP, ATP→TDF, ATP→aios-flow)
- **Capabilities matrix:** llm_chat, llm_completion, llm_tool_use, llm_json_mode, llm_vision
- **Pricing registry:** registry/pricing/model_prices.json (13 models)
- **Retry logic:** core/retry.py (exponential backoff for 429/5xx/network)
- **Per-model timeout:** ATP_MODEL_TIMEOUTS env var
- **Governance hook:** aios-gate (tier A-E)
- **Persistence:** artifact store + run history (opt-in)
- **Observability:** central config, structured JSON logging, typed error codes

## Binding source-of-truth order

Apply this hierarchy in order:

1. human-approved current task instruction
2. `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
3. ATP v0 implementation plan and architecture docs
4. design, operators, and governance docs
5. existing code and file layout

This order must not be silently inverted.

## Mandatory repository boundaries

- `SOURCE_DEV/` is the logical workspace root
- `SOURCE_DEV/platforms/ATP` is the ATP source repo
- `SOURCE_DEV/products/TDF` is the product repo ATP resolves in v0
- `SOURCE_DEV/workspace` is the runtime zone for runs, artifacts, exchange, and logs

Runtime artifacts, run outputs, exchange bundles, logs, and similar operational output must not live in this repo.

## Documentation and naming rules

- Keep glossary, naming, schema, and artifact terminology aligned with ATP docs
- Do not invent new vocabulary when ATP already has a valid term
- Do not rename files, concepts, modules, or contracts casually
- If a rename is truly necessary, preserve traceability and keep the smallest justified change set

## Architecture and scope rules

- ATP v0 is a shape-correct MVP, not a license for scope drift
- Preserve repo boundary, control-plane shape, registry shape, adapter shape, artifact lifecycle, and human-gated flow
- Do not expand scope outside the frozen ATP v0 architecture unless a clear human-approved decision allows it
- Prefer refinement, normalization, and hardening over premature feature expansion

## Change behavior

- Prefer minimal justified churn
- Avoid speculative restructuring
- Avoid hidden behavior changes
- If a requested change conflicts with the ATP baseline, do not apply it silently; surface the conflict and propose the smallest valid next step

## Archive and artifact discipline

- `archive/` is for historical traceability, not active authority
- Frozen snapshot packs must remain frozen
- Generated bundles, temporary review outputs, and ad hoc working artifacts should not remain at repo root unless explicitly intended

## When uncertain

- Do not guess architecture
- Do not expand scope implicitly
- Do not invent new authority paths
- Do not create new modules or contracts without basis
- Prefer documenting the gap, conflict, or required decision

## Version sync rule (mandatory before tag release)

Authority: `00_AUTHORITY/Global_Post_Dev_Version_Bump_Rule.md`
Shorthand: `uv` = execute this rule

When preparing a tag release, ALL these files MUST be updated atomically:

1. `VERSION` — bump to new version
2. `pyproject.toml` — version field
3. `CHANGELOG.md` — new entry with date and changes
4. `README.md` — baseline version reference
5. `AGENTS.md` — this file, version in identity section
6. `~/AI_OS/20_PROJECTS/ATP/AI_CURRENT_BASELINE.md` — version, commit, lineage
7. `~/AI_OS/20_PROJECTS/ATP/AI_NEXT_STEP.md` — phase, current state

DO NOT run `git tag` if any file above still references an old version.
If version mismatch detected, fix ALL files first, then tag.

## Working principle

Preserve boundaries strictly. Follow the source of truth in order. Make the smallest justified change. Keep ATP human-gated.

<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=AGENTS -->
AIOS7L CONTEXT
Project: ATP
GeneratedAtUTC: 20261014T135917Z

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
SHA256: 8bcf3d44abb879d1edaa629146fc201dd3618f6678d9d8bddb1e5fbe73488a7c
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.6.3
- **Released:** 2026-10-14T20:43:55+07:00
- **Last synced:** 2026-10-14 (via aios sync reverse)

## Status



## Runtime modules
  (none detected)


## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: e415e102139504b49260e0db73747de94748b78c33c90cebc35c26fd4a432815
----
# AI Next Step — ATP

- **Last updated:** 2026-10-14
- **Phase:** v2.6.3 — maintenance line after v2.6.0 (Doctrine v6.0 D6.2 closed via M4 scope-cut, ATP synthesis surface complete); v6.1 consumer cutover still open (backlog below)
- **Current state:** v2.6.3 (RELEASED 2026-10-14T20:43:55+07:00). 2.6.1 `/health` reports the real version; 2.6.2 `cli/` stdlib-shadow fix + CI matrix 3.11/3.12 + `jinja2` as optional extra `adapters`; 2.6.3 `write_exchange_bundle` writes to `_shared/exchange/current-task/` like the run writer. Last verified on 2.6.3: `make test` 658 unit passed + 22 integration passed (7 skipped). Known open: bare `python3 -m pytest` fails `test_cli_scripts_start_on_this_interpreter` (`cli/output_contract.py` imports `core` without a `sys.path` shim; passes under `make test` because the Makefile exports `PYTHONPATH=.`). v2.6.0 baseline facts: 8/8 generators functional, 81/81 generator tests pass; AOKP-side cutover deferred to v6.1 per M4 fallback (ATP runbook §3 mid-step gate).

---

## D6.2 closure rationale (M4 scope-cut, 2026-05-04)

ATP runbook §3 mid-step gate authorizes scope-cut when budget burn > 50% above estimate. Original D6.2 estimate: 1.0h. Realistic full-cutover effort: 1+ week. >>50% over → M4 invoked.

**Phase 1 SHIPPED (D6.2 acceptance §9 partial):**
- ✅ ATP exposes generator surface (≥3 generators) — actually 8/8 ported
- ✅ Citation tracking functional
- ⏸ AIOS-OC + ATCC_HCM consume `ATP_*_v3` — deferred v6.1
- ⏸ AOKP no longer hosts generators — deferred v6.1
- ⏸ Lifecycle: stable — incubating until consumer cutover (v6.1)

**Why NOT continue Phase 2 today:** AOKP `synthesizer.ts` has deep value-add ATP doesn't replicate (structured JSON sections + suggestion-engine domain-aware + quality-guard LLM retry + citation-grounding Jaccard verifier + Vietnamese prompt-bank). Naive cutover would degrade AOKP output quality. True cutover = port ~600 LOC TS→Python (6-10h dedicated session, not this scope).

## v6.1 backlog (Phase 2-4 detailed scope)

| Phase | Description | Effort |
|---|---|---|
| **2a** | Port AOKP `quality-guard.ts` + `suggestion-engine.ts` + `citation-grounding.ts` + structured-JSON parser into ATP `generators/stubs/report_v2.py` | 4-6h |
| **2b** | Vietnamese-aware prompt-bank port (synthesis prompts + retry hints) into ATP `generators/prompts/` | 1-2h |
| **2c** | AOKP-side: thin TS client `src/runtime/synthesis/atp-client.ts`; `synthesizer.ts` checks `AOKP_USE_ATP_SYNTHESIS=1` flag → calls ATP `report_v2` | 2-3h |
| **2d** | AOKP unit tests + integration tests against ATP `/api/synthesis/generate` mock | 1-2h |
| **3** | 24h compressed soak (per D8.2 precedent), divergence diff log, flip flag default | 1 day passive |
| **4** | Promote `ATP_AIOS-OC_v3` contract `incubating → stable`, ATP synthesis lifecycle `incubating → stable`, remove (or keep as fallback) AOKP internal `synthesizer.ts` | 1-2h |
| **TOTAL v6.1** | | **9-15h + 1 day soak** |

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
<!-- AI_OS:END MANAGED BLOCK -->

<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=AGCP_AGENTS -->
## AGCP Protocol — canonical at `~/AI_OS/00_AUTHORITY/AGCP_PROTOCOL.md`

**AGCP — Agentic Git Coordination Protocol** — shared rules for all AI agents working on AI_OS-managed repos. Prevents (a) orphan worktrees nobody owns, (b) silent code loss across session/AI handoffs, (c) two AIs racing on the same branch.

**Mandatory for any AI tool touching git in this ecosystem:**
1. **Register worktrees** after `git worktree add` — **ENFORCED since 2026-09-04**, no longer honour-system. Call MCP `register_worktree(path, created_by, branch, session_id)` (Tier 1), or `30_RUNTIME/tools/worktree_registry_gate.sh register <path>` (Tier 2 — this is the real command; the `aios wt register` named in earlier revisions of this document **never existed**, which is one reason compliance was 2/7 in a measured session). Every managed repo now carries a `post-checkout` hook that registers a new worktree **automatically**, so the normal path requires remembering nothing. Anonymous worktrees are out-of-protocol and a cleanup sweep may delete them — that is not hypothetical: on 2026-09-04 two unregistered worktrees holding uncommitted work were removed, and their owner could not be identified from the ledger.
   - Gate: `worktree_registry_gate.sh check|register|scan|install` — `check` exits 2 on an unregistered worktree, 3 when exempt (main worktree, or a path outside `$HOME` which the ledger cannot accept at all).
   - Detector: `scan` is wired into `aios_checks.sh`, so `aios drift` surfaces violations. First measured run reported 35/28 — **that figure was wrong**: `scan` deduplicated by repo path, and `TDF-installed` is a worktree *of* `TDF`, so the same set was counted twice. Corrected by deduplicating on `git-common-dir`: **23 linked worktrees, 20 unregistered (87%)**. Guarded by WT-12, which compares `scan`'s total against an independent count. Same error class as the `find -name .git` mistake made the same day (reported 225 branches where there were 140) — **a path is not an identity for a git repository; `git-common-dir` is**. All 20 were back-filled on 2026-09-04 with notes recording provenance and stating explicitly that ownership was **not** established — a back-fill entry is not an ownership claim.
   - Tests: `30_RUNTIME/tests/test_worktree_registry_gate.sh` — 11 assertions, including WT-05 which reconstructs the 2026-09-04 incident (a worktree created with the hook deliberately bypassed still gets caught).
2. **Acquire lease** before destructive ops (`merge-main`, `tag`, `rebase-main`, `reset`) — `acquire_lease("worktree:<path>"|"branch:<repo_id>::<name>", ttl=1800)`. Branch keys are REPO-QUALIFIED since 2026-08-07: `repo_id` = `<basename>-<8 hex of sha256(resolved git-common-dir)>`. `aios lease acquire` derives it from cwd; over MCP you must pass `repo=<path>` — the server's cwd is not yours. ⚠ A bare `branch:<name>` is still VALID and blocks that branch in **every** repo — deliberate fail-safe, not an error, and nothing warns the party who created it. Lease auto-released on session end or 10min no-heartbeat.
3. **Heartbeat** every 10min (cron) plus on every git op (event-driven) — keeps session alive in registry; expired sessions release leases automatically.
4. **Never bypass GSGR** for destructive git — GSGR pre-hook calls AGCP `propose_action()`. Default mode `warn` (prints, proceeds); CI runs `enforce` (blocks). `--no-agcp` flag exists for emergency bypass when MCP service down — only honored outside `enforce` mode, always logged to bypass audit.
5. **Handoff explicitly** when passing work to another AI — `handoff_to(target_ai_tool, payload)` (Tier 1) or `aios session handoff create <target>` (Tier 2). ⚠ This WRITES a handoff file; it does NOT deliver it to any chat — `target_ai_tool` picks the payload format, it is not an address. Tell the human, or use your harness's own cross-session message tool. Receiving AI binds with `bind_session(parent_session_id=<src>)` (Tier 1) or `aios session start --ai-tool <tool> --parent-session <src> --session-id <yours>` (Tier 2), then `aios session handoff read <handoff-id>`. Close it when done: `aios session handoff close <handoff-id> --resolution done --note "<evidence>"`. ⚠ A handoff hands over the CONVERSATION, not your locks: since 2026-08-12 `release_leases` defaults to **keep**, and the result names every lease still held. Pass `--release-leases` / `release_leases=true` only if you mean the successor — possibly on another machine — may act on them now.
6. **Build ở ĐÚNG máy — `G-BUILDTOPO-1`, bắt buộc.** ⛔ **CẤM `pnpm run build` AOKP trên server** (dù còn RAM): `next build` truy vết tệp sẽ đi bộ cả `data/` **30 GB** → hết bộ nhớ. Đo đối chiếu: server 30 GB RAM **hỏng 2 lần**; CI runner **8 GB** xong **45 giây** (khác biệt duy nhất: checkout sạch không có `data/`). Vi phạm ngày 20/7/2026 đã **phá bản dựng đang phục vụ** (`.next` 51 MB → 1,5 MB) — dịch vụ vẫn trả 200 vì bản cũ nằm trong bộ nhớ, khởi động lại là mất trắng. Trước khi build trên bất kỳ máy đích nào: `du -sh . && du -sh data` → **> 2 GB thì đi CI**. Không chắc → **đi CI** (sai thì mất 45 giây; dựng tại chỗ sai thì mất dịch vụ). Luôn xoay `.next`→`.next.prev` trước khi thay, và **khởi động lại + gọi thật endpoint** mới được nói đã xong. Bảng tra từng module + luồng đầy đủ: **`~/AI_OS/00_AUTHORITY/Global_Build_Deploy_Topology_Rule.md`**. Build nặng buộc phải chạy trên máy Owner thì giữ lease trước: `acquire_lease("host-compute:<machine_id>", ttl=1800, intent="<what>")`; `granted=False` thì **chờ**, không chạy song song. Kill tiến trình thử/gỡ lỗi ngay sau khi dùng. Xem §8.5.

**Full doctrine:** `~/AI_OS/00_AUTHORITY/AGCP_PROTOCOL.md`. AI agents read this file before any worktree/branch/lease action. AI tool capability matrix: `~/AI_OS/01_PERSONAL/AI_TOOL_CAPABILITIES.md`.
<!-- AI_OS:END MANAGED BLOCK -->
