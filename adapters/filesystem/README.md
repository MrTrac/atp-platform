# Filesystem

Filesystem adapters hỗ trợ ATP-side artifact shaping và runtime materialization tối thiểu.

Phạm vi hiện hành:

- shape exchange bundle summary
- tạo artifact-like dict cho execution output
- gán artifact state như `raw`, `filtered`, `selected`, `authoritative`, `deprecated`
- materialize run tree tối thiểu của ATP v0.2 dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- materialize handoff outputs tối thiểu trong `handoff/` của run tree
- materialize explicit v0.5 Slice A `request-to-product` resolution contract riêng với legacy `resolution.json`
- materialize explicit v0.5 Slice B `resolution-to-handoff-intent` contract riêng với Slice A contract
- materialize explicit v0.5 Slice C `product-execution-preparation` contract riêng với Slice A-B contracts
- materialize explicit v0.5 Slice D `product-execution-result` contract riêng với Slice A-C contracts
- materialize explicit v0.6 Slice A `post-execution-decision` contract riêng với Slice A-D chain
- materialize explicit v0.6 Slice B `decision-to-closure-continuation-handoff` contract riêng với Slice A-D và v0.6 Slice A chain
- materialize explicit v0.6 Slice C `closure-continuation-state` contract riêng với v0.6 Slice A-B chain
- materialize explicit v0.7 Slice A `finalization-closure-record` contract riêng với v0.6 closure chain
- materialize explicit v1.0 Slice A `review-approval-gate` contract riêng với v0.7 finalization chain
- materialize explicit v1.0 Slice B `gate-outcome-operational-followup` contract riêng với v1.0 gate chain
- materialize explicit v1.0 Slice C `operational-continuity-gate-followup-state` contract riêng với v1.0 follow-up chain
- project authoritative artifacts tối thiểu sang `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- ghi retention / cleanup semantics tối thiểu mà không auto-delete runtime artifacts
- materialize `exchange/current-task/` tối thiểu chỉ khi exchange boundary decision yêu cầu
- persist current-task state tối thiểu ở mức file-based khi exchange current-task được materialize
- ghi continue-pending recovery contract tối thiểu khi current-task ở trạng thái `continue_pending`
- ghi active pointer và supersede trace tối thiểu cho current-task ở mức traceability
- ghi continuation state tối thiểu cho `continue_pending` mà không thêm queue/scheduler subsystem
- ghi reference/index artifacts tối thiểu để trỏ current exchange, continuation, và authoritative refs

Deferred có chủ đích:

- recovery / resume execution thật
- current-task pointer management model rộng hơn
- artifact persistence thực tế ở mức production
- đầy đủ artifact lifecycle engine
- `exchange/` subsystem rộng hơn
- generalized indexing/search subsystem
- retention và cleanup engine rộng hơn
