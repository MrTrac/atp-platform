# Feature Program — Operator Readability Layer (Non-breaking)

## 0) Identity
- **Feature ID:** F-103
- **Feature name:** Operator Readability Layer (Non-breaking)
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Thêm một readability layer compact, derived, non-breaking cho operator khi execution surfaces của ATP trở nên dày hơn, nhưng vẫn giữ JSON contracts, bounded execution semantics, và không tạo alternate renderer cạnh tranh.

## 2) Why now
- **Driver:** execution expansion và session tracking sẽ làm outputs giàu metadata hơn; readability cần được giữ chủ động.
- **Expected value:** operator scan nhanh hơn, review nhanh hơn, handoff an toàn hơn mà không phá compatibility.
- **Risk:** trượt sang text/markdown renderer hoặc duplicate payload quá nhiều.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- v1.1 đã có `review_summary`, confidence/readiness/completion surfaces
- ATP vẫn JSON-first
- readability layer mới phải build trên surfaces hiện có, không tạo surface song song lớn

## 4) Scope
### In-scope
- compact derived readability metadata
- deterministic ordering / grouping cải thiện scan
- bounded operator cues cho review/handoff/integration-prep

### Non-goals
- markdown/text alternate renderer
- TUI / dashboard
- payload duplication lớn
- semantic rewrite của existing artifacts

## 5) Dependencies
- **Upstream features:** F-101, F-102 khi outputs bắt đầu dày hơn
- **Systems/components:** output contract, smoke path, existing review_summary
- **External constraints:** JSON-only output phải được giữ nguyên

## 6) Completion definition
- [ ] readability gain measurable ở operator-facing surfaces
- [ ] JSON contracts backward-compatible
- [ ] không tạo competing renderer
- [ ] verification pass

## 7) Execution strategy
- P1: identify one bounded readability pain point mới
- P2: add compact readability layer
- P3: confirm no duplicate/noise drift

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | capture readability pain | isolate one real scanability gap | reproduce + pytest | output evidence |
| P2 | add non-breaking readability layer | compact derived metadata/order tweaks | direct commands + pytest | diff + outputs |
| P3 | confirm no-noise drift | check no duplication / no renderer drift | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Readability Gap Capture
- **Objective:** chứng minh một readability pain point cụ thể thay vì polish chung chung.
- **In-scope:** scan path, section placement, operator confusion evidence.
- **Non-goals:** aesthetic cleanup.
- **Fail-stop conditions:**
  - không chứng minh được pain point cụ thể
  - pain point thực ra đã được covered ở v1.1
  - verification fail
- **Verification strategy:**
  - reproduce current scan issue with direct commands
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Non-breaking Readability Layer
- **Objective:** sửa đúng readability gap đó bằng metadata/order changes bounded.
- **In-scope:** review_summary extensions, grouping, compact cues.
- **Non-goals:** alternate renderer, prose-heavy explanations.
- **Fail-stop conditions:**
  - payload duplication lớn
  - JSON contract break
  - verification fail
- **Verification strategy:**
  - request-chain commands
  - smoke path nếu liên quan
  - `python3 -m pytest -q tests/unit`

### Pack P3 — No-noise Confirmation
- **Objective:** xác nhận gain thật sự có, không phải over-polish.
- **In-scope:** regression verification, no-churn review.
- **Non-goals:** thêm capability mới.
- **Fail-stop conditions:**
  - change chủ yếu là cosmetic wording churn
  - output trở nên noisy hơn
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - direct request-chain outputs
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- readability layer trở thành renderer song song
- duplication/noise vượt quá value operator nhận được
- semantics hoặc JSON compatibility bị ảnh hưởng
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 readability gap = 1 pack commit
- review diff phải giải thích rõ gain operator-facing
- giữ worktree sạch giữa packs

## 12) Verification commands
```bash
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- reproduced readability pain
- compact bounded diff
- before/after output evidence
- note vì sao non-breaking

## 14) Final feature acceptance
Feature được accept khi ATP có readability improvements thực sự hữu ích cho operator mà vẫn JSON-first, non-breaking, và low-noise.

## 15) Prompt-CMD execution block
```text
You are executing feature F-103 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Capture one concrete operator readability gap that appears after execution expansion, then stop unless the gap is real and bounded.

Required verification commands:
- reproduce the readability issue with direct request-chain outputs
- python3 -m pytest -q tests/unit

Expected evidence:
- one concrete scanability gap
- proof that it is not already solved by v1.1 surfaces
- one bounded non-breaking follow-up candidate
```
