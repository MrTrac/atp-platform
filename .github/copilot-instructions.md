<!-- AI_OS:BEGIN MANAGED BLOCK project=ATP target=COPILOT -->
AIOS7L CONTEXT
Project: ATP
GeneratedAtUTC: 20261014T155159Z

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
SHA256: 76d44dda493c2d08053000a739ca9bf380f93c25308cb65dc665a348bfc8606e
----
# AI_CURRENT_BASELINE — ATP

- **Version:** v2.6.6
- **Released:** 2026-10-14T22:42:17+07:00
- **Last synced:** 2026-10-14 (via aios sync reverse)

## Status



## Runtime modules
  (none detected)


## API endpoints
  (none detected)

## Next Step (excerpt)
File: 20_PROJECTS/ATP/AI_NEXT_STEP.md
SHA256: edcca8690c4cf9b5d66d6bbce23bd8413b4d25f8950637c575959efc05ecb4e2
----
# AI Next Step — ATP

- **Last updated:** 2026-10-14
- **Phase:** v2.6.6 — maintenance line after v2.6.0 (Doctrine v6.0 D6.2 closed via M4 scope-cut, ATP synthesis surface complete); v6.1 consumer cutover still open (backlog below)
- **Current state:** v2.6.6 (RELEASED 2026-10-14T22:42:17+07:00) = v2.6.5 + KD-ATP-013 (`core/retry.with_retry` closes each retried `HTTPError`). Where it runs and how it was verified: §1.
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

## 1. Current state (verified 2026-10-14 unless marked)

**Release.** v2.6.6 (tag `v2.6.6` -> `d0ff2e4`, RELEASED 2026-10-14T22:42:17+07:00). Running on `aios-server` from `/opt/aios/atp/current -> releases/2.6.6` since 2026-10-14T15:49:48Z (checked after the install: `/health` reports `2.6.6` + `released`, 7 routes answer 200, service active, 0 restarts; the changed function `with_retry` was run for real on the server's Python 3.12.3 with fake `HTTPError`s: dropped attempts closed, last one left open and readable).
Previous release `2.6.5` is kept on the server as the `--rollback` target; the rollback itself has **not** been exercised on the live service (KD-ATP-014). `2.6.3` was never installed.

**In 2.6.5 (since 2.6.4).** Tests + docs: KD-ATP-003 (`cli/` launch test only runs real entry points), KD-ATP-011 (README/AGENTS list the bridge routes; guard test reads
them from `bridge/bridge_server.py` with `ast`), KD-ATP-008 (`test_execute_timeout` uses the real `asyncio.wait_for` and asserts the kill). **Runtime code:** KD-ATP-012 — 14 `except` handlers in 7 modules now close the response an
`HTTPError` holds open, through `core/http_errors.close_http_error` (error-path only; low risk). Deployed with 2.6.5.

**New in 2.6.6 (since 2.6.5):** KD-ATP-013 — `core/retry.with_retry` (the only broad `except Exception` that can receive an `HTTPError` without re-raising it) now closes each retried error; the LAST one is left open on purpose (re-raised; adapters read its body). Deployed with 2.6.6. No real 429 from a provider has been pushed through the adapters on the server (needs an outbound call); the function itself was exercised there with fake errors.

**Execution stack** (read from `registry/providers/*.yaml`, `EXECUTOR_MAP`, `bridge/bridge_server.py`):
- LLM providers: **Anthropic** (default; bridge default model `claude-haiku-4-5-20251001`) and **OpenAI**. `non_llm_execution` for shell/git/build/test/lint. Bridge-level dispatchers: `tdf-run` (:4180), `aios-flow` (:7700). AOKP adapter opt-in (6 queries).
- **No local LLM.** The Ollama adapter was removed in v2.6.0; macOS hosts must not run Ollama or any local model (`Global_Mac_No_Ollama_Rule`). A provider with no handler (e.g. `ollama/...`) falls through to the deferred SSH stub and returns `status=deferred`.
- Bridge routes: 12 distinct paths / 13 method+path pairs, all listed in README and AGENTS and guarded by `tests/unit/test_bridge_routes_documented.py`.
- Synthesis generators: 8 (`generators/stubs/`). Consumer cutover still open (§D6.2 / v6.1 above).

**Deploy path.** Tag on GitHub -> a watcher publishes it to the VPS release store (it never deploys) -> `aios-deploy atp <version>` (Mac -> `sudo aios-deploy-local atp`): installs into a new `releases/<ver>` directory, swaps `current`, restarts,
requires HTTP 200 **and** the exact version in `/health`, rolls back by itself on failure. See `Global_Build_Deploy_Topology_Rule.md` §5.2c and §8.

**Tests (2.6.5).** `make test`: 680 unit + 22 integration passed (7 skipped). Bare `python3 -m pytest` (no `PYTHONPATH`): 702 passed, 0 failed. 0 warnings, including with `ResourceWarning` and `RuntimeWarning` promoted to errors. CI green on 3.11 and 3.12.

---

## 2. Architectural status: MATURE, with the gaps listed below

Verified in code on 2026-10-14:
- ✅ Anthropic + OpenAI handlers in `EXECUTOR_MAP`
- ✅ Retry/backoff (`core/retry.py`), pricing table (`core/pricing.py`), typed error codes (7, `core/error_codes.py`)
- ✅ Tool use / JSON mode pass-through (`tools`, `tool_choice`, `json_mode` in `bridge_request`)
- ✅ SSE streaming (`POST /run/stream`) and cancellation (`DELETE /runs/<id>`) with the in-flight tracker (`core/in_flight_tracker.py`)
- ✅ `/health` reports the running version + `released`

Per CHANGELOG, **not re-verified today**: vision (image inputs), per-model timeout, per-model pricing values, OpenAI Batch API + `wait` helper (v2.3.0 / v2.5.0), aios-flow status/wait (v2.4.0), evaluator wiring (v2.1.0).

Known gaps / stubs (measured 2026-10-14):
- **4 placeholder adapter dirs**: `adapters/api`, `desktop_bridge`, `local_service`, `ui_bridge` — only a README and `__init__.py`, imported by nothing. Plus `adapters/contracts/` (4 files, 138 lines) which no non-test code imports (not examined further).
- **SSH remote execution** (`adapters/ssh_remote/ssh_exec_adapter.py`, 49 lines): a stub that never executes anything and returns `status=deferred`. It is also where requests for an unknown provider end up.
- ~~Resource leak~~ **fixed on `main` (KD-ATP-012, unreleased):** `HTTPError` responses are now closed by every handler that can receive one; guarded by a static `ast` check + a behaviour test per call site (`tests/unit/test_http_errors_closed.py`). Broad handlers audited with `ast` (KD-ATP-013): the only one that could receive an open `HTTPError` was `core/retry.with_retry`, now closed too.

---

## 3. Possible next steps (all require human approval)

1. **v6.1 synthesis cutover** (KD-ATP-006) — see the backlog above; needs a dedicated 6-10h session and Owner scheduling.
2. **Placeholder adapters** (KD-ATP-009) — decide: delete the 4 empty dirs and `adapters/contracts`, or give them an owner and a use case. Evidence above.

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
