# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M3, run model du de the hien intake, classification, va product resolution.

Run fields toi thieu:

- `run_id`
- `request_id`
- `state`
- `current_stage`
- `created_at`
- `updated_at`

Run co the mang them thong tin seed:

- `product`
- `latest_transition`
- `resolution`

State duoc khoa cho giai doan hien tai:

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `RESOLVED`
- `FAILED`

Transition record van giu nhe, khong persistence, khong queue, khong retry.
