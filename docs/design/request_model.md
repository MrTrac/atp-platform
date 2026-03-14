# Mô hình request

`request` là input control-plane của ATP.

Trong ATP v0 hiện tại, request model là đầu vào nền cho:

- intake
- normalization
- classification
- context packaging
- routing
- execution orchestration

## Các trường top-level tối thiểu sau normalize

- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `payload`
- `metadata`

## Vai trò của request đã normalize

Request đã normalize được dùng để:

- tạo `task_manifest`
- gắn `request_id` và `product` cho các artifact/context liên quan
- làm input cho routing và execution
- giữ continuity cho các bước sau

## `task_manifest` trong v0

Task Manifest tối thiểu chứa:

- `manifest_id`
- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `required_capabilities`
- `target_scope`
- `input_artifacts`
- `notes`

## Ghi chú

ATP v0 vẫn giữ request model theo hướng nhẹ, deterministic, và file-based; chưa mở rộng sang request enrichment engine phức tạp sau routing hoặc execution.
