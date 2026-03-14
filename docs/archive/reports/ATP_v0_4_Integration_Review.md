# ATP v0.4 Integration Review

## Phạm vi đã review

Pass này review baseline ATP v0.4 trên branch `v0.4-planning`, chỉ trong phạm vi Slice A-D:

- Slice A: current-task persistence contract
- Slice B: continue-pending recovery contract
- Slice C: active/supersede pointer traceability
- Slice D: read-only inspect surface

Review tập trung vào tính nhất quán giữa docs, code, tests, và runtime model thực tế; không mở slice mới, không redesign ATP, và không mở rộng sang production persistence, scheduler/queue, remote orchestration, UI, hay broad subsystem expansion.

## Cross-slice findings

### Tổng thể

Baseline Slice A-D hiện ghép thành một operational runtime model nhất quán trên nền v0.3:

- Slice A chốt current-task persistence contract ở mức file-based cho external current-task
- Slice B chốt recovery entry contract cho `continue_pending`, không thêm resume execution
- Slice C chốt active pointer và supersede traceability ở mức tối thiểu, không thêm pointer management subsystem
- Slice D chỉ thêm inspect surface read-only cho current-task artifacts đã materialize

Các lát cắt này giữ được ranh giới semantics:

- `handoff/` vẫn là run-local handoff zone
- `exchange/current-task/<run-id>/` vẫn là current-task payload root cho external boundary
- `current-task-state.json` là persistence contract, không phải state engine
- `continue-pending-recovery.json` là recovery entry contract, không phải recovery executor
- `active-pointer.json` và `supersede-trace.json` chỉ là pointer traceability, không phải registry
- `cli/inspect.py` chỉ là read-only surface, không phải operator console

### Boundary correctness

Không thấy dấu hiệu runtime state bị ghi vào ATP source repo. Runtime writes tiếp tục đi vào:

- `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- `SOURCE_DEV/workspace/exchange/current-task/`
- `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`

Inspect surface chỉ đọc từ workspace, không tạo repo-local runtime state.

### Auditability và traceability

Traceability hiện tại đủ coherent cho baseline v0.4:

- current-task persistence nối được tới `current.json`, `continuation-state.json`, `reference-index.json`
- recovery contract nối được tới Slice A current-task state và Slice B continuation state
- active pointer và supersede trace giữ được dấu vết current task hiện tại và previous current task khi có replace
- inspect surface đọc ra được current-task state, recovery contract, active pointer, và supersede trace mà không làm mờ boundary

Không thấy slice nào làm chồng lấn sai giữa finalization, handoff, exchange, authoritative projection, persistence contract, recovery contract, và pointer traceability.

## Docs / code / test alignment findings

### Mức thấp

1. Active docs drift nhỏ:
   - `docs/architecture/overview.md` mới dừng ở v0.2-v0.3, chưa mô tả baseline v0.4.
2. Test gap nhỏ:
   - inspect surface đã có test current-task cơ bản, nhưng chưa có assertion cho case latest active pointer có supersede trace.

## Vấn đề theo mức độ nghiêm trọng

### Blocking

Không có blocking gap nào được xác định trong pass này.

### Medium

Không có.

### Low

- Drift wording nhỏ ở active overview
- Thiếu một inspect test cho supersede trace path

## Những gì đã sửa ngay trong pass này

- cập nhật wording tối thiểu trong `docs/architecture/overview.md` để phản ánh baseline runtime v0.2-v0.4
- bổ sung integration test cho inspect surface ở case có supersede trace
- rà lại local README của `cli/` và `adapters/filesystem/`; không cần chỉnh thêm vì đã phản ánh đúng baseline Slice A-D

## Những gì được defer

- docs wording cleanup rộng hơn giữa `overview.md` và các design docs nếu muốn đồng bộ sâu hơn
- inspect filtering/summarization giàu hơn cho operator
- bất kỳ generalized pointer registry, persistence layer, hay recovery engine nào vượt quá v0.4

## Kết luận review

ATP v0.4 hiện đạt trạng thái baseline tích hợp nhất quán trên Slice A-D. Không thấy blocker kiến trúc hay blocker test nào ngăn việc freeze/integrate. Các điểm còn lại chỉ là deferred cleanup nhỏ, không làm thay đổi kết luận tổng thể.
