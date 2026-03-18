# Feature Program — Control-plane Command Hardening

## 0) Identity
- **Feature ID:** F-104
- **Feature name:** Control-plane Command Hardening
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Harden command surfaces liên quan control-plane của ATP để phase execution expansion và integration-prep có entrypoints, help, validation, và boundaries rõ hơn, nhưng không biến control-plane thành automation layer hay broad orchestration framework.

## 2) Why now
- **Driver:** v1.2 sẽ đụng gần hơn tới integration surfaces; control-plane commands phải rõ boundary trước khi thêm readiness surfaces.
- **Expected value:** operator hiểu command nào dành cho execution line, command nào chỉ là control-plane preparation, và command nào chưa được phép.
- **Risk:** trượt sang broad control-plane rewrite hoặc hidden behavior changes.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện có `run`, `inspect`, `validate`, và bounded request-chain commands
- v1.1 đã harden help/control cues, nhưng chưa mở rộng control-plane command posture cho phase mới
- human-gated control phải giữ nguyên

## 4) Scope
### In-scope
- help/guidance/validation cho control-plane command surfaces
- clearer bounded command contracts
- repo-root operator path refinement khi trực tiếp liên quan control-plane

### Non-goals
- rewrite control-plane architecture
- thêm automation hoặc background behavior
- execution engine mới
- request semantics redesign

## 5) Dependencies
- **Upstream features:** F-101 hoặc F-102 để biết control-plane cần cover gì
- **Systems/components:** `./atp`, help text, control-plane command files
- **External constraints:** phải giữ repo-local CLI model và human-gated control

## 6) Completion definition
- [ ] control-plane command boundaries rõ hơn
- [ ] operator không bị nhầm execution surfaces với broader system actions
- [ ] help/validation contracts pass
- [ ] không có hidden behavior expansion

## 7) Execution strategy
- P1: identify one control-plane ambiguity cần harden
- P2: apply bounded command/help/validation fix
- P3: confirm no hidden expansion và no drift khỏi repo-local CLI model

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | capture command ambiguity | identify 1 bounded control-plane confusion point | reproduce + pytest | command evidence |
| P2 | harden command contract | help/usage/validation/surface fix | direct commands + pytest | diff + outputs |
| P3 | confirm no expansion drift | ensure repo-local human-gated model unchanged | help + smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Command Ambiguity Capture
- **Objective:** xác định một ambiguity thực sự giữa control-plane commands và execution commands.
- **In-scope:** help output, error messaging, command contract mismatch.
- **Non-goals:** broad cleanup toàn bộ CLI.
- **Fail-stop conditions:**
  - không chứng minh được ambiguity cụ thể
  - ambiguity thực chất thuộc feature khác
  - verification fail
- **Verification strategy:**
  - reproduce command ambiguity
  - `./atp help`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Command Contract Hardening
- **Objective:** sửa ambiguity bằng command-surface hardening tối thiểu.
- **In-scope:** help, usage, validation, bounded guidance.
- **Non-goals:** functional expansion của control-plane.
- **Fail-stop conditions:**
  - change tạo hidden behavior mới
  - help contract đụng nhiều unrelated surfaces
  - verification fail
- **Verification strategy:**
  - relevant control-plane commands
  - `./atp help`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Repo-local Control Confirmation
- **Objective:** xác nhận command hardening không làm ATP rời repo-local, human-gated posture.
- **In-scope:** regression confirmation, control boundary cues.
- **Non-goals:** integration implementation.
- **Fail-stop conditions:**
  - command surface imply automation
  - repo-root operator path bị mơ hồ hơn
  - verification fail
- **Verification strategy:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- control-plane command hardening biến thành command expansion ngoài feature
- implied automation / background behavior xuất hiện
- repo-local CLI model không còn rõ
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 ambiguity = 1 pack commit
- commit phải giải thích rõ ambiguity nào được sửa
- giữ worktree sạch giữa packs

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
- reproduced ambiguity
- bounded command/help diff
- regression outputs
- note vì sao fix không mở control-plane architecture

## 14) Final feature acceptance
Feature được accept khi control-plane command surfaces của ATP rõ hơn, an toàn hơn, và không imply broader execution powers.

## 15) Prompt-CMD execution block
```text
You are executing feature F-104 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Capture one concrete control-plane command ambiguity that matters in the v1.2 expansion phase.

Required verification commands:
- reproduce the ambiguity with repo-root command surfaces
- ./atp help
- python3 -m pytest -q tests/unit

Expected evidence:
- one concrete command-surface confusion point
- bounded fix candidate
- no architecture expansion implied
```
