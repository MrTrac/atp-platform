<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=COPILOT -->
AIOS7L CONTEXT
Project: ATP
GeneratedAtUTC: 20261015T042056Z

## Project Context (excerpt)
File: 20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md
SHA256: 35d5453215c4306cb971b3302770cd2ede844ab825acd6ea106626ca6d242da5
----
# AI Project Context — ATP
## Autonomous Task Platform

- **Project:** ATP (Autonomous Task Platform)
- **Repo path:** ~/SOURCE_DEV/platforms/ATP
- **Stable baseline on `main`:** **v2.6.4** (tag `v2.6.4` → `1e8d0c5`, RELEASED 2026-10-14T21:05:12+07:00)
- **Last updated:** 2026-10-14
- **Khiếm khuyết đã biết + trạng thái từng mục:** `~/AI_OS/20_PROJECTS/ATP/AI_ISSUE_LEDGER.yaml` (mã `KD-ATP-<số>`); lịch sử thay đổi: `CHANGELOG.md` trong repo.

---

## 1. ATP là gì

ATP là một platform repository có governance-first discipline, phục vụ bounded execution, review, handoff, và planning support theo repo-local model. ATP phục vụ trục:

```
requested user ⇄ ATP ⇄ products
```

ATP là **Transformation Plane** trong 6-plane multi-AI ecosystem. Current execution reality trên `main` (v2.6.4):

- repo-local, JSON-first, human-gated, bounded
- **provider-abstracted** — execution providers (đối chiếu `registry/providers/*.yaml` + `EXECUTOR_MAP` ngày 2026-10-14):
  - **Anthropic cloud** — provider LLM mặc định (chat + tool_use + json_mode + vision + streaming); model mặc định của cầu nối `claude-haiku-4-5-20251001`, escalation lên Sonnet
  - **OpenAI cloud** (gpt-4o/5, o1, o3 + tool_use + json_mode + vision + streaming + Batch API)
  - **non_llm_execution** — shell/git/build/test/lint chạy local (subprocess)
  - dispatcher mức cầu nối: `tdf-run` (TDF Web Panel :4180), `aios-flow` (DAG workflow :7700)
  - **KHÔNG có LLM local.** Adapter Ollama đã xoá từ v2.6.0; máy macOS không chạy Ollama/model local (`00_AUTHORITY/Global_Mac_No_Ollama_Rule.md`). Provider `ollama/...` không có handler — từ v2.6.4 mặc định của generators cũng không còn trỏ tới nó
- **bridge-enabled** — HTTP bridge server (stdlib) tại localhost:8765; route đối chiếu `bridge/bridge_server.py`:
  - POST `/run` (blocking), `/run/stream` (SSE), `/api/synthesis/generate`
  - DELETE `/runs/<id>` (cancellation)
  - GET `/health` và `/` (từ v2.6.1 trả `version` = phiên bản nền tảng + `released`), `/status`, `/providers`, `/capabilities`, `/runs`, `/runs/active`, `/runs/<id>`, `/api/synthesis/generators`
- **knowledge-integrated** — AOKP adapter (opt-in, 6 truy vấn: health, knowledge, graph, chat, graph-rag, temporal)
- **synthesis generators** (v2.6.0) — 8: analyze, federation, graphrag_synth, react, report, temporal, tot, transform. Cutover phía AOKP/AIOS-OC/ATCC_HCM chưa làm (KD-ATP-006)
- **observable** — central config, structured JSON logging, 7 mã lỗi có kiểu (`core/error_codes.py`)
- **production-resilient / agentic-ready / streaming-capable** — có `core/retry.py`, `core/pricing.py`, `core/streaming.py`, `core/in_flight_tracker.py`
- **governance-gated** — aios-gate phân loại artifacts tier A–E *(mang từ bản v2.0.0, CHƯA kiểm lại ở v2.6.4)*
- non-persistent runtime by default (artifacts optional via ATP_PERSIST_RUNS / ATP_PERSIST_ARTIFACTS)
- non-orchestrating (không có scheduler hay graph execution)
- non-daemonized (bridge server là opt-in, không auto-start)

Current accepted line status (v2.6.4):
- v1.6.0 observability baseline frozen
- v1.7.0 cloud API key passthrough + AOKP v2.3.x frozen
- v1.8.0 Cloud Foundations (OpenAI adapter, retry, pricing, timeout)
- v1.9.0 Agentic Capabilities (tool use, JSON mode, vision, capabilities matrix)
- v2.0.0 Streaming & Cancellation (SSE streaming, DELETE /runs/<id>, in-flight tracker)
- v2.0.1–v2.0.4 ecosystem alignment, codex/cursor adapters, tdf-run bridge provider
- v2.1.0 G9 observability, aios-flow adapter, evaluator wiring · v2.2.0 Ollama streaming parity (lịch sử; Ollama đã xoá ở v2.6.0) · v2.3.0 OpenAI Batch API · v2.4.0 aios-flow status + wait · v2.5.0 OpenAI Batch `wait` helper
- **v2.6.0** Ollama provider removed (Anthropic là mặc định duy nhất) + synthesis generators surface; **v2.6.1** `/health` báo đúng phiên bản + SIGTERM dừng được bridge; **v2.6.2** `cli/inspect.py` che stdlib `inspect` (sửa), CI ma trận 3.11/3.12, `jinja2` là extra tùy chọn `adapters`; **v2.6.3** `write_exchange_bundle` ghi vào `_shared/exchange/current-task/`; **v2.6.4** model mặc định của `generators/llm.py` không còn là `ollama/qwen3:8b`
- (lịch sử) PRs #19, #20, #21 merged 2026-04-15; tagged v1.8.0 / v1.9.0 / v2.0.0

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

## Current Baseline (excerpt)
File: 20_PROJECTS/ATP/AI_CURRENT_BASELINE.md
SHA256: 1fa4716ccb67ca19c5ee5e35123da07661b70af20c6d88f50317e3c9db2a0aa8
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.7.1
- **Released:** 2026-10-15T10:33:20+07:00
- **Last synced:** 2026-10-15 (via aios sync reverse)

## Status



## Runtime modules
  (none detected)


## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: 928684f3b7fb6d2b5d3cec95d8964de2371d09bc199008e82ad99f12062a7dcc
----
# AI Next Step — ATP

- **Last updated:** 2026-10-15
- **Phase:** v2.7.1 — maintenance line after v2.6.0 (Doctrine v6.0 D6.2 closed via M4 scope-cut, ATP synthesis surface complete); v6.1 consumer cutover still open (backlog below)
- **Current state:** v2.7.1 (RELEASED 2026-10-15T10:33:20+07:00) = v2.7.0 + KD-ATP-022 (a missing `aios-gate` no longer turns a successful `/run` into HTTP 500) + `make ci-local`. Running on `aios-server` with the aios-flow authentication ON (KD-ATP-021). `main` is 4 commits ahead and NOT released: generator `report_v2` (KD-ATP-006 phases 2a/2b) and a size guard for the AI-context files. Details: §1.
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

## 1. Current state (verified 2026-10-15 unless marked)

**Release.** v2.7.1 (tag `v2.7.1` -> `4fdc338`, RELEASED 2026-10-15T10:33:20+07:00). Running on `aios-server` from `/opt/aios/atp/current -> releases/2.7.1` since 2026-10-15T03:49:57Z (10:49 +07, on the Owner's order; published to the VPS store by hand, see Deploy path); `/health` = `2.7.1` and the `released` of `RELEASED`, 0 restarts (re-read 2026-10-15). The install checks are in the ledger block `2.7.1`; the 2.7.0 package was checked byte-for-byte against its tag.
**Rollback (KD-ATP-014, `partial`).** Target `2.7.0` (`releases/`: `0-legacy`, `2.7.0`, `2.7.1`; the tool pruned `2.6.6`). `aios-deploy atp --rollback` picks the last successfully activated other release from `/opt/aios/atp/.deploy-history.log` (never `0-legacy`); `--rollback-to <ver>` and `--list` exist; no `--dry-run`. **Manual rollback rehearsed live 2026-10-15 00:47 +07** (Owner's order, 2.7.0 <-> 2.6.6): 2.6 s each way, `/health` right each time, `MainPID` changed, 0 restarts, unserved at most 0.31 s / 0.42 s probed from the Mac (one measurement). **Automatic rollback** (a new release's `/health` fails): never fired on the live service; the sandbox suite `~/AI_OS/30_RUNTIME/tests/deploy_local_rehearsal` was re-run 2026-10-15: **46/46**, on a script with the same sha256 (`6d1d4a8b…`) as `/usr/local/bin/aios-deploy-local` on `aios-server`. Still untried: a rollback with a run in flight.

**History.** The 2.6.4–2.6.6 fixes (KD-ATP-003/008/011/012/013: tests, docs, `HTTPError` closing in the handlers and in `core/retry.with_retry`) are in CHANGELOG `[2.6.5]`/`[2.6.6]` and the ledger; not repeated here (context size, G-CTXBLOAT-1).

**What 2.7.0 and 2.7.1 brought** — details: CHANGELOG and the ledger blocks (statuses are the ledger's):
- **aios-flow authentication (KD-ATP-016 `fixed_verified`; KD-ATP-021 `fixed_verified`: ON on `aios-server`)** — `adapters/aios_flow/identity_token.py`: with `AIOS_FLOW_IDENTITY_URL` set (https/loopback) every aios-flow request carries the `svc:atp` token (secret `AIOS_FLOW_IDENTITY_SECRET`, never logged). The Owner switched it on 14-15/10 (secret typed at a hidden prompt, never seen by an AI); aios-flow 1.2.1 enforces on the server; minting a token and an authenticated read were measured. NOT measured: renewal after a real expiry (only `exp - iat`), TLS to a real https identity. Never set the URL without the secret; never configure it on the Mac (KD-ATP-019).
- **Errors named correctly (KD-ATP-016/017)** — aios-flow failures carry `error_code`, `retryable`, `reason_code`…; a 401 gets one fresh token; `wait` retries transient 429/502/503/504 (4 attempts max); `dispatch` is `retryable` only when no run can have been created.
- **KD-ATP-022 (2.7.1, `fixed_verified`)** — `bridge/governance_hook.run_governance_review` turns a missing/non-executable `aios-gate` into a normal verdict (class E, status error) instead of HTTP 500; re-measured on the server after the install. **KD-ATP-023 (`wontfix`, Owner: keep)**: `aios-server` has no `aios-gate`, so every ATP result there carries `governance_class: E`; reopen if anyone starts to rely on `governance_status`.
- **KD-ATP-020 / 018 / 015 / 009** (`fixed_verified` / `fixed_verified` / `fixed_verified` / `wontfix`) — the agent env keeps the secret out of `claude -p`/`codex exec`/`cursor-agent`; tests no longer write into the real `~/.aios/state/cross_module_trace.jsonl`; an unknown provider on the local node answers HTTP 400 (was 200 `deferred`; only AIOS-OC calls the bridge); the 4 placeholder adapter dirs stay.
- **KD-ATP-019 (`mitigated`, Owner: no code change)** — the bridge listens on `0.0.0.0:8765` unauthenticated; on `aios-server` ufw allows port 8765 only from the Mac `10.88.0.10` (read only, 14/10). Authenticate the bridge before opening it to more hosts.

**On `main` after 2.7.1, NOT released** (CHANGELOG `[Unreleased]`, CI green at `d64275f`): (a) **`report_v2`** (KD-ATP-006 phases 2a/2b, `partial`) — a Python port of AOKP's `src/runtime/synthesis` (sections, domain suggestions, quality guard + retry, Jaccard grounding, KB gap), equal to AOKP on 1,054 golden cases generated from AOKP's TypeScript (commit `51b1139b`); default mode `skeleton` = no model; `real` mode has only run against scripted models, so answer quality from a real model is unmeasured. Nothing calls it yet: the AOKP client (phase 2c/2d) was handed to an AOKP session on 15/10; phase 3 (24 h soak) and 4 (promotion) are not started. (b) `tests/unit/test_context_files_size.py`: the AI-context files must stay under 49,000 bytes (the bridge copies the first 80 lines of this file). `make ci-local` (released in 2.7.1): **run it before every push**.

**Execution stack** (read from `registry/providers/*.yaml`, `EXECUTOR_MAP`, `bridge/bridge_server.py`):
- LLM providers: **Anthropic** (default; bridge default model `claude-haiku-4-5-20251001`) and **OpenAI**. `non_llm_execution` for shell/git/build/test/lint. Bridge-level dispatchers: `tdf-run` (:4180), `aios-flow` (:7700; authenticated as `svc:atp` when configured, ON on `aios-server`). AOKP adapter opt-in (6 queries).
- **No local LLM.** The Ollama adapter was removed in v2.6.0; macOS hosts must not run Ollama or any local model (`Global_Mac_No_Ollama_Rule`). A provider with no handler (e.g. `ollama/...`) on the local node is an error since 2.7.0 (`UnsupportedProviderError`, HTTP 400); only on a node the registry does not know as local does it still fall through to the deferred SSH stub and return `status=deferred`.
- Bridge routes: 12 distinct paths / 13 method+path pairs, all listed in README and AGENTS and guarded by `tests/unit/test_bridge_routes_documented.py`.
- Synthesis generators: 9 (`generators/stubs/`): the 8 originals + `report_v2` (incubating, on `main`, not released). Consumer cutover still open (§D6.2 / v6.1 above).

**Deploy path.** Tag on GitHub -> a watcher publishes it to the VPS release store (it never deploys) -> `aios-deploy atp <version>` (Mac -> `sudo aios-deploy-local atp`): installs into a new `releases/<ver>` directory, swaps `current`, restarts,
requires HTTP 200 **and** the exact version in `/health`, rolls back by itself on failure. See `Global_Build_Deploy_Topology_Rule.md` §5.2c and §8.
Watcher note: `com.aios.publish-watch` runs about every 15 minutes and holds a one-run lock (at 2.7.0 it was busy building `aios-oc@4.6.14`), so `aios-publish atp <ver>` was run by hand after the 2.6.6, 2.7.0 and 2.7.1 tags (the same work it does; it does NOT deploy; idempotent for the same tag).

**Tests.** `main` at `d64275f`: 996 unit (+49 subtests) + 26 integration passed (7 skipped); CI green on 3.11 and 3.12 (run 38680613505) and `make ci-local` the same. At the `v2.7.0` tag in the clean environment: 931 + 26. CHANGELOG `[2.7.0]` quotes 944 passed: it was measured on the release branch BEFORE `main` (with KD-ATP-015's 13 tests: 9 + 4) was merged into it; 944 + 13 = 957. Not an error.

---

## 2. Architectural status: MATURE, with the gaps listed below

Verified in code on 2026-10-14:
- ✅ Anthropic + OpenAI handlers in `EXECUTOR_MAP`
- ✅ Retry/backoff (`core/retry.py`), pricing table (`core/pricing.py`), typed error codes (7, `core/error_codes.py`)
- ✅ Tool use / JSON mode pass-through (`tools`, `tool_choice`, `json_mode` in `bridge_request`)
- ✅ SSE streaming (`POST /run/stream`) and cancellation (`DELETE /runs/<id>`) with the in-flight tracker (`core/in_flight_tracker.py`)
- ✅ `/health` reports the running version + `released`
- ✅ (2026-10-15) aios-flow adapter: identity token provider, structured errors with `error_code`/`retryable`, `wait` retry — exercised against a real aios-identity + a real enforcing aios-flow on a throwaway stack, and ON on `aios-server` (token minted, authenticated read measured)
- ✅ (2026-10-15) an unknown provider on a local node -> `UnsupportedProviderError` -> HTTP 400 (checked on the server's Python 3.12.3)
- ✅ (2026-10-15) generator `report_v2` (on `main`, not released): equal to AOKP's synthesizer on 1,054 golden cases generated from the TypeScript, 30/30 seeded defects caught; real-model answer quality unmeasured

Per CHANGELOG, **not re-verified today**: vision (image inputs), per-model timeout, per-model pricing values, OpenAI Batch API + `wait` helper (v2.3.0 / v2.5.0), evaluator wiring (v2.1.0). (aios-flow status/wait were exercised against the real aios-flow in 2.7.0.)

Known gaps / stubs (measured 2026-10-14; the later ones added 2026-10-15):
- **4 placeholder adapter dirs** (`adapters/api`, `desktop_bridge`, `local_service`, `ui_bridge`): deliberate architectural slots from the v0 skeleton; **kept by Owner decision 2026-10-14 (KD-ATP-009)**. Status table in `adapters/README.md`, guarded by `tests/unit/test_placeholder_adapters.py`. No use case or owner assigned. `adapters/contracts/` is the documented `typing.Protocol` contract layer (no non-test code imports it; not concluded dead).

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

<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=AGCP_COPILOT -->
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
