# Run Model

Run model dai dien cho mot lan ATP orchestration. Trong M1-M2, run model chi can du de bieu dien trang thai som cua flow.

Run fields toi thieu:

- `run_id`
- `request_id`
- `state`
- `current_stage`
- `created_at`
- `updated_at`

Transition record toi thieu:

- `run_id`
- `from_state`
- `to_state`
- `stage`
- `detail`
- `recorded_at`

State duoc khoa cho early stages:

- `RECEIVED`
- `NORMALIZED`
- `CLASSIFIED`
- `FAILED`

M1-M2 khong co persistence, lock manager, queueing, retry, hay orchestration side effects.
