# Adapters

`adapters/` chứa các adapter boundaries và helper implementations mà ATP core dùng để:

- thực thi command hoặc external path ở mức tối thiểu
- shape artifact và handoff payload
- materialize runtime state dưới `SOURCE_DEV/workspace` theo baseline đã freeze

Phạm vi hiện hành:

- execution adapters tối thiểu cho local path và placeholders có chủ đích cho remote/UI/API bridges
- contract layer nhẹ giữa core và adapter
- filesystem materialization cho baseline v0.2-v0.3

Không thuộc scope của cây này:

- orchestration engine rộng
- production persistence layer
- UI subsystem
- remote execution plane hoàn chỉnh
