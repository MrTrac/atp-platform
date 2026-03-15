# Resolution

`core/resolution` chứa resolution boundary của ATP.

Phạm vi hiện hành:

- file-based product resolution cho `ATP` và `TDF`
- load registry entry, product profile, và policy refs tối thiểu
- build explicit v0.5 Slice A `request-to-product` resolution contract
- build explicit v0.5 Slice B `resolution-to-handoff intent` contract
- build explicit v0.5 Slice C `product execution preparation` contract
- build explicit v0.5 Slice D `product execution result` contract
- build explicit v0.6 Slice A `post-execution decision` contract
- build explicit v0.6 Slice B `decision-to-closure / continuation handoff` contract
- build explicit v0.6 Slice C `closure / continuation state` contract
- build explicit v0.7 Slice A `finalization / closure record` contract
- build explicit v1.0 Slice A `review / approval gate` contract
- build explicit v1.0 Slice B `gate outcome / operational follow-up` contract

Resolution boundary này phải giữ rõ separation với:

- classification
- routing
- provider selection
- broader product-portfolio orchestration

Nguồn resolve:

- product registry trong `registry/products`
- product profile trong `profiles/<product>/profile.yaml`
- policy registry seed trong `registry/policies`

Kết quả hiện hành gồm hai lớp:

- legacy resolution payload dùng cho flow hiện có
- request-to-product resolution contract với:
  - `product_target`
  - `capability_target`
  - `resolution_rationale`
  - `resolution_scope`
  - `traceability`
- resolution-to-handoff intent contract với:
  - `request_to_product_resolution_ref`
  - `handoff_intent`
  - `handoff_rationale`
  - `handoff_scope`
  - `traceability`
- product execution preparation contract với:
  - `request_to_product_resolution_ref`
  - `resolution_to_handoff_intent_ref`
  - `execution_preparation`
  - `preparation_rationale`
  - `preparation_scope`
  - `traceability`
- product execution result contract với:
  - `request_to_product_resolution_ref`
  - `resolution_to_handoff_intent_ref`
  - `product_execution_preparation_ref`
  - `execution_result`
  - `result_summary`
  - `result_scope`
  - `traceability`
- post-execution decision contract với:
  - `request_to_product_resolution_ref`
  - `resolution_to_handoff_intent_ref`
  - `product_execution_preparation_ref`
  - `product_execution_result_ref`
  - `post_execution_decision`
  - `decision_rationale`
  - `decision_scope`
  - `traceability`
- decision-to-closure / continuation handoff contract với:
  - `request_to_product_resolution_ref`
  - `resolution_to_handoff_intent_ref`
  - `product_execution_preparation_ref`
  - `product_execution_result_ref`
  - `post_execution_decision_ref`
  - `closure_or_continuation_handoff`
  - `handoff_rationale`
  - `handoff_scope`
  - `traceability`
- closure / continuation state contract với:
  - `request_to_product_resolution_ref`
  - `resolution_to_handoff_intent_ref`
  - `product_execution_preparation_ref`
  - `product_execution_result_ref`
  - `post_execution_decision_ref`
  - `decision_to_closure_continuation_handoff_ref`
  - `closure_or_continuation_state`
  - `state_rationale`
  - `state_scope`
  - `traceability`
- finalization / closure record contract với:
  - `product_execution_result_ref`
  - `post_execution_decision_ref`
  - `decision_to_closure_continuation_handoff_ref`
  - `closure_continuation_state_ref`
  - `finalization_or_closure_record`
  - `record_rationale`
  - `record_scope`
  - `traceability`
- review / approval gate contract với:
  - `product_execution_result_ref`
  - `post_execution_decision_ref`
  - `decision_to_closure_continuation_handoff_ref`
  - `closure_continuation_state_ref`
  - `finalization_closure_record_ref`
  - `review_or_approval_gate`
  - `gate_rationale`
  - `gate_scope`
  - `traceability`
- gate outcome / operational follow-up contract với:
  - `finalization_closure_record_ref`
  - `review_approval_gate_ref`
  - `gate_outcome_or_operational_followup`
  - `followup_rationale`
  - `followup_scope`
  - `traceability`

Deferred rõ ràng:

- context packaging
- routing
- execution
- approval UI
- recovery execution
- product portfolio orchestration
