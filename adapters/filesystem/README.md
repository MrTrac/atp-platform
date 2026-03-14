# Filesystem

Filesystem adapters trong M7-va-v0.2 ho tro ATP-side artifact shaping va runtime materialization toi thieu.

Pham vi:

- shape exchange bundle summary
- tao artifact-like dict cho execution output
- gan artifact state nhu `raw`, `filtered`, `selected`, `authoritative`, `deprecated`
- materialize run tree toi thieu cua ATP v0.2 duoi `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- materialize handoff outputs toi thieu trong `handoff/` cua run tree
- project authoritative artifact toi thieu sang `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- ghi retention / cleanup semantics toi thieu ma khong auto-delete runtime artifacts
- materialize `exchange/current-task/` toi thieu chi khi exchange boundary decision yeu cau
- ghi continuation state toi thieu cho `continue_pending` ma khong them queue/scheduler subsystem
- ghi reference/index artifact toi thieu de tro current exchange, continuation, va authoritative refs

Deferred:

- artifact persistence thuc te
- day du artifact lifecycle engine
- `exchange/` subsystem rong hon, indexing/search subsystem rong hon, retention va cleanup engine rong hon
