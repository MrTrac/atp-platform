# Feature Program — Execution Traceability & Review Evidence

## 0) Identity
- **Feature ID:** F-001
- **Feature name:** Execution Traceability & Review Evidence
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Làm cho ATP v1.1 bounded chain tạo ra review evidence rõ hơn, traceability rõ hơn, và acceptance-ready hơn mà không đẻ ra reporting framework lớn. Feature này tập trung vào việc giúp operator/reviewer trả lời chắc hơn: output hiện tại được build từ đâu, bằng evidence nào, và đủ gì để review/gate.

## 2) Why now
- **Driver:** Sau Slice 01-19, ATP đã usable nhưng evidence layer vẫn còn là “đọc payload và suy luận”.
- **Expected value:** giảm ambiguity trong review, acceptance, handoff, và future pack gating.
- **Risk:** nếu làm quá tay sẽ drift sang broad artifact/reporting system.

## 3) ATP-specific context
Must read:
- `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md`
- `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_CURRENT_BASELINE.md`
- `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_NEXT_STEP.md`
- `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_HANDOFF_LATEST.md`

Grounding from ATP reality:
- current bounded chain: request-flow -> request-bundle -> request-prompt
- current outputs đã có status / readiness / confidence surfaces
- ATP vẫn là manual single-AI line, JSON-centric, repo-local

## 4) Scope
### In-scope
- derived evidence metadata cho bounded outputs
- traceability tightening giữa request -> package -> bundle -> prompt
- review evidence expectations cho smoke/CLI surfaces

### Out-of-scope
- broad reporting subsystem
- runtime artifact persistence trong repo
- orchestration / scheduler / automation / provider abstraction

## 5) Dependencies
- **Upstream features:** slices 01-19; đặc biệt slices 11, 15, 16, 18
- **Systems/components:** `cli/output_contract.py`, smoke surface, bounded tests
- **External constraints:** giữ JSON-only, không tạo new architecture line

## 6) Completion definition
- [ ] functional behavior present: operator/reviewer có derived evidence surface rõ hơn
- [ ] tests/verification pass: direct CLI + smoke + unit tests pass
- [ ] docs updated if required: chỉ nếu cần trong execution-plan layer
- [ ] no policy/governance violations: không mở report framework rộng

## 7) Execution strategy
Feature này phải chạy theo packs nhỏ; mỗi pack chỉ tăng một lớp evidence/traceability value và phải verify ngay.

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | Harden chain traceability summary | derived traceability summary near operator surface | CLI direct outputs + pytest | diff + stdout |
| P2 | Harden review evidence surface | evidence-expected markers cho review/acceptance | smoke + pytest | smoke output + tests |
| P3 | Harden acceptance-ready evidence path | compact acceptance evidence hints | direct commands + pytest | deterministic outputs |

## 9) Pack details

### Pack P1 — Traceability Summary
- **Objective:** đưa traceability summary nhỏ lên gần đầu output
- **Steps:**
  1. inspect current traceability fields across flow/bundle/prompt
  2. add compact derived chain-trace surface
- **Fail-stop triggers:**
  - phải duplicate whole nested payload
  - phải lưu runtime artifacts vào repo
  - verification fail
- **Verification commands:**
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml`
  - `./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml`
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`
- **Evidence expected:** deterministic JSON diff + test pass
- **Checkpoint rule:** commit scoped vào output contract + tests

### Pack P2 — Review Evidence Surface
- **Objective:** làm rõ reviewer cần evidence gì cho step hiện tại
- **Steps:**
  1. derive evidence-needed / evidence-present hints
  2. verify smoke và operator outputs vẫn bounded
- **Fail-stop triggers:** wording chuyển thành broad checklist subsystem
- **Verification commands:**
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`
- **Evidence expected:** smoke stdout + tests

### Pack P3 — Acceptance-Ready Hints
- **Objective:** giúp reviewer nhìn ra khi nào output đủ acceptance-ready cho bounded step
- **Steps:**
  1. add compact acceptance evidence hints
  2. re-run direct outputs + tests
- **Fail-stop triggers:** overlap quá mạnh với existing readiness/confidence surfaces
- **Verification commands:**
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`
- **Evidence expected:** final prompt output + tests

## 10) Fail-stop rules
Stop nếu:
- conflict với AI_OS/project authority
- cần broad evidence framework mới
- verification không pass

## 11) Commit/test/checkpoint discipline
- Mỗi pack 1 commit sạch
- verify trước khi commit
- dừng nếu worktree không sạch giữa packs

## 12) Verification commands
```bash
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- scoped diff
- deterministic output snippets
- smoke result
- test outputs

## 14) Final feature acceptance
Feature được accept khi ATP traceability/review evidence path rõ hơn một cách compact, deterministic, bounded, và không tạo framework lớn.

## 15) Prompt-CMD execution block
```text
You are executing feature F-001 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and project pack truth.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Harden chain traceability summary without creating a broad evidence subsystem.

Required verification commands:
- ./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
- ./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
- ./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
- python3 -m pytest -q tests/unit

Expected evidence:
- compact diff on operator-facing surfaces
- deterministic output changes
- passing tests
```
