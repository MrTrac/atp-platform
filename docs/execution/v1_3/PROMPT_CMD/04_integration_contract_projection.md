# Feature Program — Integration Contract Projection

## 0) Identity
- **Feature ID:** F-204
- **Feature name:** Integration Contract Projection
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-19

## 1) Objective
Thêm `./atp integration-contract` command để sinh một machine-readable contract document mô tả cách external caller có thể invoke ATP, những inputs cần thiết, outputs sẽ nhận, và boundaries hiện tại. Contract document là derived/static artifact được tạo ra từ ATP current surfaces — không phải một API implementation, không phải một live endpoint, và không phải một active integration runtime. Đây là "specification as code" cho ATP integration surface, giúp planning, handoff, và future integration work rõ hơn.

## 2) Why now
- **Driver:** sau F-201 (artifact export), F-202 (composition), và F-203 (continuity anchors), ATP có đủ surfaces để describe rõ ràng invocation contract của mình. Contract projection là step cuối cùng trước khi ATP được coi là "integration-preparation complete" cho v1.3.
- **Expected value:** external callers và integration planners có một contract document authoritative mô tả ATP invocation surface; giảm ambiguity khi planning broader integration work; giữ integration scope bounded và documented.
- **Risk:** contract document dễ bị nhầm với API implementation hoặc live endpoint specification; phải giữ rõ ràng là derived/static, không phải active API.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- integration contract phải reflect ATP's ACTUAL current surfaces, không phải desired future state
- contract phải explicitly nêu boundaries và what is NOT supported
- contract document phải được generated trong một invocation, không có background computation
- không có live endpoint, schema registry, hay service discovery được tạo ra

## 4) Scope
### In-scope
- `./atp integration-contract` command mới xuất ra bounded JSON contract document
- contract bao gồm: invocation surface (commands, inputs, outputs), integration mode, supported features, unsupported features, safe entrypoints, blocked actions, current boundaries
- contract phải consistent với `core/integration_readiness.py` definitions
- opt-in `--export-dir` flag để write contract ra file (từ F-201)
- unit tests và smoke verification

### Non-goals
- live API endpoint hay service discovery
- schema registry hay contract validation engine
- OpenAPI / Swagger specification generation
- contract versioning system
- contract imply integration implementation

## 5) Dependencies
- **Upstream features:** F-201 (export contract), F-202 (composition contract), F-203 (continuity anchors) — cần cả 3 để contract document phản ánh đầy đủ surfaces
- **Systems/components:** `core/integration_readiness.py`, `cli/` entry points, `atp` launcher
- **External constraints:** contract document phải derived-only; không có network call hay external lookup

## 6) Completion definition
- [ ] `./atp integration-contract` command hoạt động và xuất ra bounded JSON contract
- [ ] contract phản ánh đúng ATP current surfaces (F-201, F-202, F-203 included)
- [ ] contract explicitly nêu boundaries và unsupported features
- [ ] contract consistent với `core/integration_readiness.py`
- [ ] smoke chain vẫn pass (regression)
- [ ] verification pass — unit tests

## 7) Execution strategy
- P1: define integration contract schema — fields, structure, consistency với integration_readiness module
- P2: implement `./atp integration-contract` command
- P3: xác nhận contract là derived/static, không imply integration activation, smoke chain vẫn pass

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define integration contract schema | contract fields, structure, consistency rules | pytest unit tests cho schema | contract schema evidence |
| P2 | implement integration-contract command | `./atp integration-contract`, derived JSON output | direct command + pytest | command output showing contract |
| P3 | confirm no activation drift | verify contract is static/derived, not live endpoint, smoke pass | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Integration Contract Schema Definition
- **Objective:** định nghĩa bounded integration contract schema — fields, structure, consistency rules với integration_readiness module.
- **In-scope:** contract schema (invocation_surface, integration_mode, supported_features, unsupported_features, safe_entrypoints, blocked_actions, boundaries, version), schema constants.
- **Non-goals:** implementation của command, live endpoint.
- **Fail-stop conditions:**
  - schema imply live API hoặc network endpoint
  - schema mâu thuẫn với `core/integration_readiness.py` definitions
  - verification fail
- **Verification strategy:**
  - unit tests kiểm tra contract schema
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Integration Contract Command Implementation
- **Objective:** implement `./atp integration-contract` command xuất ra JSON contract document.
- **In-scope:** CLI entry point `cli/integration_contract.py`, launcher case `integration-contract`, derived JSON output, opt-in `--export-dir` integration.
- **Non-goals:** live endpoint, schema registry, OpenAPI generation.
- **Fail-stop conditions:**
  - command requires network call hoặc external lookup
  - contract imply integration is activated
  - verification fail
- **Verification strategy:**
  - `./atp integration-contract`
  - `./atp integration-contract --export-dir /tmp/atp-contract-test`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — No Activation Drift Confirmation
- **Objective:** xác nhận contract document chỉ là derived/static specification, không phải live API activation.
- **In-scope:** regression tests, boundary lock tests, smoke chain.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - contract document imply runtime integration
  - smoke chain fail
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - `./atp integration-contract`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- contract document bắt đầu imply live API, real endpoint, hay integration activation
- contract generation đòi network call hay external system lookup
- contract mâu thuẫn với `core/integration_readiness.py` (INTEGRATION_MODE phải luôn là `not_activated`)
- smoke chain fail
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ contract schema / behavior nào được thêm
- worktree phải sạch sau mỗi pack

## 12) Verification commands
```bash
./atp help
./atp integration-contract
./atp integration-contract --export-dir /tmp/atp-contract-test
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- integration contract schema definitions
- `./atp integration-contract` output JSON showing bounded contract
- proof that contract explicitly says `integration_mode: not_activated`
- proof that unsupported_features and blocked_actions are explicit
- regression outputs from smoke chain

## 14) Final feature acceptance
Feature được accept khi `./atp integration-contract` xuất ra bounded machine-readable contract document, consistent với integration_readiness module, không imply integration activation, và không có bất kỳ live endpoint hay network call nào.

## 15) Prompt-CMD execution block
```text
You are executing feature F-204 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded integration contract schema — fields, structure, consistency with core/integration_readiness.py. Do NOT implement the CLI command yet.

Required verification commands:
- unit tests for integration contract schema module
- python3 -m pytest -q tests/unit

Expected evidence:
- contract schema defined (invocation_surface, integration_mode, boundaries)
- consistency with integration_readiness module verified
- proof this is schema definition only, not CLI implementation
- proof contract does NOT imply integration activation
```
