# Feature Program — Deployability Readiness Assessment

## 0) Identity
- **Feature ID:** F-205
- **Feature name:** Deployability Readiness Assessment
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Status:** READY
- **Last updated:** 2026-03-19

## 1) Objective
Thêm `./atp deployability-check` command để đánh giá structured deployability readiness của ATP trong môi trường hiện tại và report những gì cần thiết để chạy ATP ở một môi trường khác. Assessment phải read-only, bounded, và không thực hiện bất kỳ deployment hay packaging action nào. Output là một bounded JSON report liệt kê: Python version requirements, dependency state, entry point clarity, workspace path requirements, configuration surface gaps, và blockers-by-design cho deployment. Đây là adoption readiness signal, không phải deployment engine.

## 2) Why now
- **Driver:** sau khi v1.3 externalization features (F-201 đến F-204) complete, ATP cần surface rõ ràng những gì required để chạy ATP ở môi trường mới — giúp adoption planning và handoff. Đây là feature cuối cùng của v1.3 và đóng gói phase này.
- **Expected value:** operator và integration planner biết chính xác ATP cần gì (Python version, dependencies, workspace path, permissions) để adopt ATP vào một môi trường mới; giúp planning mà không cần ad hoc investigation.
- **Risk:** deployability-check có thể drift sang packaging engine, Docker builder, hay CI/CD automation nếu không giữ bounded.

## 3) ATP-specific context
Canonical inputs phải đọc:
- `AI_PROJECT_CONTEXT.md`
- `AI_CURRENT_BASELINE.md`
- `AI_NEXT_STEP.md`
- `AI_HANDOFF_LATEST.md`

Grounding:
- ATP hiện vẫn repo-local, human-gated, bounded single-AI
- deployability-check phải read-only — không install packages, không tạo Docker image, không push artifacts
- assessment phải reflect ATP's actual current requirements, không phải hypothetical packaging
- blockers-by-design (orchestration, provider abstraction, multi-AI) phải explicit trong report
- assessment phải runnable từ repo root trong một command, không cần external tooling

## 4) Scope
### In-scope
- `./atp deployability-check` command mới xuất ra bounded JSON readiness report
- report bao gồm: Python version check, installed dependency state (`requirements.txt` / trực tiếp), entry point check (`./atp` launcher), workspace path requirements, configuration surface gaps, blockers-by-design
- read-only environment inspection (không install, không write, không modify)
- opt-in `--export-dir` flag để write report ra file (từ F-201)
- unit tests và smoke verification

### Non-goals
- actual deployment hay packaging
- Docker / container image building
- CI/CD pipeline configuration generation
- package publishing
- multi-environment orchestration
- dependency installation hay upgrade

## 5) Dependencies
- **Upstream features:** F-201 (export flag contract), F-202 (composition contract), F-203 (continuity anchors), F-204 (integration contract) — cần toàn bộ v1.3 surfaces rõ trước khi deployability assessment phản ánh đúng
- **Systems/components:** `atp` launcher, `requirements.txt` hoặc equivalent, workspace path convention
- **External constraints:** phải read-only; không có network call hay package install; không có side effect trong repo

## 6) Completion definition
- [ ] `./atp deployability-check` command hoạt động và xuất ra bounded JSON report
- [ ] report phản ánh đúng Python version, dependency state, và entry point state của môi trường hiện tại
- [ ] report explicitly nêu blockers-by-design (orchestration, automation, network activation)
- [ ] smoke chain vẫn pass (regression)
- [ ] verification pass — unit tests

## 7) Execution strategy
- P1: define deployability assessment schema — categories, check items, blocker definitions
- P2: implement `./atp deployability-check` command với bounded read-only checks
- P3: xác nhận assessment là read-only, không có side effects, smoke chain vẫn pass

## 8) Pack sequence
| Pack | Goal | Scope | Verification | Evidence |
|---|---|---|---|---|
| P1 | define assessment schema | check categories, report structure, blockers-by-design | pytest unit tests cho schema | assessment schema evidence |
| P2 | implement deployability-check | `./atp deployability-check`, read-only environment checks, JSON report | direct command + pytest | command output showing assessment |
| P3 | confirm read-only posture | verify no side effects, no installs, smoke pass, v1.3 surfaces complete | smoke + pytest | regression note + v1.3 completion evidence |

## 9) Pack details

### Pack P1 — Assessment Schema Definition
- **Objective:** định nghĩa bounded deployability assessment schema — check categories, report structure, blockers-by-design.
- **In-scope:** assessment schema (`python_version_check`, `dependency_state`, `entry_point_check`, `workspace_path_requirements`, `configuration_gaps`, `blockers_by_design`, `overall_readiness_signal`).
- **Non-goals:** implementation của command, actual environment checks.
- **Fail-stop conditions:**
  - schema imply packaging hoặc deployment action
  - schema đòi network call để build
  - verification fail
- **Verification strategy:**
  - unit tests kiểm tra assessment schema module
  - `python3 -m pytest -q tests/unit`

### Pack P2 — Deployability Check Implementation
- **Objective:** implement `./atp deployability-check` với read-only bounded environment checks.
- **In-scope:** CLI entry point `cli/deployability_check.py`, launcher case `deployability-check`, Python version check, dependency presence check, entry point presence check, workspace path requirements, blockers-by-design listing.
- **Non-goals:** package install, network download, deployment, Docker build.
- **Fail-stop conditions:**
  - command performs any write, install, atau network call
  - assessment report imply ATP is being deployed
  - verification fail
- **Verification strategy:**
  - `./atp deployability-check`
  - `./atp deployability-check --export-dir /tmp/atp-deploy-check`
  - `python3 -m pytest -q tests/unit`

### Pack P3 — Read-only Posture Confirmation
- **Objective:** xác nhận deployability-check hoàn toàn read-only, không có side effects, và v1.3 feature set complete.
- **In-scope:** regression tests, boundary lock tests cho read-only posture, smoke chain, v1.3 completeness check.
- **Non-goals:** feature expansion.
- **Fail-stop conditions:**
  - bất kỳ write hay install nào được thực hiện
  - smoke chain fail
  - verification fail
- **Verification strategy:**
  - `./atp smoke-request-chain`
  - `./atp deployability-check`
  - `python3 -m pytest -q tests/unit`

## 10) Fail-stop rules
Stop nếu:
- deployability-check thực hiện bất kỳ package install, file write (ngoài export), hay network call nào
- assessment imply deployment đang xảy ra hoặc được kích hoạt
- overall_readiness_signal được set thành "deployed" hay "activated"
- smoke chain fail
- verification fail

## 11) Commit/test/checkpoint discipline
- 1 pack = 1 commit
- mỗi pack phải chỉ rõ assessment category nào được thêm
- worktree phải sạch sau mỗi pack
- Pack P3 commit là commit cuối cùng của v1.3 feature set

## 12) Verification commands
```bash
./atp help
./atp deployability-check
./atp deployability-check --export-dir /tmp/atp-deploy-check
./atp smoke-request-chain
python3 -m pytest -q tests/unit
```

## 13) Review evidence expected
- deployability assessment schema definitions
- `./atp deployability-check` output JSON showing bounded assessment
- proof that command is read-only (no writes, no installs, no network)
- explicit blockers-by-design in report
- regression outputs from smoke chain
- evidence that v1.3 feature set is complete (all 5 features done)

## 14) Final feature acceptance
Feature được accept khi `./atp deployability-check` xuất ra bounded read-only assessment report, phản ánh đúng ATP requirements, explicit blockers-by-design, và không có bất kỳ side effect, install, hay network call nào. Completion của F-205 cũng marks v1.3 execution phase complete.

## 15) Prompt-CMD execution block
```text
You are executing feature F-205 for project ATP.

Constraints:
- Canonical-first: obey AI_OS authority and ATP repo-local boundaries.
- Staged control: execute ONLY the next pack specified.
- Fail-stop: stop on ambiguity, missing inputs, or failed verification.

Current pack to execute: P1
Pack objective: Define bounded deployability assessment schema — check categories (python_version, dependency_state, entry_point, workspace_path_requirements, blockers_by_design), report structure. Do NOT implement CLI command yet.

Required verification commands:
- unit tests for assessment schema module
- python3 -m pytest -q tests/unit

Expected evidence:
- assessment schema defined with all check categories
- blockers_by_design list explicit (orchestration, automation, network activation)
- overall_readiness_signal field defined (not "deployed", not "activated")
- proof this is schema definition only, not CLI implementation
```
