# Filesystem

Filesystem adapters trong M7-va-v0.2 ho tro ATP-side artifact shaping va runtime materialization toi thieu.

Pham vi:

- shape exchange bundle summary
- tao artifact-like dict cho execution output
- gan artifact state nhu `raw`, `filtered`, `selected`, `authoritative`, `deprecated`
- materialize run tree toi thieu cua ATP v0.2 duoi `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- materialize handoff outputs toi thieu trong `handoff/` cua run tree
- project authoritative artifact toi thieu sang `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`

Deferred:

- artifact persistence thuc te
- day du artifact lifecycle engine
- `exchange/`, retention va cleanup engine
