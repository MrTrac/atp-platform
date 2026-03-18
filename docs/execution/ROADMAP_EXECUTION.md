# ATP Execution Roadmap

> **Purpose:** Execution roadmap project-side để chuyển ATP từ chuỗi slice rời rạc sang hệ execution planning theo feature-program, bám đúng AI_OS canonical execution model nhưng phản ánh ATP reality.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_EXECUTION_TEMPLATE.md`
> **Project instance:** `docs/execution/ROADMAP_EXECUTION.md`

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Baseline:** `v1.0.4` on `main`
- **Execution branch:** `codex/release-v1.1-execution`
- **Owner:** ATP execution line
- **Status:** ACTIVE
- **Last updated:** 2026-03-18

## 1) Purpose
Roadmap này tồn tại để:
- chuyển ATP v1.1 line từ “slice-by-slice hardening” sang “feature-execution program”
- gom các slice đã hoàn thành thành các execution lanes có ý nghĩa
- định nghĩa thứ tự thực thi tiếp theo theo pack, có staged control, review, verify, fail-stop
- giữ ATP nằm trong bounded single-AI execution posture hiện tại

## 2) Baseline và execution context

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

### ATP posture hiện tại
- stable baseline: `v1.0.4` trên `main`
- execution line mở trên `codex/release-v1.1-execution`
- execution scope hiện tại:
  - request intake
  - deterministic normalization
  - single-AI execution package
  - reviewable bundle
  - one-shot AI-ready prompt
  - operator-facing usability hardening
- explicitly out-of-scope:
  - multi-AI orchestration
  - scheduler / queue / graph
  - daemon / background automation
  - provider abstraction
  - broad architecture rewrite

### Historical grounding (Slices 01-19)
- Slice 01-04: dựng bounded request-chain và manual single-AI handoff surface
- Slice 05-10: harden help, invocation, smoke path, canonical fixture usage
- Slice 11-19: harden discoverability, quick status, readiness, confidence, review/handoff path

## 3) Execution principles
- Execution theo **feature-program**, không theo roadmap generic.
- Mỗi feature-program được chia thành **packs** bounded, reviewable, testable.
- Mỗi pack phải có:
  - objective
  - in-scope / out-of-scope
  - verification commands
  - review evidence expected
  - fail-stop triggers
- Không chạy “all programs”.
- Không cho execution-plan artifacts override canonical authority docs.

## 4) Priority map
| Priority | Feature | Why now | Risk | Dependencies |
|---|---|---|---|---|
| P0 | F-001 Execution Traceability & Review Evidence | ATP đã usable; giá trị tiếp theo là evidence chain rõ hơn cho review/acceptance | drift sang broad evidence framework nếu làm quá tay | slices 01-19 |
| P1 | F-002 Validation & Verification Robustness | smoke/fixture path đã có; cần tăng confidence bằng verify discipline chặt hơn | overbuilding verification subsystem | F-001 partial inputs, slices 07/10/13/17 |
| P2 | F-003 Review & Manual Handoff Clarity | manual single-AI handoff là current terminal surface; cần giảm ambiguity trước khi mở capability mới | trượt sang prompt-framework breadth | slices 03/04/11/14/18/19 |
| P3 | F-004 Bounded Control & Governance Surfaces | giữ execution line governable khi packs tăng dần | viết governance quá rộng so với ATP reality | slices 01/09/13/15/16 |
| P4 | F-005 Request-Chain Operator UX Followthrough | lane này đã mạnh; chỉ nên tiếp tục nếu cần polish bounded surface thật sự có evidence | cosmetic churn | slices 02/05/06/08/12 |

## 5) Recommended execution order
1. **F-001 — Execution Traceability & Review Evidence**
2. **F-002 — Validation & Verification Robustness**
3. **F-003 — Review & Manual Handoff Clarity**
4. **F-004 — Bounded Control & Governance Surfaces**
5. **F-005 — Request-Chain Operator UX Followthrough**

## 6) Feature summaries
| ID | Title | Scope summary | Status | Owner |
|---|---|---|---|---|
| F-001 | Execution Traceability & Review Evidence | Làm rõ evidence chain từ request -> package -> bundle -> prompt để review/gate chắc hơn | READY | ATP execution line |
| F-002 | Validation & Verification Robustness | Tăng độ tin cậy của canonical verify/smoke/fixture path và invalid-case evidence | READY | ATP execution line |
| F-003 | Review & Manual Handoff Clarity | Giảm ambiguity của review-first / handoff-ready / manual single-AI terminal surface | READY | ATP execution line |
| F-004 | Bounded Control & Governance Surfaces | Giữ staged control, completion/readiness/governance surfaces rõ khi line tiếp tục mở | READY | ATP execution line |
| F-005 | Request-Chain Operator UX Followthrough | Chỉ tiếp tục polish operator surface nếu evidence cho thấy còn friction bounded | READY | ATP execution line |

## 7) Dependency graph
```text
F-001 -> F-002 -> F-003
F-001 -> F-004
F-002 -> F-005
F-003 -> F-005
```

## 8) Execution governance
- **Approval gates:** merge `main`, push `main`, tag release, broad architecture change
- **Branch discipline:** execution chỉ trên `codex/release-v1.1-execution`; `main` vẫn là stable released baseline
- **Fail-stop:** dừng nếu:
  - thiếu canonical inputs
  - authority conflict giữa AI_OS và repo-local docs
  - scope trượt sang orchestration / scheduler / automation / provider abstraction
  - verification fail

## 9) Review / verify model
Mỗi feature-program phải nêu rõ:
- direct verification commands
- unit/integration checks repo-local cần chạy
- evidence expected:
  - diff có scope sạch
  - command outputs
  - test outputs
  - risk notes
- acceptance chỉ khi verification pass và scope vẫn bounded

## 10) Mapping từ slices đã hoàn thành sang feature lanes

### Lane A — Bounded request-chain foundation
- Slice 01, 02, 03, 04

### Lane B — Operator UX / output usability
- Slice 05, 06, 08, 11, 12, 14

### Lane C — Validation / verification / fixture confidence
- Slice 07, 10, 13, 17

### Lane D — Invocation / path guidance / bounded progression
- Slice 09, 15, 16, 18, 19

Roadmap này không coi các slice trên là “future work”. Chúng là historical grounding để ATP chuyển sang feature-program execution từ điểm hiện tại.

## 11) Current next recommendation
- **Current next action:** mở execution theo `pr-cmd run 01`
- **Program:** F-001 — Execution Traceability & Review Evidence
- **Why:** ATP đã có bounded chain usable; điểm yếu tiếp theo không còn là “can run”, mà là “can prove and review clearly”
- **Preconditions:**
  - branch vẫn là `codex/release-v1.1-execution`
  - worktree sạch
  - canonical AI_OS inputs đọc đủ
- **Stop conditions:**
  - evidence lane bắt đầu đẻ ra broad reporting framework
  - yêu cầu runtime artifact placement trong repo
  - bất kỳ scope drift nào sang orchestration / automation
