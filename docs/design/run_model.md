# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M8, run model du de the hien full ATP v0 flow.

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
- `approval`
- `finalization`
- `close_or_continue`
- `latest_transition`

State duoc khoa cho ATP v0:

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

`close_or_continue` trong M8 phan biet:

- `close`
- `continue_pending`
- `close_rejected`
