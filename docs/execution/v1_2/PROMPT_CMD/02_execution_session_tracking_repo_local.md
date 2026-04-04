# Feature Program — Execution Session Tracking (Repo-local)

## 0) Identity
- **Feature ID:** F-102
- **Feature name:** Execution Session Tracking (Repo-local)
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Thêm session tracking repo-local cho execution line của ATP để operator có thể thấy continuity của một execution session theo bounded, deterministic, human-gated way, nhưng không tạo runtime state subsystem rộng, background service, hay persistent coordination engine.

## 2) Why now
- **Driver:** khi ATP mở multi-request surface hoặc control-plane integration surface, session continuity sẽ quan trọng hơn chỉ run từng command rời.
- **Expected value:** tăng traceability, review continuity, và khả năng resume/audit repo-local.
- **Risk:** dễ trượt sang run manager hoặc runtime state system quá rộng.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- v1.1 đã có run_id và traceability surfaces ở level command output
- ATP repo boundary cấm đặt runtime artifacts lung tung trong repo
- session tracking ở đây phải là repo-local control surface, không phải background runtime manager

## 4) Scope
### In-scope
- repo-local session identity / session summary surface
- deterministic mapping giữa session và request-chain outputs
- bounded operator visibility cho current execution session

### Non-goals
- background session daemon
- execution database / telemetry system
- distributed coordination
- thay đổi semantics của request/bundle/prompt artifacts

## 5) Dependencies
- **Upstream features:** F-101 hoặc equivalent execution-surface expansion evidence
- **Systems/components:** output contract, CLI surfaces, traceability surfaces
- **External constraints:** không lưu runtime artifacts trong repo root; không mở automation

## 6) Completion definition
- [ ] session tracking repo-local surface xuất hiện bounded
- [ ] operator có thể thấy session continuity rõ hơn
- [ ] single-request outputs vẫn giữ compatibility
- [ ] verification pass

## 7) Execution strategy
- P1: define bounded session identity surface
- P2: harden session visibility / validation / review cues
- P3: confirm no drift thành runtime state subsystem

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define session identity | session id / session summary surface | direct command + pytest | output evidence |
| P2 | harden session visibility | validation/help/review around session surface | direct commands + pytest | diff + tests |
| P3 | confirm bounded repo-local posture | no daemon / no runtime-state drift | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Session Identity
- **Objective:** thêm session identity surface tối thiểu, deterministic.
- **In-scope:** session id, session summary, mapping tới run/request outputs.
- **Non-goals:** persistence engine, event log framework.
- **Fail-stop conditions:**
  - session design bắt đầu đòi DB/daemon/background writer
  - runtime artifact placement đòi mở repo-local policy
  - verification fail
- **Verification strategy:**
  - relevant session-aware command
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Session Visibility Hardening
- **Objective:** làm rõ session continuity cho operator review.
- **In-scope:** compact status/readability/help around session surface.
- **Non-goals:** dashboards, telemetry, monitoring.
- **Fail-stop conditions:**
  - session UI bắt đầu thành broad status framework
  - JSON contracts bị phá
  - verification fail
- **Verification strategy:**
  - direct commands for session surface
  - `./atp help`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Bounded Posture Confirmation
- **Objective:** chốt rằng session tracking vẫn repo-local và human-gated.
- **In-scope:** regression and governance confirmation.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - needs background behavior
  - integration with external state store implied
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - session-aware command regression
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- session tracking đòi persistent runtime manager
- scope drift sang automation / daemon / telemetry subsystem
- repo artifact discipline bị phá
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- evidence phải gồm direct outputs + tests
- worktree sạch sau mỗi pack

## 12) Verification commands
```bash
./atp help
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- session surface demo
- bounded diff
- compatibility proof với existing run_id / traceability surfaces
- note rõ vì sao đây không phải runtime state system

## 14) Final feature acceptance
Feature được accept khi ATP có repo-local session tracking surface đủ dùng cho review continuity mà không biến thành execution manager.

## 15) Prompt-CMD execution block
```text
You are executing feature F-102 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define one bounded repo-local execution session identity surface that complements existing run_id/traceability outputs.

Required verification commands:
- direct command exposing the session surface
- ./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
- python3 -m pytest -q tests/unit

Expected evidence:
- deterministic session identity
- no runtime-state subsystem drift
- compatibility with existing bounded execution outputs
```
