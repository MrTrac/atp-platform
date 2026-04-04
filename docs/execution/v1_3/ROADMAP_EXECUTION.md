# ATP Execution Roadmap v1.3

> **Purpose:** Execution roadmap generation mới cho ATP sau khi roadmap v1.2 đã complete, chuyển phase từ execution expansion & integration readiness signaling sang execution externalization & structured integration preparation theo bounded execution model.
> **Canonical model:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_EXECUTION_TEMPLATE.md`
> **Canonical rerun governance:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_RERUN_GOVERNANCE.md`
> **Project instance:** `docs/execution/v1_3/ROADMAP_EXECUTION.md`
> **Relationship với v1.1:** `docs/execution/ROADMAP_EXECUTION.md` là completed baseline roadmap của phase v1.1 và không bị sửa đổi.
> **Relationship với v1.2:** `docs/execution/v1_2/ROADMAP_EXECUTION.md` là completed baseline roadmap của phase v1.2 và không bị sửa đổi.

## 0) Metadata
- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Baseline:** `v1.0.4` on `main`
- **Execution branch:** `codex/release-v1.1-execution`
- **Owner:** ATP execution line
- **Generation:** `v1.3`
- **Status:** ACTIVE
- **Last updated:** 2026-03-19

## 1) Purpose
Roadmap v1.3 tồn tại để:
- chuyển ATP từ "integration readiness signaling" sang "execution externalization & structured integration preparation"
- làm ATP outputs có thể tiêu thụ được bởi external tooling mà không phá internal contracts
- tạo nền tảng structured cho future broader integration work qua bounded composition, artifact export, và contract projection
- giữ ATP ở repo-local, human-gated, bounded single-AI execution posture trong suốt quá trình externalization preparation

## 2) Vì sao đây là generation mới
Theo `ROADMAP_RERUN_GOVERNANCE.md`, lần tạo roadmap này thuộc:
- **Case C — Phase transition lớn:** ATP chuyển từ execution expansion & readiness signaling sang execution externalization & structured integration preparation
- **Case D — Roadmap exhaustion / roadmap completion:** tất cả 5 feature programs của roadmap v1.2 (F-101 đến F-105) đã complete

### Điều được giữ nguyên
- v1.1 roadmap cũ dưới `docs/execution/` vẫn là completed baseline
- v1.2 roadmap cũ dưới `docs/execution/v1_2/` vẫn là completed generation
- JSON-first output surfaces của request-chain
- bounded execution model
- human-gated control
- manual single-AI handoff là terminal surface hiện tại
- repo-local CLI model

### Điều thay đổi trong v1.3
- trọng tâm chuyển sang externalization: artifact export, structured composition, continuity linkage, contract projection, deployability
- feature map mới không lặp lại hardening lanes (v1.1) hay expansion/readiness lanes (v1.2)
- feature programs mới tập trung vào khả năng ATP được tiêu thụ bởi caller bên ngoài theo bounded, structured cách

## 3) Baseline và invariants

### Canonical truth inputs phải đọc cùng
- AI_OS project pack:
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_PROJECT_CONTEXT.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_CURRENT_BASELINE.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_NEXT_STEP.md`
  - `/Users/nguyenthanhthu/AI_OS/20_PROJECTS/ATP/AI_HANDOFF_LATEST.md`
- Repo-local authority:
  - `README.md`
  - `docs/architecture/overview.md`
  - `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
  - `docs/design/request_model.md`
  - `docs/design/handoff_model.md`
  - `docs/execution/ROADMAP_EXECUTION.md` như completed baseline v1.1
  - `docs/execution/v1_2/ROADMAP_EXECUTION.md` như completed baseline v1.2

### v1.1 completed baseline
- Slices 01-19 đã harden bounded single-AI request-chain
- Feature programs F-001 đến F-005 của roadmap v1.1 đã complete
- Repo-root launcher canonical là `./atp`
- Canonical fixture là `tests/fixtures/requests/sample_request_slice02.yaml`

### v1.2 completed baseline
- F-101: Multi-request Execution Surface — bounded entry surface cho nhiều request files
- F-102: Execution Session Tracking (Repo-local) — derived-in-memory session identity
- F-103: Operator Readability Layer (Non-breaking) — compact operator scan summaries
- F-104: Control-plane Command Hardening — rõ ràng CLI boundaries và help contracts
- F-105: Integration Readiness Surface — truthful signaling-only readiness categories

### Invariants bắt buộc giữ ở v1.3
- không phá JSON contracts đã có
- không đổi request/bundle/prompt semantics
- không mở multi-AI orchestration
- không thêm scheduler / queue / graph / daemon / background automation
- không thêm provider abstraction
- không phá repo-local CLI model
- không bỏ human-gated control
- artifact export phải opt-in, không phải default behavior
- không có real external network calls, webhook, hay event consumer

## 4) Execution principles
- v1.3 vẫn chạy theo **feature-execution program** và **packs bounded**
- mỗi feature phải có đúng **3 pack: P1 / P2 / P3**
- mỗi pack phải reviewable, testable, fail-stop
- externalization work chỉ theo bounded surface, không by-pass v1.1/v1.2 contracts
- artifact export là preparation surface, không phải activation của broader integration runtime
- composition là synchronous, human-initiated, fail-stop tại mỗi stage — không phải automation

## 5) Priority map
| Priority | Feature | Why now | Risk | Dependencies |
|---|---|---|---|---|
| P0 | F-201 Execution Artifact Export Surface | ATP output hiện chỉ là stdout JSON; externalization bắt đầu từ việc làm artifacts addressable dưới workspace path | drift sang file-watch hay event-driven model | v1.2 complete baseline |
| P1 | F-202 Structured CLI Composition Surface | operator hiện phải chạy request-flow → request-bundle → request-prompt riêng lẻ; composition surface cho phép bounded sequential invocation trong một lệnh human-initiated | bị nhầm với automation; phải giữ synchronous, fail-stop, human-gated | F-201 artifact export contract |
| P2 | F-203 Session-to-Artifact Continuity Surface | session tracking hiện thiếu link tới artifacts đã tạo ra; continuity anchors cần thiết cho audit trail trước khi expose ra ngoài | trượt sang stateful runtime hay audit log engine | F-201, F-202 |
| P3 | F-204 Integration Contract Projection | sau khi export và continuity đã rõ, cần một machine-readable contract document mô tả cách external caller invokes ATP | bị nhầm với API implementation; phải giữ là derived/static artifact | F-201, F-202, F-203 |
| P4 | F-205 Deployability Readiness Assessment | cần surface rõ ATP cần gì để chạy trong môi trường mới, để planning adoption | trượt sang packaging/bundling engine | tất cả features trên |

## 6) Recommended execution order
1. **F-201 — Execution Artifact Export Surface**
2. **F-202 — Structured CLI Composition Surface**
3. **F-203 — Session-to-Artifact Continuity Surface**
4. **F-204 — Integration Contract Projection**
5. **F-205 — Deployability Readiness Assessment**

## 7) Feature summaries
| ID | Title | Scope summary | Status | Owner |
|---|---|---|---|---|
| F-201 | Execution Artifact Export Surface | thêm opt-in artifact export từ CLI ra workspace path; output vẫn JSON-first, không phá stdout contract | READY | ATP execution line |
| F-202 | Structured CLI Composition Surface | thêm bounded sequential composition command `./atp compose-chain` cho request-flow → request-bundle → request-prompt trong một invocation human-initiated | READY | ATP execution line |
| F-203 | Session-to-Artifact Continuity Surface | liên kết session records với artifacts đã tạo ra để audit trail rõ hơn mà không cần persistence layer | READY | ATP execution line |
| F-204 | Integration Contract Projection | sinh machine-readable contract document mô tả invocation surface của ATP cho external callers; derived/static, không phải active API | READY | ATP execution line |
| F-205 | Deployability Readiness Assessment | structured check environment và surface what's needed để ATP chạy ở môi trường mới; read-only, không thực hiện deploy | READY | ATP execution line |

## 8) Dependency graph
```text
F-201 -> F-202 -> F-204
F-201 -> F-203 -> F-204
F-204 -> F-205
```

## 9) Execution governance
- **Approval gates:** merge `main`, push `main`, tag release, architecture rewrite, broad integration activation
- **Branch discipline:** execution chỉ trên `codex/release-v1.1-execution`; `main` vẫn là stable released baseline `v1.0.4`
- **Generation discipline:** v1.1 và v1.2 roadmaps được frozen như completed baselines; v1.3 là generation mới, không phải in-place rewrite
- **Fail-stop:** dừng nếu:
  - scope drift sang orchestration / scheduler / automation / provider abstraction / real external integration
  - bất kỳ thay đổi nào phá JSON contract hiện có
  - artifact export bắt đầu imply event publishing, push, hoặc background writing
  - composition surface bắt đầu imply async execution hoặc retry logic
  - verification fail

## 10) Review / verify model
Mỗi feature program phải định nghĩa:
- direct verification commands
- unit tests / smoke checks cần chạy
- expected evidence:
  - bounded diff
  - command outputs
  - test outputs
  - risk note nói rõ vì sao chưa mở broader architecture
- acceptance chỉ khi capability mới vẫn non-breaking với v1.1 và v1.2 contracts

## 11) Mapping từ v1.2 sang v1.3

### v1.1 + v1.2 retained as completed baselines
- request-chain foundation (v1.1)
- operator usability hardening (v1.1)
- validation / smoke confidence (v1.1)
- review / handoff clarity (v1.1)
- bounded control surfaces (v1.1)
- bounded multi-request surface (v1.2)
- repo-local session continuity (v1.2)
- non-breaking readability layer (v1.2)
- control-plane command hardening (v1.2)
- integration readiness signaling (v1.2)

### v1.3 new focus lanes
- opt-in artifact export surface cho external consumption
- synchronous bounded composition command
- session-to-artifact continuity anchors
- machine-readable integration contract projection
- deployability readiness assessment

## 12) Current next recommendation
- **Current next action:** `pr-cmd run 01`
- **Program:** F-201 — Execution Artifact Export Surface
- **Why:** đây là bước externalization đầu tiên và có giá trị cao nhất — làm ATP output addressable mà không phá stdout contract; tất cả features khác trong v1.3 đều build trên nền này
- **Preconditions:**
  - branch vẫn là `codex/release-v1.1-execution`
  - worktree sạch
  - v1.1 và v1.2 baseline surfaces vẫn pass trên canonical fixture
  - đọc đủ canonical AI_OS inputs
- **Stop conditions:**
  - artifact export bắt đầu imply real-time publishing, push, hay background writing
  - bất kỳ output change nào phá JSON contract của stdout path hiện có
  - export path bắt đầu write vào repo root thay vì workspace directory
