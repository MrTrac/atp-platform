# Feature Program — Session-to-Artifact Continuity Surface

## 0) Identity
- **Feature ID:** F-203
- **Feature name:** Session-to-Artifact Continuity Surface
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-19

## 1) Objective
Mở rộng session tracking (F-102) để bao gồm continuity anchors liên kết session records với artifacts đã tạo ra trong session đó. Khi operator chạy `execution-session` hoặc `compose-chain`, session summary sẽ ghi nhận không chỉ request IDs mà còn artifact IDs, artifact types, và (nếu có export) export paths — tạo audit trail rõ ràng từ session sang artifacts. Đây là derived-in-memory linkage, không phải persistent state store hay audit log engine.

## 2) Why now
- **Driver:** sau F-201 (artifact export) và F-202 (composition), session records cần phản ánh artifacts đã tạo để review và handoff rõ hơn. Continuity anchors là nền cho F-204 integration contract projection.
- **Expected value:** operator và reviewer có thể nhìn vào session summary và biết chính xác artifacts nào được tạo ra, ở đâu, và theo thứ tự nào — mà không cần query external system.
- **Risk:** continuity anchors có thể drift sang stateful audit log, persistent session database, hoặc event sourcing pattern nếu không giữ bounded.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- session tracking hiện tại (`core/session_tracking.py`) là derived-in-memory từ request inputs
- continuity anchors phải cũng là derived — computed từ artifacts đã tạo ra trong cùng invocation
- không có database write, không có persistent state, không có background log
- nếu không có export (`--export-dir`), continuity anchors chỉ ghi nhận artifact types và IDs (không có path)

## 4) Scope
### In-scope
- `artifact_continuity_anchors` field trong session summary của `execution-session` và `compose-chain`
- anchor bao gồm: artifact IDs, artifact types, creation order, export path nếu có
- `build_artifact_continuity_anchors()` function trong `core/session_tracking.py` hoặc module riêng
- unit tests và smoke verification

### Non-goals
- persistent session log hay audit database
- real-time artifact tracking hay file watcher
- cross-session continuity (chỉ within-session)
- artifact validation hay schema enforcement
- continuity anchors thay thế artifact content trong output

## 5) Dependencies
- **Upstream features:** F-201 (export path contract cần rõ để anchor có thể reference), F-202 (compose-chain cần emit artifact IDs cho session)
- **Systems/components:** `core/session_tracking.py`, `cli/execution_session.py`, `cli/compose_chain.py`
- **External constraints:** continuity phải derived-only; không có file read hay network call để build anchors

## 6) Completion definition
- [ ] `artifact_continuity_anchors` xuất hiện trong `execution-session` output sau khi artifacts được tạo
- [ ] anchors ghi nhận đúng artifact IDs, types, và order
- [ ] anchors ghi nhận export path nếu `--export-dir` được dùng
- [ ] session summary không thay đổi khi không có artifacts (graceful empty anchors)
- [ ] verification pass — unit tests và smoke chain

## 7) Execution strategy
- P1: define continuity anchor schema và mở rộng session tracking contract
- P2: implement `artifact_continuity_anchors` trong execution-session và compose-chain outputs
- P3: xác nhận continuity là derived-only, không có persistence, smoke chain vẫn pass

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define continuity anchor schema | anchor fields, empty-anchor contract, integration với session tracking | pytest unit tests | anchor schema evidence |
| P2 | implement continuity anchors | `build_artifact_continuity_anchors()`, integration vào execution-session và compose-chain | direct commands + pytest | session output với anchors |
| P3 | confirm no persistence drift | verify anchors là derived-only, no file write, no background logging | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Continuity Anchor Schema Definition
- **Objective:** định nghĩa bounded continuity anchor schema — fields, empty-anchor contract, integration point với session tracking.
- **In-scope:** anchor schema (`artifact_id`, `artifact_type`, `creation_order`, `export_path` khi có), empty-anchor pattern (khi không có artifacts).
- **Non-goals:** implementation, actual file write hay database write.
- **Fail-stop conditions:**
  - schema imply persistent state hoặc cross-session tracking
  - anchor đòi file read để build
  - verification fail
- **Verification strategy:**
  - unit tests kiểm tra anchor schema module
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Continuity Anchor Implementation
- **Objective:** implement `build_artifact_continuity_anchors()` và integrate vào execution-session và compose-chain session summaries.
- **In-scope:** function building derived anchors từ in-memory artifact data, output field trong session summary.
- **Non-goals:** database write, persistent log, cross-session linkage.
- **Fail-stop conditions:**
  - anchor requires file system read hoặc external lookup
  - session summary thay đổi shape khi không có artifacts
  - verification fail
- **Verification strategy:**
  - `./atp execution-session tests/fixtures/requests/sample_request_slice02.yaml`
  - `./atp compose-chain tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — No Persistence Confirmation
- **Objective:** xác nhận continuity anchors không có persistence side-effects và ATP posture không thay đổi.
- **In-scope:** regression tests, boundary lock tests cho derived-only anchors, smoke chain.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - bất kỳ file write nào bên ngoài `--export-dir` scope
  - anchor requires stateful lookup
  - smoke chain fail
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- continuity anchors đòi persistent state hoặc database
- anchor building đòi file read hay external system call
- cross-session continuity bị thêm vào
- session summary shape thay đổi khi không có artifacts
- smoke chain fail
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ continuity behavior nào được thêm
- worktree phải sạch sau mỗi pack

## 12) Verification commands
```bash
./atp help
./atp execution-session tests/fixtures/requests/sample_request_slice02.yaml
./atp compose-chain tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- continuity anchor schema definitions
- execution-session output showing `artifact_continuity_anchors` field
- proof that anchors are derived-in-memory (no file write when no `--export-dir`)
- regression outputs from smoke chain

## 14) Final feature acceptance
Feature được accept khi session records có artifact continuity anchors rõ, derived-only, không có persistence side-effects, và không thay đổi session summary shape khi không có artifacts.

## 15) Prompt-CMD execution block
```text
You are executing feature F-203 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded continuity anchor schema — fields, empty-anchor contract, integration point with session tracking. Do NOT implement the function yet.

Required verification commands:
- unit tests for continuity anchor schema module
- python3 -m pytest -q tests/unit

Expected evidence:
- anchor schema defined (artifact_id, artifact_type, creation_order, export_path)
- empty-anchor pattern documented
- integration point with session summary clear
- proof this is schema definition only, not implementation
```
