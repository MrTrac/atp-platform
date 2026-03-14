# Mô hình handoff

- **Mục đích:** Định nghĩa bốn cơ chế handoff trong ATP v0.
- **Phạm vi:** inline_context, evidence_bundle, exchange_bundle, manifest_reference.
- **Trạng thái:** Active.
- **Tài liệu liên quan:** `architecture/workspace_artifact_handoff.md`, `architecture/ATP_Workspace_Artifact_Handoff_Model.md`

---

ATP v0 giữ bốn handoff model cố định:

- `inline_context`
- `evidence_bundle`
- `exchange_bundle`
- `manifest_reference`

## Vai trò của từng handoff model trong ATP v0

### Inline Context
Tóm tắt các continuity fields quan trọng nhất để bước tiếp theo hiểu đúng ngữ cảnh.

### Evidence Bundle
Tập artifact được chọn cùng các authoritative refs tương ứng.

### Exchange Bundle
Summary bundle có thể dùng để giao bước tiếp theo trong flow.

### Manifest Reference
Tham chiếu ổn định đến manifest hoặc final artifact liên quan.

## Ghi chú

ATP v0 hiện chỉ hỗ trợ handoff summary theo kiểu dict-based. ATP chưa có workspace handoff engine đầy đủ ở mức production.
