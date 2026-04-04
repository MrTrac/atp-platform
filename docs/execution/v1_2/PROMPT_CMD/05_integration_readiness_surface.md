# Feature Program — Integration Readiness Surface

## 0) Identity
- **Feature ID:** F-105
- **Feature name:** Integration Readiness Surface
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Thêm integration readiness surface bounded cho ATP để operator và reviewer hiểu ATP đã sẵn sàng tích hợp tới đâu ở phase v1.2, nhưng không kích hoạt integration implementation, không mở automation, và không thay đổi bounded execution semantics.

## 2) Why now
- **Driver:** sau execution expansion và command hardening, ATP cần nói rõ readiness boundaries trước khi tiến sang deeper integration work.
- **Expected value:** giúp planning, review, và handoff rõ hơn mà không biến readiness thành implementation.
- **Risk:** readiness surface dễ bị đẩy thành pseudo-integration layer hoặc broad governance framework.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- control-plane integration là phase mới, chưa phải runtime integration activation
- readiness ở đây là operator-facing / review-facing signal, không phải integration engine

## 4) Scope
### In-scope
- compact derived readiness surface cho integration-prep
- bounded signals về “ready / not ready / blocked by design”
- operator-facing guidance về next safe integration-prep action

### Non-goals
- integration implementation
- provider abstraction
- orchestration / scheduler / automation
- broad governance subsystem

## 5) Dependencies
- **Upstream features:** F-102, F-104
- **Systems/components:** output contract, help/smoke surfaces, control-plane command posture
- **External constraints:** readiness surface phải non-breaking và bounded

## 6) Completion definition
- [ ] integration readiness surface xuất hiện rõ ràng và deterministic
- [ ] operator biết ATP đã sẵn sàng tới đâu và chưa sẵn sàng ở đâu
- [ ] không implied integration activation
- [ ] verification pass

## 7) Execution strategy
- P1: define bounded readiness categories
- P2: surface readiness in operator-facing outputs/help
- P3: confirm no pseudo-integration drift

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define readiness categories | compact readiness states and blockers | direct outputs + pytest | state map evidence |
| P2 | surface readiness cleanly | add bounded readiness cues to operator surfaces | direct commands + pytest | output/help evidence |
| P3 | confirm no pseudo-integration drift | verify readiness is only signaling, not activation | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Readiness Category Definition
- **Objective:** định nghĩa categories bounded cho integration readiness.
- **In-scope:** categorical states, blockers-by-design, next safe prep action.
- **Non-goals:** scoring system, activation logic.
- **Fail-stop conditions:**
  - readiness categories imply automation/activation
  - design đòi semantic change của existing artifacts
  - verification fail
- **Verification strategy:**
  - direct operator-facing output checks
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Readiness Surface Integration
- **Objective:** surfacing readiness cho operator ở đúng places cần thiết.
- **In-scope:** review_summary/help/smoke cues nếu thật sự cần.
- **Non-goals:** new report framework, markdown renderer.
- **Fail-stop conditions:**
  - too much duplication/noise
  - readiness surface overlap nặng với confidence/readiness đã có mà không tạo value mới
  - verification fail
- **Verification strategy:**
  - `./atp help`
  - request-chain commands
  - `python3 -m pytest -q tests/unit`

### Pack P3 — No Pseudo-Integration Confirmation
- **Objective:** xác nhận readiness chỉ là signal, không phải activation.
- **In-scope:** regression and governance checks.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - readiness language imply integrated runtime
  - broader control-plane implementation bị kéo vào
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - relevant command surfaces
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- integration readiness surface biến thành pseudo-integration implementation
- overlap với existing readiness/confidence surfaces không còn clean
- bất kỳ scope drift nào sang provider abstraction hoặc orchestration
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ readiness signal nào được thêm
- worktree phải sạch sau mỗi pack

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
- clear state definitions
- bounded output/help diffs
- proof that readiness is signaling only
- regression outputs

## 14) Final feature acceptance
Feature được accept khi ATP có integration readiness surface rõ, bounded, non-breaking, và không imply integration activation.

## 15) Prompt-CMD execution block
```text
You are executing feature F-105 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded integration-readiness categories and blockers without implying integration activation.

Required verification commands:
- direct operator-facing output checks for readiness categories
- python3 -m pytest -q tests/unit

Expected evidence:
- compact readiness categories
- explicit blockers-by-design
- proof that this remains signaling only
```
