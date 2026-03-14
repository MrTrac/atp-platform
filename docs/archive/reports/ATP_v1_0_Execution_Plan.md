# ATP v1.0 Execution Plan

## 1. Execution identity

- Milestone: `ATP v1.0`
- Target version: `v1.0.0`
- Planning branch: `v1.0-planning`
- Status: `Planned`

## 2. Execution objective

Mục tiêu của execution plan này là chuyển `v1.0` từ planning baseline sang execution baseline có kiểm soát, bắt đầu bằng Slice A:

- `Review / Approval Gate Contract`

Execution của `v1.0` phải bảo đảm:

- không drift khỏi operational maturity intent
- không mở rộng scope sang `v2`
- giữ continuity rõ với `v0.7.0`
- tạo được evidence đủ để review, consolidate, freeze, và close-out về sau

## 3. Execution principles

Toàn bộ execution của `v1.0` tuân theo các nguyên tắc sau:

1. Stable core first, controlled operationalization next.
2. Không dùng `v1.0` như cớ để redesign ATP.
3. Slice A phải giữ boundary hẹp và file-based.
4. Mọi output planning/implementation phải trace được về roadmap và close-out continuity.
5. Mọi thay đổi ở docs layer phải rà README tại level tương ứng.
6. Chỉ freeze khi evidence chain đầy đủ và nhất quán.

## 4. Planned execution phases

## Phase 0 — Planning baseline lock

### Purpose
Khóa planning baseline của `v1.0`.

### Tasks
- chuẩn hóa `ATP_v1_0_Roadmap.md`
- chuẩn hóa `ATP_v1_0_Milestone_Proposal.md`
- chuẩn hóa `ATP_v1_0_Execution_Plan.md`
- xác nhận Slice A là first execution step của `v1.0`

### Outputs
- version roadmap sạch
- milestone proposal sạch
- execution plan sạch

### Validation
- ba tài liệu không mâu thuẫn nhau
- semantic `v1.0` đúng là controlled operationalization
- `v0 -> v1` continuity được giải thích rõ

### Exit criteria
- planning baseline coherent và reviewable

## Phase 1 — Slice A planning bundle completion

### Purpose
Hoàn tất bundle supporting docs cho `Review / Approval Gate Contract`.

### Tasks
- viết Slice A execution plan
- viết gate contract
- viết traceability model
- viết acceptance criteria
- viết review checklist

### Outputs
- bundle supporting docs hoàn chỉnh cho Slice A

### Validation
- bundle không mâu thuẫn với major roadmap, version roadmap, proposal, execution plan
- boundary với approval UI / recovery / routing / orchestration được giữ rõ
- lifecycle placement sau `v0.7.0` finalization record được mô tả rõ

### Exit criteria
- Slice A bundle đủ rõ để làm basis cho implementation pass và supporting-doc normalization sau implementation

## Phase 2 — Slice A implementation pass

### Purpose
Implement narrow runtime/file-based contract cho Slice A.

### Tasks
- implement explicit review / approval gate contract
- materialize contract trong workspace
- giữ repo/workspace boundary đúng
- thêm targeted tests đúng scope

### Outputs
- Slice A implementation delta
- tests và README alignment liên quan

### Validation
- contract explicit, bounded, file-based, traceable
- không có scope creep sang approval UI, recovery engine, routing/provider

### Exit criteria
- Slice A implementation đủ để đi vào verification pass

## Phase 3 — Verification and consolidation

### Purpose
Xác minh Slice A đúng scope và đủ coherent cho `v1.0`.

### Tasks
- slice verification
- integration review
- consolidation decision

### Outputs
- verification outcome
- `ATP_v1_0_Integration_Review.md`
- `ATP_v1_0_Consolidation_Decision.md`

### Validation
- contract shape đúng
- traceability đúng
- docs/README aligned
- không có blocker nền tảng

### Exit criteria
- baseline `v1.0` được coi là consolidated

## Phase 4 — Freeze-readiness and close-out path

### Purpose
Đưa baseline đã consolidate vào freeze path chuẩn ATP.

### Tasks
- freeze-readiness assessment
- freeze decision
- freeze close-out

### Outputs
- readiness reports
- freeze decision
- close-out docs

### Validation
- evidence chain đầy đủ
- roadmap/governance/docs không mâu thuẫn nhau
- không có blocker boundary hoặc continuity

### Exit criteria
- `v1.0` đủ điều kiện merge/tag khi có human approval

## 5. Slice-to-phase mapping

### Slice A — Review / Approval Gate Contract
Đi qua chủ yếu:

- Phase 1
- Phase 2
- Phase 3
- Phase 4

## 6. Control gates

## Gate G0 — Planning gate

Điều kiện qua gate:

- `ATP_v1_0_Roadmap.md` sạch
- `ATP_v1_0_Milestone_Proposal.md` sạch
- `ATP_v1_0_Execution_Plan.md` sạch
- Slice A được xác định rõ là first execution slice

## Gate G1 — Slice planning gate

Điều kiện qua gate:

- Slice A execution plan, gate contract, traceability model, acceptance criteria, và review checklist đã có
- bundle Slice A không mâu thuẫn với roadmap/proposal/plan baseline

## Gate G2 — Implementation gate

Điều kiện qua gate:

- implementation chỉ harden review / approval gate contract
- có targeted tests và README alignment
- không có scope creep

## Gate G3 — Consolidation gate

Điều kiện qua gate:

- integration review kết luận coherent
- consolidation decision chấp nhận baseline
- không có blocker nền tảng

## Gate G4 — Freeze gate

Điều kiện qua gate:

- freeze-readiness assessment sạch
- freeze decision rõ
- close-out chain đủ để support merge/tag khi có human approval

## 7. Validation strategy

Validation của `v1.0` phải đi theo thứ tự:

1. planning coherence
2. slice boundary correctness
3. contract traceability correctness
4. consolidation coherence
5. freeze-readiness evidence

`v1.0` không được coi là complete nếu chỉ có planning mà không có verification/consolidation/freeze chain tương ứng.

## 8. Immediate next step

Bước kế tiếp ngay sau execution plan này là:

- hoàn tất bundle Slice A supporting docs

Khi Slice A đã được implement, bundle này phải được rà và normalize lại thành supporting-doc set bounded trước khi đi vào integration review / consolidation pass.
