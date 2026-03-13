# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M4, run model du de the hien intake, classification, resolution, va context packaging.

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
- `latest_transition`

State duoc khoa cho giai doan hien tai:

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `RESOLVED`
- `CONTEXT_PACKAGED`
- `FAILED`

`context_package` trong M4 co the chua summary nhe cua:

- task manifest
- product context
- evidence selection
- evidence bundle

Transition record van giu nhe, khong persistence, khong queue, khong retry.
