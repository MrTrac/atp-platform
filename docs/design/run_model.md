# Mô hình run

`run model` đại diện cho một lần ATP orchestration.

Trong ATP v0 hiện tại, run model đã đủ để thể hiện full repo-local flow đến M8.

## Các trường run tối thiểu

- `run_id`
- `request_id`
- `state`
- `current_stage`
- `created_at`
- `updated_at`

## Thông tin mà run có thể mang theo

- `product`
- `resolution`
- `context_package`
- `routing`
- `execution`
- `artifacts`
- `validation`
- `review`
- `approval`
- `finalization`
- `close_or_continue`
- `latest_transition`

## Trạng thái run trong ATP v0

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `RESOLVED`
- `CONTEXT_PACKAGED`
- `ROUTED`
- `EXECUTED`
- `VALIDATED`
- `REVIEWED`
- `APPROVED`
- `FINALIZED`
- `CLOSED`
- `CONTINUE_PENDING`
- `FAILED`

## `close_or_continue` trong M8

Phân biệt tối thiểu:

- `close`
- `continue_pending`
- `close_rejected`

## Ghi chú

Run model trong ATP v0 vẫn thiên về summary và state representation; chưa phải runtime model có persistence-backed đầy đủ ở mức production.
