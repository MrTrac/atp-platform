# Feature Program — Execution Artifact Export Surface

## 0) Identity
- **Feature ID:** F-201
- **Feature name:** Execution Artifact Export Surface
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-19

## 1) Objective
Thêm opt-in artifact export surface cho ATP để operator và external tooling có thể đọc execution artifacts từ một workspace path xác định, thay vì chỉ từ stdout. Export phải hoàn toàn opt-in (flag-gated), không thay đổi stdout behavior mặc định, không phá JSON contracts hiện có, và không có bất kỳ background writing, event publishing, hay real-time push nào. Đây là bước externalization đầu tiên và là nền cho tất cả v1.3 features.

## 2) Why now
- **Driver:** sau v1.2, ATP có integration readiness signaling nhưng chưa có cách để external tooling tiêu thụ artifacts một cách addressable. Externalization bắt đầu từ đây.
- **Expected value:** external callers (scripts, CI steps, future integrations) có thể đọc ATP artifacts từ file thay vì cần parse stdout; tạo nền cho F-202 composition, F-203 continuity, và F-204 contract projection.
- **Risk:** export path có thể drift sang background writer, event emitter, hay file-watch daemon nếu không giữ bounded.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- stdout JSON là canonical primary output; export file là additive secondary surface
- export path phải nằm trong workspace directory (`SOURCE_DEV/workspace/`), không phải repo root
- không có automatic file watch, event publish, hay push sau khi export

## 4) Scope
### In-scope
- `--export-dir` flag cho `request-flow`, `request-bundle`, và `request-prompt` commands
- export artifact ra file JSON tại `<export-dir>/<run_id>/<artifact_type>.json`
- export manifest file mô tả artifacts đã export trong run
- unit tests và smoke verification cho export behavior
- tài liệu bounded export contract

### Non-goals
- export background hay automatic (phải luôn explicit human-initiated)
- event publishing hay webhook sau export
- file-watch hay polling mechanism
- real network upload / remote write
- schema validation engine cho exported files
- export thay thế stdout (stdout vẫn là canonical primary)

## 5) Dependencies
- **Upstream features:** v1.2 complete baseline (F-101 đến F-105)
- **Systems/components:** `cli/request_flow.py`, `cli/request_bundle.py`, `cli/request_prompt.py`, workspace path convention
- **External constraints:** export phải opt-in; không có side effect khi không có `--export-dir`

## 6) Completion definition
- [ ] `--export-dir` flag hoạt động trên `request-flow`, `request-bundle`, và `request-prompt`
- [ ] artifacts được write đúng path, đúng schema khi flag được cấp
- [ ] stdout behavior không thay đổi khi không có flag
- [ ] export manifest file được tạo khi export thành công
- [ ] verification pass — unit tests và smoke chain

## 7) Execution strategy
- P1: define artifact export contract — schema, path convention, manifest format
- P2: implement opt-in export flag trên 3 CLI commands
- P3: xác nhận export không phá stdout contract và smoke chain vẫn pass

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define export contract | export schema, path convention, manifest structure | pytest unit tests cho contract định nghĩa | contract evidence (schema, path map) |
| P2 | implement opt-in export | `--export-dir` flag trên 3 CLI commands, artifact write | direct command + pytest | command output + exported files |
| P3 | confirm stdout contract intact | verify export không thay đổi stdout behavior, smoke vẫn pass | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Export Contract Definition
- **Objective:** định nghĩa bounded export contract trước khi implement — schema, path, manifest.
- **In-scope:** export path convention (`<export-dir>/<run_id>/<artifact_type>.json`), manifest schema, export contract module.
- **Non-goals:** implementation của CLI flag, actual file write.
- **Fail-stop conditions:**
  - export contract imply real-time push hoặc background write
  - schema đòi thay đổi stdout JSON structure
  - verification fail
- **Verification strategy:**
  - unit tests kiểm tra contract definitions (module constants, schema shape)
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Opt-in Export Implementation
- **Objective:** implement `--export-dir` flag và write artifacts ra file khi flag được cấp.
- **In-scope:** flag parsing, file write, manifest generation, error handling khi dir không tồn tại.
- **Non-goals:** automatic retry, background write, network upload.
- **Fail-stop conditions:**
  - export thay đổi stdout output khi không có flag
  - export write vào repo root
  - verification fail
- **Verification strategy:**
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test`
  - `./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test`
  - `./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Stdout Contract Confirmation
- **Objective:** xác nhận export không phá stdout contract và ATP posture không thay đổi.
- **In-scope:** regression tests, smoke chain verification, boundary lock tests.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - stdout output thay đổi khi không có `--export-dir` flag
  - smoke chain fail
  - verification fail
- **Verification strategy:**
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml` (không có flag)
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- export behavior trở thành automatic hoặc default
- export path write vào repo root hoặc locations ngoài approved workspace
- stdout JSON bị thay đổi khi không có export flag
- bất kỳ real-time push, event emit, hay background write nào được thêm vào
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ contract/behavior nào được thêm
- worktree phải sạch sau mỗi pack

## 12) Verification commands
```bash
./atp help
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml --export-dir /tmp/atp-export-test
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- export contract definitions (schema, path map, manifest format)
- command output showing artifacts written to correct path
- proof that stdout is unchanged without flag
- regression outputs from smoke chain

## 14) Final feature acceptance
Feature được accept khi ATP có opt-in artifact export surface hoạt động đúng, bounded, non-breaking với stdout contract, và không có bất kỳ background hay automatic write nào.

## 15) Prompt-CMD execution block
```text
You are executing feature F-201 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded artifact export contract — schema, path convention, export manifest structure. Do NOT implement CLI flags yet.

Required verification commands:
- unit tests for export contract module
- python3 -m pytest -q tests/unit

Expected evidence:
- export contract schema defined
- path convention documented
- export manifest structure defined
- proof this is signaling/contract definition only, not implementation
```
