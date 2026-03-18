# ATP Execution Roadmap v1.2

> **Purpose:** Execution roadmap generation mới cho ATP sau khi roadmap v1.1 đã complete, chuyển phase từ execution hardening sang execution expansion & control-plane integration theo bounded execution model.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_EXECUTION_TEMPLATE.md`
> **Canonical rerun governance:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_RERUN_GOVERNANCE.md`
> **Project instance:** `docs/execution/v1_2/ROADMAP_EXECUTION.md`
> **Relationship với v1.1:** `docs/execution/ROADMAP_EXECUTION.md` là completed baseline roadmap của phase v1.1 và không bị sửa đổi trong generation này.

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Baseline:** `v1.0.4` on `main`
- **Execution branch:** `codex/release-v1.1-execution`
- **Owner:** ATP execution line
- **Generation:** `v1.2`
- **Status:** ACTIVE
- **Last updated:** 2026-03-18

## 1) Purpose
Roadmap v1.2 tồn tại để:
- mở execution capability theo bounded expansion thay vì chỉ hardening operator surface
- chuẩn bị integration surfaces cho control-plane mà không phá JSON contracts hiện có
- giữ ATP ở repo-local, human-gated, bounded single-AI execution posture
- chuyển ATP từ “execution line usable và hardened” sang “execution line có thể mở rộng có kiểm soát”

## 2) Vì sao đây là generation mới
Theo `ROADMAP_RERUN_GOVERNANCE.md`, lần tạo roadmap này thuộc:
- **Case C — Phase transition lớn**
- **Case D — Roadmap exhaustion / roadmap completion**

### Điều được giữ nguyên
- v1.1 roadmap cũ dưới `docs/execution/` vẫn là completed baseline
- JSON-only output surfaces của request-chain
- bounded execution model
- human-gated control
- manual single-AI handoff là terminal surface hiện tại

### Điều thay đổi trong v1.2
- trọng tâm chuyển sang execution expansion & control-plane integration
- feature map mới không lặp lại hardening lanes đã complete ở v1.1
- feature programs mới tập trung vào multi-request surface, session tracking, readability layer, control-plane command hardening, integration readiness

## 3) Baseline và invariants

### Canonical truth inputs phải đọc cùng
- AI_OS project pack:
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_CURRENT_BASELINE.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_NEXT_STEP.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_HANDOFF_LATEST.md`
- Repo-local authority:
  - `README.md`
  - `docs/architecture/overview.md`
  - `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
  - `docs/design/request_model.md`
  - `docs/design/handoff_model.md`
  - `docs/execution/ROADMAP_EXECUTION.md` như completed baseline v1.1

### v1.1 completed baseline
- Slices 01-19 đã harden bounded single-AI request-chain
- Feature programs F-001 đến F-005 của roadmap v1.1 đã complete
- Repo-root launcher canonical là `./atp`
- Canonical fixture là `tests/fixtures/requests/sample_request_slice02.yaml`

### Invariants bắt buộc giữ ở v1.2
- không phá JSON contracts đã có
- không đổi request/bundle/prompt semantics
- không mở multi-AI orchestration
- không thêm scheduler / queue / graph / daemon / background automation
- không thêm provider abstraction
- không phá repo-local CLI model
- không bỏ human-gated control

## 4) Execution principles
- v1.2 vẫn chạy theo **feature-execution program** và **packs bounded**
- mỗi feature phải có đúng **3 pack: P1 / P2 / P3**
- mỗi pack phải reviewable, testable, fail-stop
- mở capability chỉ theo bounded surface, không by-pass v1.1 contracts
- integration readiness là preparation surface, không phải activation của broad integration engine

## 5) Priority map
| Priority | Feature | Why now | Risk | Dependencies |
|---|---|---|---|---|
| P0 | F-101 Multi-request Execution Surface | ATP hiện chỉ rõ single-request path; bước mở rộng hữu ích nhất là bounded multi-request entry surface | drift sang orchestration hoặc batch engine | v1.1 complete baseline |
| P1 | F-102 Execution Session Tracking (Repo-local) | mở capability cần session trace repo-local để review và continuity rõ hơn | trượt sang runtime state system quá rộng | F-101 partial outputs, v1.1 traceability surfaces |
| P2 | F-103 Operator Readability Layer (Non-breaking) | execution mở rộng sẽ làm JSON dày hơn; cần readability layer không phá contract | accidental alternate renderer hoặc payload duplication | F-101, F-102 |
| P3 | F-104 Control-plane Command Hardening | khi control-plane integration surfaces xuất hiện, command boundaries phải rõ hơn | broad control-plane rewrite | v1.1 control surfaces, F-101/F-102 |
| P4 | F-105 Integration Readiness Surface | cần surface rõ để nói ATP đã sẵn sàng tích hợp tới đâu mà chưa activate integration | trượt sang integration implementation | F-102, F-104 |

## 6) Recommended execution order
1. **F-101 — Multi-request Execution Surface**
2. **F-102 — Execution Session Tracking (Repo-local)**
3. **F-103 — Operator Readability Layer (Non-breaking)**
4. **F-104 — Control-plane Command Hardening**
5. **F-105 — Integration Readiness Surface**

## 7) Feature summaries
| ID | Title | Scope summary | Status | Owner |
|---|---|---|---|---|
| F-101 | Multi-request Execution Surface | thêm bounded multi-request entry/summary surface mà không mở orchestration | READY | ATP execution line |
| F-102 | Execution Session Tracking (Repo-local) | thêm repo-local session tracking surface cho traceability và review continuity | READY | ATP execution line |
| F-103 | Operator Readability Layer (Non-breaking) | thêm readability surfaces không phá JSON contract hiện có | READY | ATP execution line |
| F-104 | Control-plane Command Hardening | harden control-plane CLI boundaries và help/contracts cho phase mở rộng | READY | ATP execution line |
| F-105 | Integration Readiness Surface | surfacing mức readiness và boundaries cho integration tiếp theo | READY | ATP execution line |

## 8) Dependency graph
```text
F-101 -> F-102 -> F-103
F-101 -> F-104
F-102 -> F-105
F-104 -> F-105
```

## 9) Execution governance
- **Approval gates:** merge `main`, push `main`, tag release, architecture rewrite, broad integration activation
- **Branch discipline:** execution chỉ trên `codex/release-v1.1-execution`; `main` vẫn là stable released baseline `v1.0.4`
- **Generation discipline:** v1.1 roadmap được frozen như completed baseline; v1.2 là generation mới, không phải in-place rewrite
- **Fail-stop:** dừng nếu:
  - scope drift sang orchestration / scheduler / automation / provider abstraction
  - bất kỳ thay đổi nào phá JSON contract hiện có
  - multi-request surface bắt đầu imply async engine hoặc batch automation
  - verification fail

## 10) Review / verify model
Mỗi feature program phải định nghĩa:
- direct verification commands
- unit tests / smoke checks cần chạy
- expected evidence:
  - bounded diff
  - command outputs
  - test outputs
  - risk note nói rõ vì sao chưa mở broader architecture
- acceptance chỉ khi capability mới vẫn non-breaking với v1.1 contracts

## 11) Mapping từ v1.1 sang v1.2

### v1.1 retained as completed baseline
- request-chain foundation
- operator usability hardening
- validation / smoke confidence
- review / handoff clarity
- bounded control surfaces

### v1.2 new focus lanes
- bounded execution expansion
- repo-local session continuity
- non-breaking readability over denser outputs
- control-plane integration preparation
- integration readiness signaling

## 12) Current next recommendation
- **Current next action:** `pr-cmd run 01`
- **Program:** F-101 — Multi-request Execution Surface
- **Why:** đây là bước mở rộng capability có giá trị cao nhất sau khi v1.1 hardening đã complete, đồng thời tạo nền cho session tracking và integration readiness mà vẫn bounded
- **Preconditions:**
  - branch vẫn là `codex/release-v1.1-execution`
  - worktree sạch
  - v1.1 baseline surfaces vẫn pass trên canonical fixture
  - đọc đủ canonical AI_OS inputs
- **Stop conditions:**
  - multi-request scope bắt đầu imply routing, scheduling, queueing, background execution
  - bất kỳ output change nào phá JSON contract của single-request path
