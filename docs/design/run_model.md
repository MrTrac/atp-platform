# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M7, run model du de the hien intake, routing, execution, artifact capture, validation, va review.

Run fields toi thieu:

- `run_id`
- `request_id`
- `state`
- `current_stage`
- `created_at`
- `updated_at`

Run co the mang them thong tin seed:

- `product`
- `resolution`
- `context_package`
- `routing`
- `execution`
- `artifacts`
- `validation`
- `review`
- `latest_transition`

State duoc khoa cho giai doan hien tai:

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `RESOLVED`
- `CONTEXT_PACKAGED`
- `ROUTED`
- `EXECUTED`
- `VALIDATED`
- `REVIEWED`
- `FAILED`

Validation summary trong M7 chi la rule-based summary nhe. Review decision trong M7 chi la pre-approval preview, chua la approval workflow.
