# Feature Program — Review & Manual Handoff Clarity

## 0) Identity
- **Feature ID:** F-003
- **Feature name:** Review & Manual Handoff Clarity
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Tiếp tục giảm ambiguity của review-first và manual single-AI handoff surface trong ATP bounded chain, đặc biệt ở terminal path `request-bundle -> request-prompt`, nhưng không biến ATP thành generalized prompt framework.

## 2) Why now
- **Driver:** current chain đã usable, nhưng chất lượng review/handoff clarity quyết định operator confidence thực tế.
- **Expected value:** operator biết rõ hơn phải review gì, giao gì, và vì sao handoff là bounded-safe.
- **Risk:** trượt sang broad prompt/handoff framework.

## 3) ATP-specific context
Grounding slices:
- Slice 03, 04: bundle và prompt surfaces
- Slice 08, 11, 14, 18, 19: review/discoverability/handoff clarity

## 4) Scope
### In-scope
- derived review-first and handoff clarity surfaces
- manual single-AI terminal surface hardening
- review evidence expectations for bundle/prompt transition

### Out-of-scope
- prompt semantics redesign
- alternate renderer
- multi-AI or provider routing

## 5) Dependencies
- **Upstream features:** F-001, F-002
- **Systems/components:** request-bundle, request-prompt, output contract
- **External constraints:** handoff stays manual and single-AI only

## 6) Completion definition
- [ ] review-first / handoff surface ambiguity giảm rõ
- [ ] tests pass
- [ ] JSON-only preserved
- [ ] no scope drift

## 7) Execution strategy
Feature này nên chạy từ review-surface clarity -> handoff-surface clarity -> acceptance-ready manual handoff cues.

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | Review-first clarity | bundle/prompt review-first cues | direct CLI + pytest | outputs |
| P2 | Manual handoff surface clarity | prompt terminal handoff surface | prompt CLI + pytest | prompt output |
| P3 | Review-to-handoff acceptance cues | bounded acceptance/handoff bridge | smoke + pytest | smoke + outputs |

## 9) Pack details

### Pack P1 — Review-First Clarity
- **Objective:** chốt operator review order cho bundle/prompt
- **Steps:**
  1. inspect existing review-first metadata
  2. harden only if ambiguity thực sự còn
- **Fail-stop triggers:** duplicate payload / semantic churn
- **Verification commands:**
  - `./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml`
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Manual Handoff Surface
- **Objective:** làm terminal handoff surface low-ambiguity hơn
- **Steps:**
  1. inspect prompt handoff surface
  2. add compact cues if needed
- **Fail-stop triggers:** transform into prompt system/framework
- **Verification commands:**
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Acceptance Bridge
- **Objective:** giúp operator chuyển từ review xong sang handoff một cách bounded
- **Steps:**
  1. tighten review-to-handoff path cues
  2. validate with smoke and direct prompt output
- **Fail-stop triggers:** help/output surfaces become noisy
- **Verification commands:**
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu phải đổi prompt semantics hoặc phải mở generic handoff system.

## 11) Commit/test/checkpoint discipline
- commits phải gọn theo pack
- prompt/bundle direct verification là mandatory

## 12) Verification commands
```bash
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- before/after prompt or bundle output summary
- tests
- any residual ambiguity notes

## 14) Final feature acceptance
Feature được accept khi bounded review path và manual single-AI handoff path rõ hơn nhưng ATP vẫn giữ same architecture and semantics.

## 15) Prompt-CMD execution block
```text
You are executing feature F-003 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and project pack truth.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Improve review-first clarity on bundle/prompt outputs without changing semantics.

Required verification commands:
- ./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
- ./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
- python3 -m pytest -q tests/unit

Expected evidence:
- compact operator-surface diff
- deterministic outputs
- passing tests
```
