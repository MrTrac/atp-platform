# Finalization

`core/finalization` chứa final summary và close/continue semantics tối thiểu cho ATP v0.

Phạm vi:

- tạo finalization summary dict-based
- quyết định `close`, `continue_pending`, hoặc `close_rejected`
- làm đầu vào cho exchange boundary decision và continuation semantics ở baseline v0.3

Không thuộc scope:

- approval UI
- external finalization workflow
- production handoff / persistence orchestration
