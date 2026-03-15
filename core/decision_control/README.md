# Decision control (ATP v1.0 Slice D)

`core/decision_control` chứa runtime contract shape cho **Operational Decision / State Transition Control Contract** (Slice D, v1.0.3).

Authority runtime module hiện tại là:

- `core/decision_control/contract.py`

Compatibility layer hiện còn được giữ tại:

- `core/decision_control/slice_d_contract.py`

Compatibility file này chỉ re-export authority API để tránh làm vỡ imports cũ trong branch hiện tại. Nó không còn là authority implementation.

Phạm vi:

- Decision record shape: `record_id`, `source_state_ref`, `decision_actor`, `decision_authority`, `decision_class`, `rationale_summary`, `evidence_summary`, `requested_transition`, `decision_result`, linkage tới Slice C continuity state.
- Transition record shape: `record_id`, `source_state_ref`, `decision_record_ref`, `transition_class`, `permission_block_basis`, `resulting_state_or_move`, `status_summary`.
- Validation tối thiểu: enum constraints, required fields, traceability linkage (source state → decision → transition → resulting state).

Validation semantics hiện tại giữ thêm các guard hẹp sau:

- `source_state_ref` phải bám canonical Slice C continuity-state contract identity.
- `observational_decision` và `advisory_decision` không được tạo binding `allow`.
- `blocking_decision` phải tạo `decision_result = block`.
- `decision_record_ref` của transition phải giữ đủ traceability semantics để reconstruct `decision_class` và `decision_result`.
- `transition_class` phải align với `decision_result` ở mức contract shape.

Source-of-truth: `docs/archive/reports/ATP_v1_0_Slice_D_*.md`. Slice D không phải workflow engine, execution engine, hay approval UI — chỉ contract layer để biểu diễn và validate chain decision/transition.
