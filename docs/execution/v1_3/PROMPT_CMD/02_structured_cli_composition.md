# Feature Program — Structured CLI Composition Surface

## 0) Identity
- **Feature ID:** F-202
- **Feature name:** Structured CLI Composition Surface
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-19

## 1) Objective
Thêm bounded sequential composition command `./atp compose-chain` cho ATP để operator có thể khởi chạy chuỗi `request-flow → request-bundle → request-prompt` trong một lệnh human-initiated thay vì ba lệnh riêng lẻ. Composition phải synchronous, fail-stop tại mỗi stage, và không có bất kỳ background execution, retry logic, hay automated progression nào. Output của mỗi stage vẫn được emit ra stdout theo thứ tự, và toàn bộ composed output được wrap trong một bounded JSON envelope. Đây là convenience composition, không phải automation.

## 2) Why now
- **Driver:** sau F-201 artifact export, ATP output có thể được đọc từ file; composition surface cho phép staged outputs được linked rõ trong một invocation, tạo nền cho F-203 continuity anchors.
- **Expected value:** giảm operator friction trong happy-path execution; tạo một bounded reference invocation cho external callers; không phá bất kỳ individual command nào.
- **Risk:** composition surface dễ bị đẩy thành async pipeline engine, retry scheduler, hoặc background runner nếu không giữ bounded.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- composition phải synchronous và blocking trong cùng một process
- nếu bất kỳ stage nào fail, compose-chain phải dừng ngay và report rõ stage nào fail và tại sao
- không có retry, không có partial-success continuation, không có background worker
- individual commands (`request-flow`, `request-bundle`, `request-prompt`) vẫn hoạt động độc lập và không thay đổi

## 4) Scope
### In-scope
- `./atp compose-chain <request_file>` command mới
- sequential execution: request-flow → request-bundle → request-prompt trên cùng request file
- composed JSON output envelope gom 3 stage outputs
- fail-stop tại mỗi stage với rõ ràng stage error reporting
- opt-in `--export-dir` flag integration (từ F-201) trong compose-chain
- unit tests và smoke verification

### Non-goals
- parallel execution của stages
- retry logic khi stage fail
- background execution hay async mode
- dynamic stage ordering hay pluggable stage definition
- compose-chain thay thế individual commands (chúng vẫn tồn tại độc lập)
- multi-request composition (dùng `request-flow-multi` cho multi-request)

## 5) Dependencies
- **Upstream features:** F-201 (artifact export contract cần rõ trước khi compose-chain integrate export)
- **Systems/components:** `cli/request_flow.py`, `cli/request_bundle.py`, `cli/request_prompt.py`, `atp` launcher
- **External constraints:** composition phải synchronous; không có side effect nếu không được explicit invoke

## 6) Completion definition
- [ ] `./atp compose-chain <request_file>` hoạt động và chạy 3 stages tuần tự
- [ ] fail-stop tại stage đầu tiên fail — không tiếp tục sang stage tiếp theo
- [ ] composed JSON output rõ ràng mô tả stage outputs và composition status
- [ ] individual commands vẫn hoạt động như cũ (regression)
- [ ] smoke chain vẫn pass (regression)
- [ ] verification pass — unit tests

## 7) Execution strategy
- P1: define composition contract — output schema, stage sequencing semantics, fail-stop model
- P2: implement `./atp compose-chain` command với synchronous fail-stop execution
- P3: xác nhận composition không phá individual commands, không imply automation, smoke chain vẫn pass

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define composition contract | output envelope schema, stage sequencing model, fail-stop semantics | pytest unit tests cho contract definitions | contract schema evidence |
| P2 | implement compose-chain command | `./atp compose-chain`, synchronous 3-stage execution, composed output | direct command + pytest | command output showing 3 stages |
| P3 | confirm no automation drift | verify individual commands unchanged, composition is synchronous, smoke pass | smoke + pytest | regression note |

## 9) Pack details

### Pack P1 — Composition Contract Definition
- **Objective:** định nghĩa bounded composition contract trước khi implement — output envelope schema, stage model, fail-stop semantics.
- **In-scope:** composition output schema (`compose_chain_summary` với `stages`, `composition_status`, `fail_stage`), stage sequencing constants.
- **Non-goals:** implementation của command, actual execution.
- **Fail-stop conditions:**
  - contract imply async execution hoặc retry
  - schema đòi thay đổi individual command outputs
  - verification fail
- **Verification strategy:**
  - unit tests kiểm tra composition contract module
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Compose-chain Command Implementation
- **Objective:** implement `./atp compose-chain` dưới dạng synchronous staged CLI command.
- **In-scope:** CLI entry point `cli/compose_chain.py`, launcher case `compose-chain`, 3-stage sequential execution, fail-stop error reporting, composed JSON envelope.
- **Non-goals:** async mode, retry, parallel stages, background execution.
- **Fail-stop conditions:**
  - bất kỳ stage nào continue sau failure
  - background process được spawn
  - stdout của individual commands thay đổi
  - verification fail
- **Verification strategy:**
  - `./atp compose-chain tests/fixtures/requests/sample_request_slice02.yaml`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Automation Drift Confirmation
- **Objective:** xác nhận composition chỉ là synchronous convenience, không phải automation engine.
- **In-scope:** regression tests cho individual commands, boundary lock tests cho compose-chain, smoke chain.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - compose-chain imply retry hay async
  - individual commands thay đổi behavior
  - smoke chain fail
  - verification fail
- **Verification strategy:**
  - `./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml` (unchanged)
  - `./atp compose-chain tests/fixtures/requests/sample_request_slice02.yaml`
  - `./atp smoke-request-chain`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- composition bắt đầu imply async execution, retry, hay background runner
- individual commands bị thay đổi để accommodate composition
- bất kỳ stage nào tiếp tục chạy sau stage trước đó fail
- smoke chain fail
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ composition behavior nào được thêm
- worktree phải sạch sau mỗi pack

## 12) Verification commands
```bash
./atp help
./atp request-flow tests/fixtures/requests/sample_request_slice02.yaml
./atp request-bundle tests/fixtures/requests/sample_request_slice02.yaml
./atp request-prompt tests/fixtures/requests/sample_request_slice02.yaml
./atp compose-chain tests/fixtures/requests/sample_request_slice02.yaml
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- composition contract definitions (output schema, stage model, fail-stop semantics)
- compose-chain command output showing 3 stages executed sequentially
- proof that individual commands are unchanged (regression diff)
- proof that compose-chain is synchronous and fails fast

## 14) Final feature acceptance
Feature được accept khi `./atp compose-chain` hoạt động đúng, synchronous, fail-stop tại mỗi stage, không thay đổi individual commands, và không có bất kỳ automation/background execution nào.

## 15) Prompt-CMD execution block
```text
You are executing feature F-202 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded composition contract — output envelope schema, stage sequencing model, fail-stop semantics. Do NOT implement the CLI command yet.

Required verification commands:
- unit tests for composition contract module
- python3 -m pytest -q tests/unit

Expected evidence:
- composition output schema defined
- stage sequencing model documented
- fail-stop semantics explicit
- proof this is contract definition only, not CLI implementation
```
