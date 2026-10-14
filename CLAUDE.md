<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=CLAUDE -->
AIOS7L CONTEXT
Project: ATP
GeneratedAtUTC: 20261014T141747Z

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
SHA256: 82600697cb86ac2518a15308faecf0d14dd4d6c3f0425e94d3343e9491e03ad4
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.6.4
- **Released:** 2026-10-14T21:05:12+07:00
- **Last synced:** 2026-10-14 (via aios sync reverse)

## Status



## Runtime modules
  (none detected)


## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: e342d551d8fb769cd1c992c3c96e69162cd362c0cbd048e1a0680bdea86737cf
----
# AI Next Step — ATP

- **Last updated:** 2026-10-14
- **Phase:** v2.6.4 — maintenance line after v2.6.0 (Doctrine v6.0 D6.2 closed via M4 scope-cut, ATP synthesis surface complete); v6.1 consumer cutover still open (backlog below)
- **Current state:** v2.6.4 (RELEASED 2026-10-14T21:05:12+07:00). 2.6.4 `generators/llm.py` default model no longer `ollama/qwen3:8b` (empty = bridge default, anthropic); 2.6.1 `/health` reports the real version; 2.6.2 `cli/` stdlib-shadow fix + CI matrix 3.11/3.12 + `jinja2` as optional extra `adapters`; 2.6.3 `write_exchange_bundle` writes to `_shared/exchange/current-task/` like the run writer. Last verified on 2.6.4: `make test` 661 unit passed + 22 integration passed (7 skipped). Known open: bare `python3 -m pytest` fails `test_cli_scripts_start_on_this_interpreter` (`cli/output_contract.py` imports `core` without a `sys.path` shim; passes under `make test` because the Makefile exports `PYTHONPATH=.`). v2.6.0 baseline facts: 8/8 generators functional, 81/81 generator tests pass; AOKP-side cutover deferred to v6.1 per M4 fallback (ATP runbook §3 mid-step gate).

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

AIOS7L HANDOFF
Project: ATP
File: 20_PROJECTS/ATP/AI_HANDOFF_LATEST.md
SHA256: 7a3b21d0aed32e472c12499ae84dc4fb2ed2825238550fe4c37631cde5f37579
----
# AI_HANDOFF_LATEST — ATP

## Handoff: v2.6.4 — reverse sync from source repo
**Date**: 2026-10-14
**Release report (G-RELREPORT-1)**: ledger `~/AI_OS/20_PROJECTS/ATP/AI_ISSUE_LEDGER.yaml` · user report `~/AI_Shared_Outputs/AIOS_Ecosystem/ATP/bao-cao-phat-hanh/Bao_Cao_Phat_Hanh_ATP_2.6.4.{md,html,pdf,docx,pptx}`
**Open at release**: KD-ATP-007 (2.6.3 + 2.6.4 NOT deployed; aios-server runs 2.6.2) · KD-ATP-004 partial (fixed locally, NOT pushed: see `git log origin/main..HEAD` in ATP and AI_OS) · KD-ATP-011 (README/AGENTS '12 endpoints') · KD-ATP-003/005/006/008/009

### What changed in v2.6.4
## [2.6.4] — 2026-10-14

### Fixed — `generators/llm.py` defaulted to the removed Ollama provider, so every real-mode call without an explicit model failed

`DEFAULT_MODEL` was `ollama/qwen3:8b`. `bridge_request` parsed it as provider `ollama`; the executor has had no handler for that provider since 2.6.0 removed the Ollama adapter, so the call
fell through to the deferred SSH stub (`status=deferred`, empty `stdout`) and `generators.llm` raised `LlmError`. Measured 2026-10-14 by calling `invoke_executor` directly: no network,
nothing launched. The default is now empty, so `bridge_request` applies the bridge's own default (anthropic, `claude-haiku-4-5-20251001`) — one source instead of a copy that can drift
(the sonnet-4 id that went 404 in 2.6.0 is the precedent). `ATP_GENERATORS_DEFAULT_MODEL` still overrides. The `report` generator's `model` parameter example no longer suggests an Ollama model.

macOS hosts must not run Ollama or any local LLM (`Global_Mac_No_Ollama_Rule`). Nothing in ATP can start one since 2.6.0; a read-only probe of the Mac on 2026-10-14 found no Ollama process,
no listener on 11434, no `ollama` binary or app. Guarded by `tests/unit/test_generators_llm_default.py` (3 tests; all 3 fail against the old default). Not exercised against the real Anthropic
API in this release: that needs a key and an outward call.

### Changed — `README.md` and `AGENTS.md` baseline lines now say v2.6.4

Đầy đủ / full history: `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP/CHANGELOG.md`

---



> ⏷ Lịch sử handoff đầy đủ KHÔNG nội tuyến (chống bloat context).
> On-demand: MCP get_last_handoff(project=ATP) hoặc đọc pack AI_HANDOFF_LATEST.md + AI_HANDOFF_ARCHIVE.md.
<!-- AI_OS:END MANAGED BLOCK -->

<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=AGCP_CLAUDE -->
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
