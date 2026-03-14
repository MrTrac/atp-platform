# ATP v1.0 Slice A Gate Contract

## 1. Gate definition

`Review / Approval Gate Contract` là contract operational hẹp dùng để ghi nhận một điểm review / approval explicit sau `finalization / closure record` của `v0.7.0`.

Gate này không phải approval UI, không phải workflow engine, và không phải broad approval subsystem. Nó chỉ là contract file-based để ATP ghi:

- gate đang xét cái gì
- xét trên evidence nào
- decision semantics nào được phép ghi nhận
- resulting direction nào được phép phát sinh từ gate đó

## 2. Gate purpose

Gate này tồn tại để:

- đưa review / approval từ ngầm hiểu thành explicit contract
- tăng operational clarity trên lifecycle chain đã có của `v0`
- tạo một decision boundary rõ hơn trước khi ATP nghĩ tới các horizon rộng hơn của `v1`

## 3. Vì sao gate này cần xuất hiện sau `v0.7.0`

Sau `v0.7.0`, ATP đã có:

- finalization / closure record bounded
- lifecycle continuity rõ tới mức finalization seam đã khép

Điều còn thiếu là một operational gate layer để ghi nhận:

- một review / approval checkpoint chính thức
- checkpoint đó đang xét finalization result nào
- checkpoint đó đang cho phép, chặn, defer, hay hold điều gì ở mức bounded

Nếu thiếu lớp này, `v1` sẽ không có first operational contract đủ rõ dù `v0` đã hoàn tất family goal.

## 4. Lifecycle placement

Gate này nằm ngay sau:

- `finalization / closure record` của `v0.7.0`

Placement logic:

1. `v0.7.0` chốt lifecycle tới mức finalized closure record.
2. `v1.0` Slice A thêm một review / approval gate để operationalize decision boundary trên finalized record đó.
3. Gate này không thay thế finalization record; nó dùng finalization record như pre-gate continuity anchor.

Trong implementation hiện tại, artifact runtime tương ứng là:

- `SOURCE_DEV/workspace/atp-runs/<run-id>/manifests/review-approval-gate-contract.json`

## 5. Pre-gate state

Pre-gate state tối thiểu phải có:

- `finalization / closure record` đã tồn tại
- lifecycle continuity của run đã trace được về:
  - execution result
  - post-execution decision
  - decision-to-closure / continuation handoff
  - closure / continuation state
  - finalization / closure record

Pre-gate state không yêu cầu:

- approval UI
- recovery engine
- provider routing state mới
- orchestration breadth mới

## 6. Gate inputs

Gate inputs tối thiểu trong Slice A gồm:

- reference tới `product execution result`
- reference tới `post-execution decision`
- reference tới `decision-to-closure / continuation handoff`
- reference tới `closure / continuation state`
- reference tới `finalization / closure record`
- review decision summary
- approval result summary

## 7. Gate review subject

Gate review subject là phần mà ATP đang đưa qua bounded operational review.

Ở Slice A, review subject được giữ hẹp:

- tính đầy đủ và đúng boundary của finalization / closure record
- tính nhất quán của continuity chain dẫn tới record đó
- tính đủ của review / approval summaries tối thiểu để đưa ra một operational gate decision

Gate này không review:

- UI behavior
- routing quality
- provider arbitration quality
- recovery execution behavior
- orchestration breadth

## 8. Gate decision semantics

Slice A chuẩn hóa các decision semantics sau:

- `approved`
- `rejected`
- `deferred`
- `hold`

Ý nghĩa bounded:

- `approved`: gate chấp nhận review subject theo boundary hiện hành
- `rejected`: gate xác nhận review subject không đạt boundary hiện hành
- `deferred`: gate chưa thể quyết định vì evidence hoặc readiness chưa đủ
- `hold`: gate chủ động dừng tiếp diễn dù đã có enough review subject context, do cần chặn continuation tạm thời

Các semantics này chỉ là gate decision semantics, không phải UI action model.

Trong implementation hiện tại:

- `approved` -> `gate_status = passed` -> `resulting_direction = ready_for_approved_continuation`
- `rejected` -> `gate_status = rejected` -> `resulting_direction = ready_for_rejected_closure`
- `hold` -> `gate_status = held` -> `resulting_direction = pending_further_review`
- `deferred` -> `gate_status = deferred` -> `resulting_direction = decision_deferred`

## 9. Post-gate outputs / resulting state

Sau gate, ATP phải ghi tối thiểu:

- gate decision đã chọn
- gate status đã chọn
- gate rationale tóm tắt
- continuity references đã dùng
- resulting continuity direction ở mức bounded

Post-gate outputs không đồng nghĩa với:

- thực thi recovery
- điều phối provider
- mở workflow engine

## 10. Required evidence tối thiểu

Gate này phải có tối thiểu:

- reference tới `finalization / closure record`
- continuity references cần thiết về `v0.6`/`v0.7` chain
- `review_decision_id`
- `approval_id`
- review subject summary
- decision rationale summary

Evidence tối thiểu phải đủ để một reviewer biết:

- gate đang xét cái gì
- dựa trên bằng chứng nào
- vì sao decision hợp lệ trong boundary hiện tại

## 11. Gate ownership / decision recording expectations

Gate này yêu cầu:

- ownership của decision phải được xác định rõ ở mức contract hoặc decision record
- decision không được tồn tại như implicit outcome
- decision phải được ghi lại dưới dạng có traceability

Slice A chưa yêu cầu:

- operator UI
- multi-actor approval workflow
- approval queue subsystem

Trong implementation hiện tại, tối thiểu các trace anchors phải tồn tại:

- `finalization_closure_record_contract_id`
- `closure_continuation_state_contract_id`
- `decision_to_closure_continuation_handoff_contract_id`
- `post_execution_decision_contract_id`
- `product_execution_result_contract_id`
- `review_decision_id`
- `approval_id`
- `close_or_continue`

## 12. Quan hệ với freeze / close-out / continuation logic

Gate này có quan hệ như sau:

- với `freeze`: gate không thay thế freeze gate; nó là operational gate ở layer `v1.0` Slice A
- với `close-out`: gate decision phải trace được tới planning/consolidation/freeze chain về sau nếu version đi tiếp
- với `continuation logic`: gate có thể ảnh hưởng resulting continuity direction ở mức record semantics, nhưng không tự triển khai recovery hoặc continuation engine

## 13. Explicit non-goals / boundary guardrails

Gate này không làm:

- approval UI
- recovery engine
- recovery execution
- routing
- provider selection
- provider arbitration
- topology-aware orchestration
- distributed control
- generalized orchestration

## 14. Những gì gate này không làm

Gate này không:

- hiển thị UI cho reviewer
- chạy workflow nhiều bước
- tự quyết định provider hay route
- tự thực hiện continuation hoặc recovery action
- thay thế finalization / closure record của `v0.7.0`
- thay thế freeze decision hoặc close-out decision của version

## 15. Contract shape tối thiểu

Contract runtime hiện tại được hiểu ở mức shape như sau:

- `contract_id`
- `contract_version`
- `request_id`
- `run_id`
- `gate_scope`
- `product_execution_result_ref`
- `post_execution_decision_ref`
- `decision_to_closure_continuation_handoff_ref`
- `closure_continuation_state_ref`
- `finalization_closure_record_ref`
- `review_or_approval_gate`
- `gate_rationale`
- `traceability`
- `notes`

`gate_scope` hiện tại phải là:

- `review_approval_gate_only`

## 16. Kết luận contract

Trong phạm vi Slice A, `Review / Approval Gate Contract` phải được hiểu là:

- một operational gate contract hẹp
- đứng sau `finalization / closure record`
- dùng để ghi review / approval decision semantics có traceability
- là first operational contract của `v1`, không phải UI hay workflow subsystem
