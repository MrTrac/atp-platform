# ATP v1.0 Slice D Baseline Execution Plan

## 1. Objective

Mục tiêu của Slice D là thiết lập một baseline hoàn chỉnh cho:

`Operational Decision / State Transition Control Contract`

trong ATP `v1.0.3`, theo đúng lineage hiện tại:

`Gate`
-> `Outcome / Follow-up`
-> `Continuity State`
-> `Decision Qualification`
-> `Transition Permission / Block`
-> `Next Operational State / Move`

Baseline này phải đủ để ATP đi tiếp qua:

- docs baseline
- implementation baseline
- integration review
- consolidation decision
- freeze-readiness
- close-out
- merge readiness

## 2. Deliverable set

Slice D baseline tối thiểu phải có:

1. `ATP_v1_0_Slice_D_Decision_Transition_Control_Contract.md`
2. `ATP_v1_0_Slice_D_Transition_Matrix.md`
3. `ATP_v1_0_Slice_D_Decision_Traceability_Model.md`
4. `ATP_v1_0_Slice_D_Scope_and_NonGoals.md`
5. execution plan này

Sau docs baseline, Slice D còn phải đi qua các deliverables kế tiếp cùng pattern với Slice A/B/C:

- implementation delta nếu được mở
- targeted tests
- integration review report
- consolidation decision report
- freeze-readiness assessment
- freeze decision
- freeze close-out

## 3. Work order / execution sequence

### Step D1 — Confirm lineage and scope
- xác nhận Slice D nối trực tiếp sau Slice C
- xác nhận Slice D vẫn nằm trong `v1.0.3`
- xác nhận Slice D là control-contract slice, không phải capability expansion

### Step D2 — Build docs baseline
- viết source-of-truth contract cho Slice D
- viết transition matrix
- viết traceability model
- viết scope and non-goals
- normalize execution plan

### Step D3 — Implementation baseline
- materialize runtime contract shape theo contract doc
- bảo đảm explicit linkage tới Slice C continuity-state contract
- giữ artifact trong `SOURCE_DEV/workspace`
- không làm workflow engine hoặc recovery executor

### Step D4 — Test baseline
- bổ sung targeted tests cho:
  - contract shape
  - authority / qualification semantics
  - transition classes
  - traceability
  - workspace artifact existence
  - boundary separation

### Step D5 — Integration review
- review runtime chain sau Slice C
- review docs alignment với implementation
- xác nhận không có semantic blur sang approval UI, workflow engine, recovery execution, routing/provider, hay orchestration

### Step D6 — Consolidation decision
- kết luận Slice D baseline có coherent hay không
- kết luận có blocker thật sự hay không
- kết luận có cần mở slice tiếp theo hay không

### Step D7 — Freeze-readiness
- rà blocker vs deferred items
- rà docs/runtime/tests alignment
- xác nhận Slice D baseline có đủ readiness để freeze hay chưa

### Step D8 — Close-out and merge readiness
- ghi freeze close-out nếu readiness đạt
- xác nhận baseline ready to proceed toward integration vào `main`
- merge/tag chỉ được coi là bước sau đó và vẫn cần explicit human approval

## 4. Validation checkpoints

Các checkpoint bắt buộc trong execution path:

### Checkpoint 1 — Contract clarity
- authority model rõ
- decision classes rõ
- transition classes rõ
- advisory vs binding vs blocking không nhập nhằng

### Checkpoint 2 — Lineage continuity
- Slice D nối mượt với Slice C
- không rewrite meaning của Slice A/B/C
- không mâu thuẫn với `v1.0` roadmap

### Checkpoint 3 — Boundary discipline
- không workflow engine
- không recovery engine
- không routing/provider expansion
- không broader orchestration
- không `v1.1` drift

### Checkpoint 4 — Traceability usability
- state -> decision -> transition -> resulting state reconstruct được
- evidence sufficiency đủ cho audit-grade review

### Checkpoint 5 — Runtime fitness
- artifact path rõ
- no repo writes
- contract linkage explicit

## 5. Integration review checkpoints

Slice D chỉ nên được đưa vào integration review khi:

- docs baseline đã sạch và nhất quán
- contract semantics đã được implement ở mức tối thiểu
- tests targeted đã chứng minh được shape, linkage, traceability, và boundary discipline
- runtime artifact naming và placement không mâu thuẫn với lineage hiện tại

Integration review phải trả lời:

- Slice D có coherent không
- transition control có distinct khỏi continuity state không
- có blocker thật sự không
- có cần slice tiếp theo ngay không

## 6. Consolidation criteria

Slice D chỉ nên được coi là consolidated khi:

- contract doc là source-of-truth rõ
- transition matrix usable cho audit
- traceability model reconstruct được path
- scope/non-goals chặn được scope creep
- implementation và tests bám đúng contract
- docs hỗ trợ không tự mâu thuẫn nhau

## 7. Freeze-readiness criteria

Slice D chỉ nên được coi là freeze-ready khi:

- baseline đã coherent qua integration review và consolidation
- blocker thật sự đã được xử lý hoặc chứng minh là không tồn tại
- tests relevant pass
- docs, runtime, và traceability không drift
- không có hidden expansion sang workflow/recovery/orchestration

## 8. Close-out expectation

Close-out của Slice D phải chốt rõ:

- freeze identity
- frozen scope included
- scope not included
- validation / verification status
- governance closure statement
- follow-on direction
- deferred areas
- caution rằng merge vào `main` và tag/release vẫn cần explicit human approval

Close-out không được:

- claim merge đã xảy ra nếu chưa có evidence
- claim tag đã tồn tại nếu chưa có evidence
- kéo Slice D sang planning line khác

## 9. Definition of Done cho Slice D baseline

Slice D baseline chỉ được coi là Done khi:

- ATP có docs baseline hoàn chỉnh cho decision / transition control
- implementation baseline tồn tại và bounded
- tests targeted đủ chứng minh contract semantics
- integration review hoàn tất
- consolidation decision hoàn tất
- freeze-readiness hoàn tất
- freeze close-out hoàn tất
- baseline được coi là ready to proceed toward merge/integration khi có explicit human approval

## 10. Anti-drift execution discipline

Trong suốt execution path của Slice D, ATP phải giữ:

- không tự mở `v1.1-planning`
- không tự mở capability/platform scope mới
- không tự biến control contract thành engine design
- không dùng transition matrix như orchestration plan
- không dùng decision authority model như identity/permission subsystem rộng

## 11. Kết luận

Execution plan này giữ Slice D trong đúng vai trò:

- bounded
- lineage-consistent
- governance-grade
- implementation-ready
- review-ready

Đây là baseline plan để đưa `ATP v1.0.3 Slice D` đi hết vòng đời governance giống Slice A/B/C, không nhiều hơn và không ít hơn.
