# ATP v1.0 Slice B Follow-up Contract

## 1. Follow-up definition

`Gate Outcome / Operational Follow-up Contract` là contract operational hẹp dùng để ghi nhận một operational follow-up explicit sau `Review / Approval Gate Contract` của `v1.0 Slice A`.

Follow-up này không phải approval UI, không phải workflow engine, và không phải recovery engine. Nó chỉ là contract file-based để ATP ghi:

- gate decision nào đã tồn tại
- finalization record nào đang được kế thừa
- bounded operational follow-up nào đang được xác nhận
- continuity signal nào được phát sinh ở mức record semantics

## 2. Follow-up purpose

Follow-up này tồn tại để:

- biến post-gate outcome từ ngầm hiểu thành explicit contract
- tăng operational clarity sau `review / approval gate`
- tạo một operational record layer rõ hơn trước khi nghĩ tới các horizon rộng hơn của `v1`

## 3. Vì sao follow-up này cần xuất hiện sau Slice A

Sau Slice A, ATP đã có:

- review / approval gate bounded
- gate decision semantics rõ
- resulting direction ở mức gate semantics

Điều còn thiếu là một operational follow-up layer để ghi nhận:

- gate decision đang dẫn tới follow-up nào
- follow-up đó đang xác nhận readiness / closure / pending / defer ở mức bounded ra sao
- follow-up đó đang nối continuity ra sao

Nếu thiếu lớp này, Slice A vẫn là gate contract tốt, nhưng ATP chưa có một post-gate operational record đủ rõ để mở rộng operational maturity theo từng step nhỏ.

## 4. Lifecycle placement

Follow-up này nằm ngay sau:

- `review / approval gate` của `v1.0 Slice A`

Placement logic:

1. `v0.7.0` chốt lifecycle tới mức `finalization / closure record`.
2. `v1.0 Slice A` thêm `review / approval gate`.
3. `v1.0 Slice B` ghi bounded operational follow-up phát sinh từ gate đó.

Follow-up này không thay thế gate. Nó dùng gate như continuity anchor trực tiếp.

Trong implementation hiện tại, artifact runtime tương ứng là:

- `SOURCE_DEV/workspace/atp-runs/<run-id>/manifests/gate-outcome-operational-followup-contract.json`

## 5. Pre-follow-up state

Pre-follow-up state tối thiểu phải có:

- `finalization / closure record` đã tồn tại
- `review / approval gate` đã tồn tại
- gate decision đã trace được về:
  - finalization record
  - closure / continuation state
  - prior `v0.6` and `v0.5` chain khi cần

Pre-follow-up state không yêu cầu:

- approval UI
- workflow queue
- recovery execution
- provider routing state mới
- orchestration breadth mới

## 6. Follow-up inputs

Follow-up inputs tối thiểu trong Slice B gồm:

- reference tới `finalization / closure record`
- reference tới `review / approval gate`
- gate decision
- gate status
- resulting direction
- rationale state kế thừa từ gate

## 7. Follow-up subject

Follow-up subject là phần mà ATP đang ghi lại sau gate ở mức operational continuity hẹp.

Ở Slice B, follow-up subject được giữ hẹp:

- gate outcome nào đã được xác nhận
- follow-up status nào đang đúng
- continuity signal nào đang phát sinh từ gate
- close-or-continue semantics nào đang được giữ tiếp

Follow-up này không review:

- UI behavior
- workflow assignment
- recovery action execution
- routing quality
- provider arbitration quality
- orchestration breadth

## 8. Bounded follow-up semantics

Slice B chuẩn hóa các bounded follow-up semantics sau:

- `approved_operational_followup`
- `rejected_operational_followup`
- `held_operational_followup`
- `deferred_operational_followup`

Ý nghĩa bounded:

- `approved_operational_followup`: ATP ghi follow-up xác nhận gate đã pass và approved continuation đã sẵn sàng ở mức record semantics
- `rejected_operational_followup`: ATP ghi follow-up xác nhận gate đã reject và rejected closure đã được xác nhận ở mức record semantics
- `held_operational_followup`: ATP ghi follow-up xác nhận gate đang hold và follow-up vẫn pending review ở mức record semantics
- `deferred_operational_followup`: ATP ghi follow-up xác nhận gate decision đang deferred và continuity chưa nên đi xa hơn ở mức record semantics

Các semantics này chỉ là follow-up record semantics, không phải workflow action model.

Trong implementation hiện tại:

- `approved` -> `bounded_followup = approved_operational_followup` -> `followup_status = operationally_ready` -> `continuity_signal = approved_continuation_available`
- `rejected` -> `bounded_followup = rejected_operational_followup` -> `followup_status = operationally_closed` -> `continuity_signal = rejected_closure_confirmed`
- `hold` -> `bounded_followup = held_operational_followup` -> `followup_status = operationally_pending` -> `continuity_signal = followup_pending_review`
- `deferred` -> `bounded_followup = deferred_operational_followup` -> `followup_status = operationally_deferred` -> `continuity_signal = followup_deferred`

## 9. Post-follow-up outputs / resulting state

Sau follow-up, ATP phải ghi tối thiểu:

- bounded follow-up đã chọn
- follow-up status đã chọn
- continuity signal đã chọn
- follow-up rationale tóm tắt
- continuity references đã dùng

Post-follow-up outputs không đồng nghĩa với:

- thực thi recovery
- tạo workflow step mới
- điều phối provider
- mở orchestration engine

## 10. Required evidence tối thiểu

Follow-up này phải có tối thiểu:

- reference tới `finalization / closure record`
- reference tới `review / approval gate`
- `review_decision_id`
- `approval_id`
- follow-up rationale summary
- continuity mapping về `close_or_continue`

Evidence tối thiểu phải đủ để một reviewer biết:

- follow-up đang kế thừa gate nào
- follow-up đang xác nhận điều gì
- vì sao follow-up đó hợp lệ trong boundary hiện tại

## 11. Follow-up ownership / decision recording expectations

Follow-up này yêu cầu:

- gate outcome không được tồn tại như implicit consequence
- follow-up phải được ghi lại dưới dạng có traceability
- references về gate và finalization record phải explicit

Slice B chưa yêu cầu:

- operator UI
- multi-actor workflow
- queue subsystem
- operational executor cho follow-up

Trong implementation hiện tại, tối thiểu các trace anchors phải tồn tại:

- `review_approval_gate_contract_id`
- `finalization_closure_record_contract_id`
- `review_decision_id`
- `approval_id`
- `close_or_continue`

## 12. Quan hệ với freeze / close-out / continuation logic

Follow-up này có quan hệ như sau:

- với `freeze`: follow-up không thay thế freeze gate; nó là operational record layer trong `v1.0 Slice B`
- với `close-out`: follow-up phải trace được tới gate decision và finalization baseline đã close-out ở `v1.0.0 Slice A`
- với `continuation logic`: follow-up có thể xác nhận continuity signal ở mức record semantics, nhưng không tự triển khai recovery hay continuation engine

## 13. Explicit non-goals / boundary guardrails

Follow-up này không làm:

- approval UI
- workflow engine
- recovery execution
- routing
- provider selection
- provider arbitration
- topology-aware orchestration
- distributed control
- generalized orchestration

## 14. Những gì follow-up này không làm

Follow-up này không:

- hiển thị UI cho reviewer
- chạy workflow nhiều bước
- tạo job queue hay approval queue
- tự thực hiện continuation hoặc recovery action
- thay thế `review / approval gate`
- thay thế `finalization / closure record`

## 15. Contract shape tối thiểu

Contract runtime hiện tại được hiểu ở mức shape như sau:

- `contract_id`
- `contract_version`
- `request_id`
- `run_id`
- `followup_scope`
- `finalization_closure_record_ref`
- `review_approval_gate_ref`
- `gate_outcome_or_operational_followup`
- `followup_rationale`
- `traceability`
- `notes`

`followup_scope` hiện tại phải là:

- `gate_outcome_operational_followup_only`

## 16. Kết luận contract

Trong phạm vi Slice B, `Gate Outcome / Operational Follow-up Contract` phải được hiểu là:

- một operational follow-up contract hẹp
- đứng sau `review / approval gate`
- dùng để ghi post-gate outcome semantics có traceability
- là bước hardening kế tiếp của `v1` operational maturity, không phải workflow subsystem
