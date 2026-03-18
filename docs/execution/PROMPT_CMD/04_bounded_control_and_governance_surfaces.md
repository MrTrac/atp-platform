# Feature Program — Bounded Control & Governance Surfaces

## 0) Identity
- **Feature ID:** F-004
- **Feature name:** Bounded Control & Governance Surfaces
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Giữ ATP execution line governable khi tiếp tục hardening v1.1: completion, readiness, confidence, operator path, và fail-stop discipline phải tiếp tục sạch nhưng không mở thêm governance bureaucracy không cần thiết.

## 2) Why now
- **Driver:** execution line đã dày hơn; nếu không gom lại thành governance/control lane, future packs dễ drift.
- **Expected value:** bounded execution tiếp tục mở nhưng vẫn reviewable và fail-stop được.
- **Risk:** tài liệu/control surface bị viết quá rộng, tách rời ATP reality.

## 3) ATP-specific context
Grounding:
- Slice 01 boundary contract là governance gốc của v1.1
- slices 09, 13, 15, 16, 18, 19 đã tạo control surfaces operator-facing

## 4) Scope
### In-scope
- governance-safe control surfaces cho current execution line
- bounded completion/readiness/confidence/path discipline
- minimal doc/control alignment nếu cần cho execution

### Out-of-scope
- broad governance rewrite
- release/integration planning
- orchestration / automation / provider abstraction

## 5) Dependencies
- **Upstream features:** F-001, F-002, F-003
- **Systems/components:** execution outputs, repo-local help/smoke guidance, docs/execution
- **External constraints:** baseline `v1.0.4` trên `main` phải bất biến

## 6) Completion definition
- [ ] current execution control surfaces nhất quán hơn
- [ ] fail-stop boundaries rõ
- [ ] verification pass
- [ ] không mở governance sprawl

## 7) Execution strategy
Thực hiện theo packs nhỏ thiên về control consistency, không thiên về thêm capability.

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | Control-surface consistency | outputs/help/smoke control cues | direct commands + pytest | outputs |
| P2 | Governance-safe progression cues | next-step / stop-condition cues | help/smoke + pytest | stdout |
| P3 | Execution-line acceptance discipline | bounded acceptance discipline surfaces | direct outputs + pytest | tests + notes |

## 9) Pack details

### Pack P1 — Control Consistency
- **Objective:** kiểm tra và chốt consistency giữa completion/readiness/confidence/path surfaces
- **Verification commands:**
  - `./atp help`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Governance-Safe Progression
- **Objective:** ensure next-step guidance không imply auto-execution hoặc integration
- **Verification commands:**
  - direct CLI outputs
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Acceptance Discipline
- **Objective:** make bounded acceptance path clearer if needed
- **Verification commands:**
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu change bắt đầu:
- imply release / integration approval
- broaden governance beyond current execution line
- rewrite ATP doctrine

## 11) Commit/test/checkpoint discipline
- mỗi pack một commit rõ
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
- diff summary
- command outputs
- explicit note rằng `main` / release gates không bị chạm

## 14) Final feature acceptance
Feature được accept khi ATP control surfaces đủ rõ để tiếp tục v1.1 execution line theo staged control mà không phải mở governance line mới.

## 15) Prompt-CMD execution block
```text
You are executing feature F-004 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and project pack truth.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Make current control surfaces more internally consistent without broadening governance scope.

Required verification commands:
- ./atp help
- ./atp smoke-request-chain
- python3 -m pytest -q tests/unit

Expected evidence:
- bounded control-surface diff
- no release/integration implication
- passing tests
```
