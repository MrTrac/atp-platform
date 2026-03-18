# Feature Program — Multi-request Execution Surface

## 0) Identity
- **Feature ID:** F-101
- **Feature name:** Multi-request Execution Surface
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-18

## 1) Objective
Mở một bounded multi-request execution surface cho ATP để operator có thể làm việc với nhiều request trong cùng execution line một cách deterministic, repo-local, và human-gated, nhưng không biến ATP thành orchestration engine, batch scheduler, hay queue processor.

## 2) Why now
- **Driver:** v1.1 đã harden rất mạnh single-request chain; giá trị mở rộng kế tiếp là cho phép multi-request entry surface có kiểm soát.
- **Expected value:** tăng khả năng vận hành thực tế cho operator mà vẫn giữ JSON contracts, bounded execution, và reviewability.
- **Risk:** dễ trượt sang batch automation, async queue, hoặc multi-AI routing nếu decomposition không chặt.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding từ ATP hiện tại:
- request-chain single-request đã complete và hardened ở v1.1
- `./atp` là canonical repo-root launcher
- canonical fixture hiện tại là `tests/fixtures/requests/sample_request_slice02.yaml`
- manual single-AI handoff vẫn là terminal bounded surface

## 4) Scope
### In-scope
- bounded multi-request entry surface
- deterministic aggregation / ordering cho nhiều request trong cùng một invocation
- reviewable, repo-local operator surfaces cho multi-request execution

### Non-goals
- multi-AI orchestration
- scheduler / queue / graph / daemon / background automation
- thay đổi request/bundle/prompt semantics của single-request path
- async execution hoặc provider abstraction

## 5) Dependencies
- **Upstream features:** v1.1 completed baseline
- **Systems/components:** root CLI, request-chain CLIs, output contract
- **External constraints:** phải giữ single-request JSON contracts backward-compatible

## 6) Completion definition
- [ ] có multi-request execution surface bounded
- [ ] single-request path không bị phá
- [ ] verification pass cho multi-request và canonical single-request path
- [ ] không có dấu hiệu orchestration/batch-engine drift

## 7) Execution strategy
Feature này phải mở theo 3 pack nhỏ:
- P1: xác định shape bounded của multi-request surface
- P2: harden output/help/validation cho surface đó
- P3: xác nhận backward compatibility và no-drift

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define multi-request entry | thêm entry surface bounded cho nhiều request | direct command + pytest | diff + output mẫu |
| P2 | harden multi-request contract | help, validation, output ordering cho surface mới | direct commands + pytest | error/output evidence |
| P3 | confirm backward compatibility | verify single-request path không bị phá | smoke + pytest | regression evidence |

## 9) Pack details

### Pack P1 — Multi-request Entry
- **Objective:** tạo đúng một multi-request entry surface bounded và deterministic.
- **In-scope:** command surface, fixture list input, deterministic ordering.
- **Non-goals:** batch engine, fan-out execution, session framework.
- **Fail-stop conditions:**
  - design bắt đầu imply orchestration hoặc async processing
  - single-request path bị buộc phải đổi semantics
  - verification fail
- **Verification strategy:**
  - direct repo-root command cho surface mới
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Multi-request Contract Hardening
- **Objective:** làm rõ validation, help, output shape cho multi-request surface.
- **In-scope:** guidance, deterministic result ordering, bounded invalid-input handling.
- **Non-goals:** alternate renderer, batch-progress UI, retry logic.
- **Fail-stop conditions:**
  - output shape trượt thành framework report lớn
  - validation bắt đầu imply scheduler/queue semantics
  - verification fail
- **Verification strategy:**
  - command help / invalid cases / happy path
  - `./atp help`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Compatibility Confirmation
- **Objective:** chốt rằng surface mới không phá v1.1 baseline.
- **In-scope:** regression verification, bounded docs/help refinement nếu thật cần.
- **Non-goals:** mở thêm capability mới.
- **Fail-stop conditions:**
  - phải sửa rộng nhiều feature cũ mới chạy được
  - canonical single-request smoke không còn pass
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - relevant multi-request command
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop ngay nếu:
- scope drift sang orchestration / automation / provider abstraction
- multi-request surface không còn bounded
- backward compatibility với JSON contracts không giữ được
- verification không thể hoàn tất

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải có direct verification evidence
- không batch nhiều pack vào một commit
- worktree phải sạch giữa các checkpoint

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
- reproduced need cho multi-request surface
- bounded diff
- outputs chứng minh deterministic ordering
- regression evidence rằng single-request path vẫn nguyên

## 14) Final feature acceptance
Feature được accept khi ATP có multi-request execution surface bounded, reviewable, và backward-compatible, nhưng chưa hề mở orchestration hay batch automation.

## 15) Prompt-CMD execution block
```text
You are executing feature F-101 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define one bounded multi-request execution entry surface without breaking the single-request chain.

Required verification commands:
- direct repo-root command for the new multi-request surface
- ./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
- python3 -m pytest -q tests/unit

Expected evidence:
- one concrete bounded multi-request entry surface
- no orchestration drift
- backward-compatible single-request path
```
