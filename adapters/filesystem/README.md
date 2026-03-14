# Filesystem

Filesystem adapters hỗ trợ ATP-side artifact shaping và runtime materialization tối thiểu.

Phạm vi hiện hành:

- shape exchange bundle summary
- tạo artifact-like dict cho execution output
- gán artifact state như `raw`, `filtered`, `selected`, `authoritative`, `deprecated`
- materialize run tree tối thiểu của ATP v0.2 dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- materialize handoff outputs tối thiểu trong `handoff/` của run tree
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
