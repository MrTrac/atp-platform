# Feature Program — Request-Chain Operator UX Followthrough

## 0) Identity
- **Feature ID:** F-005
- **Feature name:** Request-Chain Operator UX Followthrough
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Giữ lane operator UX của ATP ở trạng thái bounded, high-signal, low-friction, nhưng chỉ tiếp tục khi có evidence thật sự về friction còn lại. Đây không phải lane để “polish vô hạn”, mà là lane để xử lý bounded operator pain points có thể verify được.

## 2) Why now
- **Driver:** operator UX lane đã mạnh sau Slice 05-19, nhưng vẫn cần một execution program riêng để absorb future bounded friction một cách governable.
- **Expected value:** tránh quay lại ad hoc slices rời rạc mỗi khi có một pain point nhỏ.
- **Risk:** cosmetic churn hoặc over-polish không tạo value.

## 3) ATP-specific context
Grounding:
- slices 05, 06, 08, 10, 11, 12, 14, 19 đã tạo operator UX surface tốt
- ATP vẫn chạy repo-local, CLI-first, JSON-first

## 4) Scope
### In-scope
- bounded UX friction fixes có evidence
- help / invocation / output clarity polish nhỏ
- canonical operator path improvements nếu thật sự cần

### Out-of-scope
- cosmetic cleanup không có operator value
- alternate renderer / TUI
- workflow engine

## 5) Dependencies
- **Upstream features:** F-001 đến F-004
- **Systems/components:** root help, smoke path, request-chain output contract
- **External constraints:** giữ repo-local CLI model

## 6) Completion definition
- [ ] friction được chứng minh và xử lý bounded
- [ ] tests/verification pass
- [ ] không có churn cosmetic vô ích
- [ ] semantics không đổi

## 7) Execution strategy
Feature này chỉ nên run khi có evidence cụ thể từ operator/reviewer. Không ưu tiên trước F-001 đến F-004.

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | Capture bounded friction | identify 1 concrete operator pain point | reproduce + tests | command output |
| P2 | Apply minimum UX hardening | fix one bounded issue | direct commands + pytest | diff + outputs |
| P3 | Confirm no churn drift | ensure gain is real and bounded | full verify | tests + review note |

## 9) Pack details

### Pack P1 — Capture Friction
- **Objective:** chỉ proceed nếu pain point cụ thể được chứng minh
- **Verification commands:**
  - reproduce command
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Minimum Hardening
- **Objective:** sửa đúng pain point đó, không hơn
- **Verification commands:**
  - relevant direct commands
  - `python3 -m pytest -q tests/unit`

### Pack P3 — No-Drift Confirmation
- **Objective:** confirm không có over-polish / noise
- **Verification commands:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- không có friction evidence cụ thể
- solution chỉ là cosmetic churn
- change bắt đầu đụng semantics hoặc architecture

## 11) Commit/test/checkpoint discipline
- one bounded pain point = one pack commit
- no batch UX cleanup

## 12) Verification commands
```bash
./atp help
./atp smoke-request-chain
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- reproduced friction
- bounded diff
- passing tests
- note why fix mattered

## 14) Final feature acceptance
Feature được accept khi ATP có quy trình followthrough cho operator UX mà vẫn tránh được cosmetic-churn lane.

## 15) Prompt-CMD execution block
```text
You are executing feature F-005 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and project pack truth.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Identify one concrete bounded operator friction point worth fixing.

Required verification commands:
- reproduce the friction with direct repo-root commands
- python3 -m pytest -q tests/unit

Expected evidence:
- concrete friction reproduction
- reason this is not cosmetic churn
- bounded next pack candidate
```
