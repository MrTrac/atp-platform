# AGENTS.md

This file is the mandatory governance file for AI agents operating in ATP. These rules are binding unless a human explicitly overrides them for the current task.

## Repository identity

ATP is a platform repository at `SOURCE_DEV/platforms/ATP`.

ATP is a governance-first platform at v2.1.0 baseline. Preserve its frozen boundary discipline, control-plane shape, registry shape, adapter shape, artifact lifecycle, and human-gated flow.

Current runtime components (v2.1.0):
- **Ollama adapter:** local LLM execution (qwen3:14b, qwen3:8b, deepseek-r1:8b)
- **Anthropic adapter:** cloud + retry + pricing + tool use + JSON mode + vision + streaming
- **OpenAI adapter:** gpt-4o/5 + o1/o3 + retry + pricing + tool use + JSON mode + vision + streaming
- **AOKP adapter (v2.3.x):** 6 endpoints — health, search, graph, chat, graph-rag, temporal (opt-in)
- **tdf-run bridge provider:** structured task dispatch to TDF Web Panel :4180 (governance-classified A–C)
- **aios-flow adapter:** DAG workflow dispatch to aios-flow :7700 via POST /api/runs
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
GeneratedAtUTC: 20260429T144152Z

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
SHA256: e90116aece69b7883faddf564bba5818160470a64d9b42dc67ac548617311163
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.0.4
- **Last synced:** 2026-04-29 (via aios sync reverse)

## Status


## Runtime modules
  (none detected)

## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: da72375dee6f71f3e17992f91aa160f9adeb20c64b8ac178751d930f186102df
----
# AI Next Step — ATP

- **Last updated:** 2026-04-29
- **Phase:** v2.1.0 — Doctrine v5 compliance (G9 observability + aios-flow adapter + evaluator wiring)
- **Current state:** v2.1.0 implemented in worktree; commits + merge gate + tag pending human approval.

---

## 1. Current state

ATP v2.1.0 implements all 5 Doctrine v5 compliance items:
- ✅ **D1:** Doctrine §4 fixed — `FastAPI` → `stdlib HTTP server (no framework)`
- ✅ **D2:** `AI_CURRENT_BASELINE.md` expanded (13 → 100 lines, closes DP#22)
- ✅ **D3:** G9 recordTrace() — `core/trace.py` + instrumented AOKP (×3), TDF (×1), aios-flow (×1)
- ✅ **D4:** `adapters/aios_flow/` adapter + `registry/providers/aios_flow.yaml` + routing
- ✅ **D5:** `core/evaluator.py` + evaluator hook in `bridge/openclaw_bridge.py`
- 28 new unit tests pass; 419 total passing

---

## 2. ATP architectural status: MATURE + DOCTRINE-COMPLIANT

All critical gaps closed (v2.0.0 + v2.0.1–v2.0.4 + v2.1.0):
- ✅ OpenAI + Anthropic + Ollama (LLM providers)
- ✅ Retry/backoff on 429/5xx/network
- ✅ Per-model pricing (13 models) + per-model timeout
- ✅ Tool use / function calling (both cloud providers)
- ✅ JSON mode / structured outputs (both cloud providers)
- ✅ Vision (image inputs, cloud only)
- ✅ SSE streaming with token/tool/manifest events
- ✅ Request cancellation via DELETE /runs/<id>
- ✅ In-flight tracking for monitoring
- ✅ tdf-run bridge provider (P3 ATP↔TDF)
- ✅ aios-flow adapter (P4 ATP→aios-flow DAG dispatch)
- ✅ G9 cross-module observability (80% coverage achieved)
- ✅ Evaluator pattern (http-probe native; llm-judge/visual-diff → stub)

Remaining stubs (not blockers):
- SSH remote execution (no use case)
- 4 placeholder adapter dirs (architectural slots, no roadmap)
- Streaming not yet supported for Ollama adapter
- llm-judge + visual-diff evaluator native (aios-flow delegation stub sufficient)

---

## 3. Possible next steps (all require human approval)

1. **Merge + tag v2.1.0** — all items implemented and tested; requires explicit GSGR approval
2. **AIOS-OC UI integration of streaming + cancellation**
   - Wire `/run/stream` into AIOS-OC analyze node
   - Wire `DELETE /runs/<id>` for true abort UX
3. **aios-flow Phase 2** — polling/wait for flow run completion (DP#130 Phase 2)
4. **llm-judge evaluator native** — wire to aios-flow delegation properly
5. **Streaming for Ollama adapter** — current v2.0.x is cloud-only
6. **Batch API support** — OpenAI batch endpoints
7. **AOKP v2.4+ enrichments** — deeper knowledge integration

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
<!-- AI_OS:END MANAGED BLOCK -->
