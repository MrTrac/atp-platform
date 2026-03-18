# Feature Program — Validation & Verification Robustness

## 0) Identity
- **Feature ID:** F-002
- **Feature name:** Validation & Verification Robustness
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Tăng robustness của validation và canonical verification path cho ATP bounded chain, để invalid cases, canonical fixture checks, và smoke confidence có evidence rõ hơn nhưng vẫn giữ repo-local, JSON-centric, fail-fast behavior.

## 2) Why now
- **Driver:** validation path đã usable nhưng current value tiếp theo là giảm ambiguity quanh invalid cases và verify discipline.
- **Expected value:** operator tin hơn vào bounded chain vì biết invalid-path và verify-path đều được khóa chặt.
- **Risk:** nếu làm rộng sẽ drift sang verification framework.

## 3) ATP-specific context
Grounding:
- slices 07, 10, 13, 17 đã mở validation + smoke + canonical fixture line
- ATP vẫn chưa có broader integration/runtime verification outside repo-local CLI

## 4) Scope
### In-scope
- invalid-input contract hardening tiếp theo nếu còn bounded gaps
- smoke verification robustness trong giới hạn repo-local
- canonical fixture consistency checks

### Out-of-scope
- integration test framework lớn
- environment matrix / distributed runtime verification
- automation / scheduler / orchestration

## 5) Dependencies
- **Upstream features:** F-001, slices 07/10/13/17
- **Systems/components:** CLI validation path, smoke script, tests
- **External constraints:** fixture canonical phải giữ ổn định

## 6) Completion definition
- [ ] invalid and verify paths bounded hơn
- [ ] tests/verification pass
- [ ] không sinh subsystem verify mới
- [ ] không vi phạm governance

## 7) Execution strategy
Chạy theo packs nhỏ xoay quanh verify path, invalid path, và canonical fixture contract.

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | Lock canonical verify contract | smoke/help/output checks | smoke + pytest | smoke stdout |
| P2 | Tighten invalid-path evidence | invalid cases có bounded reason rõ hơn | CLI invalid runs + pytest | stderr/stdout |
| P3 | Consolidate verification confidence | canonical chain verify contract rõ hơn | smoke + unit tests | deterministic outputs |

## 9) Pack details

### Pack P1 — Canonical Verify Contract
- **Objective:** giữ canonical smoke/help/example path không drift
- **Steps:**
  1. inspect fixture/help/smoke references
  2. tighten any remaining ambiguity
- **Fail-stop triggers:** cần reorganize fixtures hoặc create new framework
- **Verification commands:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Invalid Path Evidence
- **Objective:** make invalid cases more bounded and easier to trust
- **Steps:**
  1. identify high-signal invalid cases
  2. tighten operator-facing evidence only where needed
- **Fail-stop triggers:** request-model redesign hoặc broad validator rewrite
- **Verification commands:**
  - invalid CLI runs
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Verification Confidence Consolidation
- **Objective:** chốt bounded verification confidence for current chain
- **Steps:**
  1. consolidate verify result clarity
  2. ensure tests lock the contract
- **Fail-stop triggers:** verify result starts duplicating deep payloads
- **Verification commands:**
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu scope drift sang framework/infrastructure verify line mới.

## 11) Commit/test/checkpoint discipline
- one pack = one scoped commit
- full pytest required before declaring pack complete

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
- smoke outputs
- invalid-path outputs
- tests
- scoped diff

## 14) Final feature acceptance
Feature được accept khi canonical verify path và invalid evidence path đều rõ hơn, bounded hơn, và không làm ATP trượt sang framework verify rộng.

## 15) Prompt-CMD execution block
```text
You are executing feature F-002 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and project pack truth.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Lock canonical verify contract around help, smoke, and canonical fixture guidance.

Required verification commands:
- ./atp help
- ./atp smoke-request-chain
- python3 -m pytest -q tests/unit

Expected evidence:
- stable canonical-fixture references
- stable smoke result layer
- passing tests
```
