# ATP Prompt-CMD Program Index v1.2

> **Purpose:** Index cho feature-execution programs của ATP trong roadmap generation v1.2.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PROMPT_CMD_INDEX_TEMPLATE.md`
> **Roadmap:** `docs/execution/v1_2/ROADMAP_EXECUTION.md`
> **Relationship với v1.1:** `docs/execution/PROMPT_CMD/` là completed baseline của generation v1.1 và không bị sửa trong index này.

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Roadmap generation:** `v1.2`
- **Last updated:** 2026-03-18

## 1) Purpose
Thư mục `docs/execution/v1_2/PROMPT_CMD/` dùng để:
- chia ATP phase mới thành 5 feature-execution programs bounded
- chuẩn hóa cách sinh execution prompt theo `pr-cmd run <id>`
- giữ chuyển pha từ v1.1 hardening sang v1.2 expansion/integration-prep ở trạng thái governable

## 2) Usage
- `pr-cmd roadmap`
  - dùng khi cần rerun execution roadmap theo canonical rerun governance
- `pr-cmd n`
  - dùng khi cần generate thêm feature-program files cho generation hiện tại
- `pr-cmd run <id>`
  - dùng để sinh execution prompt cho **pack tiếp theo** của feature `<id>` trong roadmap `v1_2`

**Rule:** v1.2 roadmap là generation mới, nhưng execution vẫn staged. Không implied auto-run toàn bộ 5 features.

## 3) Recommended execution order
1. **01** — Multi-request Execution Surface
2. **02** — Execution Session Tracking (Repo-local)
3. **03** — Operator Readability Layer (Non-breaking)
4. **04** — Control-plane Command Hardening
5. **05** — Integration Readiness Surface

## 4) Program summaries
| ID | File | Title | Status | Why now |
|---|---|---|---|---|
| 01 | `PROMPT_CMD/01_multi_request_execution_surface.md` | Multi-request Execution Surface | READY | mở capability đầu vào có bounded value cao nhất sau v1.1 complete baseline |
| 02 | `PROMPT_CMD/02_execution_session_tracking_repo_local.md` | Execution Session Tracking (Repo-local) | READY | cần session continuity để expansion vẫn traceable và reviewable |
| 03 | `PROMPT_CMD/03_operator_readability_layer_non_breaking.md` | Operator Readability Layer (Non-breaking) | READY | outputs sẽ dày hơn khi capability mở rộng; cần readability mà không phá contract |
| 04 | `PROMPT_CMD/04_control_plane_command_hardening.md` | Control-plane Command Hardening | READY | control-plane integration surfaces cần help/command boundaries rõ trước khi mở integration readiness |
| 05 | `PROMPT_CMD/05_integration_readiness_surface.md` | Integration Readiness Surface | READY | cần surface rõ để nói ATP sẵn sàng tích hợp tới đâu mà chưa kích hoạt broad integration |

## 5) Execution rules
- Chỉ run **1 feature program tại một thời điểm**.
- Mỗi feature có đúng **3 pack: P1 / P2 / P3**.
- Mỗi run phải:
  - xác nhận branch / worktree / canonical inputs
  - giữ JSON contract backward-compatible
  - chạy verification commands của đúng feature file
  - dừng tại fail-stop triggers
- Không được dùng v1.2 feature files để bypass authority docs hoặc mở broader architecture.

## 6) Current next action
- **Current program:** `01`
- **Next step:** `pr-cmd run 01`
- **Preconditions:**
  - branch `codex/release-v1.1-execution`
  - worktree sạch
  - v1.1 request-chain hiện hành vẫn pass trên `./atp smoke-request-chain`
  - canonical inputs AI_OS đã được đọc
- **Verification baseline:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`
