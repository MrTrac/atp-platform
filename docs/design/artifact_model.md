# Mô hình artifact

- **Mục đích:** Định nghĩa đơn vị artifact, trường seed, trạng thái.
- **Phạm vi:** ATP v0; execution output capture và continuity.
- **Trạng thái:** Active.
- **Tài liệu liên quan:** `handoff_model.md`, `architecture/workspace_artifact_handoff.md`.

`artifact` là đơn vị đầu vào và đầu ra cốt lõi của ATP.

Trong ATP v0, artifact model được dùng rõ hơn từ M7 trở đi cho execution output capture và continuity.

## Các trường seed của artifact

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

## Trạng thái artifact trong ATP v0

- `raw` — execution output vừa được capture
- `filtered` — đã được trim xuống để phục vụ summary
- `selected` — đã được chọn cho continuity
- `authoritative` — artifact đại diện cho nguồn sự thật hiện tại của run
- `deprecated` — state model-only để giữ compatibility cho phase sau

## Ghi chú

Artifact capture trong ATP v0 hiện vẫn là dict-based shaping. ATP chưa có persistence hoặc retention engine đầy đủ ở mức production.
