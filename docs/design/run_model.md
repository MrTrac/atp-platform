# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M5, run model du de the hien intake, classification, resolution, context packaging, va routing.

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
- `latest_transition`

State duoc khoa cho giai doan hien tai:

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `RESOLVED`
- `CONTEXT_PACKAGED`
- `ROUTED`
- `FAILED`

`routing` trong M5 co the chua summary nhe cua:

- required capabilities
- candidate providers
- candidate nodes
- selected provider
- selected node
- reason codes

Transition record van giu nhe, khong persistence, khong queue, khong retry.
