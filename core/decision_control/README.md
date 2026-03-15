# Decision control (ATP v1.0 Slice D)

`core/decision_control` chứa runtime contract shape cho **Operational Decision / State Transition Control Contract** (Slice D, v1.0.3).

Phạm vi:

- Decision record shape: `record_id`, `source_state_ref`, `decision_actor`, `decision_authority`, `decision_class`, `rationale_summary`, `evidence_summary`, `requested_transition`, `decision_result`, linkage tới Slice C continuity state.
- Transition record shape: `record_id`, `source_state_ref`, `decision_record_ref`, `transition_class`, `permission_block_basis`, `resulting_state_or_move`, `status_summary`.
- Validation tối thiểu: enum constraints, required fields, traceability linkage (source state → decision → transition → resulting state).

Source-of-truth: `docs/archive/reports/ATP_v1_0_Slice_D_*.md`. Slice D không phải workflow engine, execution engine, hay approval UI — chỉ contract layer để biểu diễn và validate chain decision/transition.
