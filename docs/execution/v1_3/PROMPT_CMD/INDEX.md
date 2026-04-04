# ATP Prompt-CMD Program Index v1.3

> **Purpose:** Index cho feature-execution programs của ATP trong roadmap generation v1.3.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PROMPT_CMD_INDEX_TEMPLATE.md`
> **Roadmap:** `docs/execution/v1_3/ROADMAP_EXECUTION.md`
> **Relationship với v1.1:** `docs/execution/PROMPT_CMD/` là completed baseline của generation v1.1 và không bị sửa trong index này.
> **Relationship với v1.2:** `docs/execution/v1_2/PROMPT_CMD/` là completed baseline của generation v1.2 và không bị sửa trong index này.

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Roadmap generation:** `v1.3`
- **Last updated:** 2026-03-19

## 1) Purpose
Thư mục `docs/execution/v1_3/PROMPT_CMD/` dùng để:
- chia ATP phase mới thành 5 feature-execution programs bounded
- chuẩn hóa cách sinh execution prompt theo `pr-cmd run <id>`
- giữ chuyển pha từ v1.2 expansion/integration-readiness sang v1.3 externalization/integration-preparation ở trạng thái governable

## 2) Usage
- `pr-cmd roadmap`
  - dùng khi cần rerun execution roadmap theo canonical rerun governance
- `pr-cmd n`
  - dùng khi cần generate thêm feature-program files cho generation hiện tại
- `pr-cmd run <id>`
  - dùng để sinh execution prompt cho **pack tiếp theo** của feature `<id>` trong roadmap `v1_3`

**Rule:** v1.3 roadmap là generation mới, nhưng execution vẫn staged. Không implied auto-run toàn bộ 5 features.

## 3) Recommended execution order
1. **01** — Execution Artifact Export Surface
2. **02** — Structured CLI Composition Surface
3. **03** — Session-to-Artifact Continuity Surface
4. **04** — Integration Contract Projection
5. **05** — Deployability Readiness Assessment

## 4) Program summaries
| ID | File | Title | Status | Why now |
|---|---|---|---|---|
| 01 | `PROMPT_CMD/01_execution_artifact_export.md` | Execution Artifact Export Surface | READY | ATP output hiện chỉ là stdout JSON; externalization bắt đầu từ opt-in artifact export ra workspace path |
| 02 | `PROMPT_CMD/02_structured_cli_composition.md` | Structured CLI Composition Surface | READY | operator phải run 3 lệnh riêng lẻ; bounded sequential composition trong 1 human-initiated invocation có giá trị cao |
| 03 | `PROMPT_CMD/03_session_artifact_continuity.md` | Session-to-Artifact Continuity Surface | READY | session tracking thiếu link tới artifacts đã tạo; continuity anchors cần trước khi expose ra ngoài |
| 04 | `PROMPT_CMD/04_integration_contract_projection.md` | Integration Contract Projection | READY | cần machine-readable contract mô tả ATP invocation surface cho external callers sau khi export và continuity rõ |
| 05 | `PROMPT_CMD/05_deployability_readiness.md` | Deployability Readiness Assessment | READY | surface rõ ATP cần gì để chạy ở môi trường mới; planning adoption mà không thực hiện deploy |

## 5) Execution rules
- Chỉ run **1 feature program tại một thời điểm**.
- Mỗi feature có đúng **3 pack: P1 / P2 / P3**.
- Mỗi run phải:
  - xác nhận branch / worktree / canonical inputs
  - giữ JSON contract backward-compatible với v1.1 và v1.2
  - chạy verification commands của đúng feature file
  - dừng tại fail-stop triggers
- Không được dùng v1.3 feature files để bypass authority docs hoặc mở broader architecture.
- Artifact export phải opt-in và không thay đổi stdout behavior mặc định.
- Composition phải synchronous, human-initiated, fail-stop — không phải automated pipeline.

## 6) Current next action
- **Current program:** `01`
- **Next step:** `pr-cmd run 01`
- **Preconditions:**
  - branch `codex/release-v1.1-execution`
  - worktree sạch
  - v1.1 và v1.2 request-chain surfaces vẫn pass trên `./atp smoke-request-chain`
  - canonical inputs AI_OS đã được đọc
- **Verification baseline:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`
