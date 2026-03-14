# Artifact Model

Artifact la don vi dau ra/dua vao chinh cua ATP. Trong M7, artifact model bat dau duoc dung cho execution output capture.

Artifact seed fields:

- `artifact_id`
- `request_id`
- `product`
- `artifact_type`
- `artifact_state`
- `source_stage`
- `source_ref`
- `authoritative`
- `artifact_freshness`
- `payload_summary`
- `notes`

Artifact state trong v0:

- `raw`: execution output vua duoc capture
- `filtered`: da trim xuong de phuc vu summary
- `selected`: da duoc chon cho continuity
- `authoritative`: artifact dai dien nguon su that hien tai cua run
- `deprecated`: state model-only de giu compatibility cho phase sau

Artifact capture trong M7 chi la dict-based shaping, khong co production persistence hay retention engine.
