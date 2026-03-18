# ATP Prompt-CMD Program Index

> **Purpose:** Index cho feature-execution programs của ATP và cách dùng `pr-cmd` trên project instance.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PROMPT_CMD_INDEX_TEMPLATE.md`
> **Roadmap:** `docs/execution/ROADMAP_EXECUTION.md`

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Last updated:** 2026-03-18

## 1) Purpose
Thư mục `PROMPT_CMD/` dùng để:
- chia ATP execution line thành feature-execution programs có staged control
- chuẩn hoá cách sinh execution prompt theo `pr-cmd run <id>`
- giữ next action rõ, bounded, và audit-friendly

## 2) Usage
- `pr-cmd roadmap`
  - dùng để tạo / refresh execution-plan layer của ATP
- `pr-cmd n`
  - dùng khi cần generate thêm feature-program files mới cho ATP
- `pr-cmd run <id>`
  - dùng để sinh execution prompt cho **pack tiếp theo** của feature `<id>`

**Rule:** `pr-cmd` là planning / execution-control mechanism. Nó không auto-run toàn bộ roadmap.

## 3) Recommended execution order
1. **01** — Execution Traceability & Review Evidence
2. **02** — Validation & Verification Robustness
3. **03** — Review & Manual Handoff Clarity
4. **04** — Bounded Control & Governance Surfaces
5. **05** — Request-Chain Operator UX Followthrough

## 4) Program summaries
| ID | File | Title | Status | Why now |
|---|---|---|---|---|
| 01 | `PROMPT_CMD/01_execution_traceability_and_review_evidence.md` | Execution Traceability & Review Evidence | READY | ATP cần evidence chain rõ hơn để review/gate v1.1 line |
| 02 | `PROMPT_CMD/02_validation_and_verification_robustness.md` | Validation & Verification Robustness | READY | canonical fixture/smoke path đã có, cần harden validation confidence |
| 03 | `PROMPT_CMD/03_review_and_manual_handoff_clarity.md` | Review & Manual Handoff Clarity | READY | manual single-AI handoff đã tồn tại nhưng còn cần giảm ambiguity |
| 04 | `PROMPT_CMD/04_bounded_control_and_governance_surfaces.md` | Bounded Control & Governance Surfaces | READY | execution line dài hơn cần staged control rõ hơn mà không mở architecture |
| 05 | `PROMPT_CMD/05_request_chain_operator_ux_followthrough.md` | Request-Chain Operator UX Followthrough | READY | chỉ tiếp tục polish bounded operator surface khi có evidence cụ thể |

## 5) Execution rules
- Chỉ run **1 feature-program tại một thời điểm**.
- Mỗi run phải:
  - xác nhận branch và worktree
  - đọc AI_OS canonical inputs
  - bám đúng pack hiện tại
  - chạy verification commands
  - dừng tại fail-stop triggers
- Không được dùng `PROMPT_CMD/*.md` để bypass authority docs.

## 6) Current next action
- **Current program:** `01`
- **Next step:** `pr-cmd run 01`
- **Preconditions:**
  - branch `codex/release-v1.1-execution`
  - worktree sạch
  - đọc `AI_PROJECT_CONTEXT.md`, `AI_CURRENT_BASELINE.md`, `AI_NEXT_STEP.md`, `AI_HANDOFF_LATEST.md`
- **Verification baseline:**
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`
