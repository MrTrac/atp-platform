# Core

`core/` chứa implementation repo-local cho ATP v0 theo flow đã freeze đến M8.

Phạm vi hiện hành:

- request intake
- normalize
- rule-based classification
- product resolution
- context packaging
- routing preparation và route selection
- execution orchestration
- validation, review, approval, handoff, finalization
- run state transitions cho preview flow
- exchange boundary, continuation, và traceability semantics tối thiểu đã được thêm ở baseline v0.3

Phần vẫn deferred có chủ đích:

- production persistence hoặc current-task persistence contract rộng hơn
- approval UI
- remote orchestration plane đầy đủ
- scheduling / queueing
- production artifact lifecycle engine hoàn chỉnh

Nguyên tắc:

- provider-agnostic
- adapter-first
- artifact-centric
- human-gated
- local-first but node-portable
