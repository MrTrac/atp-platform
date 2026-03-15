# ATP v1.0 Slice C Continuity State Contract

## 1. Continuity state definition

`Operational Continuity / Gate Follow-up State Contract` là contract operational hẹp dùng để ghi nhận một continuity state explicit sau `Gate Outcome / Operational Follow-up Contract` của `v1.0 Slice B`.

State này không phải approval UI, không phải workflow engine, không phải recovery engine, và không phải broader orchestration system. Nó chỉ là contract file-based để ATP ghi:

- finalization record nào đang được kế thừa
- gate nào và follow-up nào đã đi trước
- continuity state nào đang đúng sau follow-up
- continuity signal nào đang được giữ ở mức bounded

## 2. Continuity state purpose

State này tồn tại để:

- biến post-follow-up continuity từ ngầm hiểu thành explicit contract
- tăng operational clarity sau Slice B
- tạo một continuity state layer rõ hơn trước khi nghĩ tới các horizon operational rộng hơn của `v1`

## 3. Vì sao continuity state này cần xuất hiện sau Slice B

Sau Slice B, ATP đã có:

- `review / approval gate`
- `gate outcome / operational follow-up`
- bounded follow-up semantics và continuity signal ở mức follow-up record

Điều còn thiếu là một continuity state layer để ghi nhận:

- follow-up đang dẫn ATP tới continuity state nào
- continuity state đó đang là `ready`, `closed`, `pending`, hay `deferred` ở mức bounded
- continuity state đó đang giữ `close_or_continue` semantics ra sao

Nếu thiếu lớp này, Slice B vẫn là follow-up contract tốt, nhưng ATP chưa có một post-follow-up state contract đủ rõ để đóng continuity layer tiếp theo.

## 4. Lifecycle placement

State này nằm ngay sau:

- `Gate Outcome / Operational Follow-up Contract` của `v1.0 Slice B`

Placement logic:

1. `v0.7.0` chốt lifecycle tới mức `finalization / closure record`.
2. `v1.0 Slice A` thêm `review / approval gate`.
3. `v1.0 Slice B` ghi bounded operational follow-up phát sinh từ gate.
4. `v1.0 Slice C` ghi bounded operational continuity state phát sinh sau follow-up đó.

State này không thay thế gate hay follow-up. Nó dùng Slice B follow-up như continuity anchor trực tiếp.

Trong implementation hiện tại, artifact runtime tương ứng là:

- `SOURCE_DEV/workspace/atp-runs/<run-id>/manifests/operational-continuity-gate-followup-state-contract.json`

## 5. Pre-state inputs

Pre-state inputs tối thiểu phải có:

- `finalization / closure record`
- `review / approval gate`
- `gate outcome / operational follow-up`

Pre-state inputs không yêu cầu:

- approval UI
- workflow queue
- recovery execution
- provider routing state mới
- orchestration breadth mới

## 6. Continuity state inputs

State inputs tối thiểu trong Slice C gồm:

- reference tới `finalization / closure record`
- reference tới `review / approval gate`
- reference tới `gate outcome / operational follow-up`
- `bounded_followup`
- `followup_status`
- `continuity_signal`
- `close_or_continue`
- rationale state kế thừa từ follow-up

## 7. State subject

State subject là phần mà ATP đang ghi lại sau follow-up ở mức bounded operational continuity.

Ở Slice C, state subject được giữ hẹp:

- continuity state nào đã được xác nhận sau follow-up
- state status nào đang đúng
- continuity signal nào đang được giữ tiếp
- `close_or_continue` semantics nào vẫn đang được kế thừa

State này không review:

- UI behavior
- workflow assignment
- recovery action execution
- routing quality
- provider arbitration quality
- orchestration breadth

## 8. Bounded state semantics

Slice C chuẩn hóa các bounded state semantics sau:

- `approved_continuity_ready`
- `rejected_continuity_closed`
- `held_continuity_pending`
- `deferred_continuity_deferred`

Ý nghĩa bounded:

- `approved_continuity_ready`: ATP ghi continuity state xác nhận approved path đã ở trạng thái continuity-ready
- `rejected_continuity_closed`: ATP ghi continuity state xác nhận rejected path đã ở trạng thái continuity-closed
- `held_continuity_pending`: ATP ghi continuity state xác nhận held path vẫn đang continuity-pending
- `deferred_continuity_deferred`: ATP ghi continuity state xác nhận deferred path vẫn continuity-deferred

Các semantics này chỉ là continuity state record semantics, không phải workflow action model.

Trong implementation hiện tại:

- `approved_operational_followup` -> `continuity_state = approved_continuity_ready` -> `state_status = continuity_ready`
- `rejected_operational_followup` -> `continuity_state = rejected_continuity_closed` -> `state_status = continuity_closed`
- `held_operational_followup` -> `continuity_state = held_continuity_pending` -> `state_status = continuity_pending`
- `deferred_operational_followup` -> `continuity_state = deferred_continuity_deferred` -> `state_status = continuity_deferred`

`continuity_signal` và `close_or_continue` được kế thừa từ Slice B follow-up thay vì được tính như workflow engine mới.

## 9. Post-state outputs / resulting continuity state

Sau state này, ATP phải ghi tối thiểu:

- `continuity_state`
- `state_status`
- `continuity_signal`
- `close_or_continue`
- `state_rationale` tóm tắt
- continuity references đã dùng

Post-state outputs không đồng nghĩa với:

- thực thi recovery
- mở workflow step mới
- điều phối provider
- mở orchestration engine

## 10. Required evidence tối thiểu

State này phải có tối thiểu:

- reference tới `finalization / closure record`
- reference tới `review / approval gate`
- reference tới `gate outcome / operational follow-up`
- `review_decision_id`
- `approval_id`
- state rationale summary
- continuity mapping về `close_or_continue`

Evidence tối thiểu phải đủ để một reviewer biết:

- state đang kế thừa follow-up nào
- state đang xác nhận continuity nào
- vì sao state đó hợp lệ trong boundary hiện tại

## 11. State ownership / decision recording expectations

State này yêu cầu:

- post-follow-up continuity không được tồn tại như implicit consequence
- continuity state phải được ghi lại dưới dạng có traceability
- references về finalization record, gate, và follow-up phải explicit

Slice C chưa yêu cầu:

- operator UI
- multi-actor workflow
- queue subsystem
- runtime executor cho recovery hay continuation

Trong implementation hiện tại, tối thiểu các trace anchors phải tồn tại:

- `finalization_closure_record_contract_id`
- `review_approval_gate_contract_id`
- `gate_outcome_operational_followup_contract_id`
- `review_decision_id`
- `approval_id`
- `close_or_continue`

## 12. Quan hệ với `final/continuation-state.json`

Slice C phải giữ tách biệt rõ với `final/continuation-state.json`.

- `operational-continuity-gate-followup-state-contract.json` là bounded state contract của `v1.0 Slice C`, nằm trong `manifests/`
- `final/continuation-state.json` tiếp tục là runtime continuity artifact sâu hơn

Slice C không thay thế `final/continuation-state.json`, cũng không cố hợp nhất hai artifact này thành một workflow state engine.

## 13. Quan hệ với freeze / close-out / continuation logic

State này có quan hệ như sau:

- với `freeze`: state không thay thế freeze gate; nó là operational state layer trong `v1.0 Slice C`
- với `close-out`: state phải trace được tới Slice B freeze baseline nếu version đi tiếp
- với `continuation logic`: state chỉ ghi continuity semantics ở mức record contract, không tự triển khai recovery hay continuation engine

## 14. Explicit non-goals / boundary guardrails

State này không làm:

- approval UI
- workflow engine
- recovery engine
- recovery execution
- routing
- provider selection
- provider arbitration
- topology-aware orchestration
- distributed control
- generalized orchestration

## 15. Những gì state này không làm

State này không:

- hiển thị UI cho reviewer
- chạy workflow nhiều bước
- tạo job queue hay approval queue
- tự thực hiện continuation hoặc recovery action
- thay thế `Review / Approval Gate Contract`
- thay thế `Gate Outcome / Operational Follow-up Contract`
- thay thế `final/continuation-state.json`

## 16. Contract shape tối thiểu

Contract runtime hiện tại được hiểu ở mức shape như sau:

```json
{
  "contract_id": "operational-continuity-gate-followup-state-<request_id>",
  "contract_version": "v1.0-slice-c",
  "request_id": "<request_id>",
  "run_id": "<run_id>",
  "state_scope": "operational_continuity_gate_followup_state_only",
  "finalization_closure_record_ref": {
    "contract_id": "...",
    "record_scope": "...",
    "bounded_path": "...",
    "final_status": "..."
  },
  "review_approval_gate_ref": {
    "contract_id": "...",
    "gate_scope": "...",
    "gate_decision": "...",
    "gate_status": "..."
  },
  "gate_outcome_operational_followup_ref": {
    "contract_id": "...",
    "followup_scope": "...",
    "bounded_followup": "...",
    "followup_status": "..."
  },
  "operational_continuity_state": {
    "state_stage": "post_gate_operational_continuity",
    "continuity_state": "...",
    "state_status": "...",
    "continuity_signal": "...",
    "close_or_continue": "..."
  },
  "state_rationale": {
    "validation_status": "...",
    "review_status": "...",
    "approval_status": "...",
    "rationale_codes": ["..."],
    "summary": "..."
  },
  "traceability": {
    "finalization_closure_record_contract_id": "...",
    "review_approval_gate_contract_id": "...",
    "gate_outcome_operational_followup_contract_id": "...",
    "review_decision_id": "...",
    "approval_id": "...",
    "close_or_continue": "..."
  },
  "notes": ["..."]
}
```

## 17. Kết luận

`Operational Continuity / Gate Follow-up State Contract` là node operational tiếp theo sau Slice B trong `v1.0`.

Nó tồn tại để:

- biến post-follow-up continuity thành explicit state contract
- giữ continuity semantics bounded
- tăng traceability của operational maturity chain
- vẫn giữ ATP tránh xa approval UI, workflow engine, recovery execution, routing/provider selection, và broader orchestration
