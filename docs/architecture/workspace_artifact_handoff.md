# Handoff artifact sang workspace

- **Mục đích:** Tóm tắt handoff artifact sang workspace; source vs runtime.
- **Phạm vi:** ATP v0; bốn cơ chế handoff.
- **Trạng thái:** Active.
- **Tài liệu chi tiết:** `ATP_Workspace_Artifact_Handoff_Model.md` (reference freeze).

ATP tách rõ `source` và `runtime`:

- source code nằm ở `platforms/ATP`
- runtime artifact thuộc `SOURCE_DEV/workspace`

## Các cơ chế handoff trong ATP v0

ATP v0 dùng bốn cơ chế handoff ổn định:

- `inline_context`
- `evidence_bundle`
- `exchange_bundle`
- `manifest_reference`

## Trạng thái đang có trong M8

Trong baseline hiện tại:

- handoff được tạo ở dạng summary dict-based
- `finalization` chỉ ra các handoff reference phù hợp cho bước tiếp theo
- ATP chưa materialize đầy đủ runtime artifact vào `SOURCE_DEV/workspace`
- ATP chưa có transport hoặc handoff engine ở mức production

## Ý nghĩa kiến trúc

ATP đã chốt đúng hình thái handoff về mặt kiến trúc và vocabulary. Phần còn deferred là persistence, transport, và workspace materialization ở mức vận hành production-grade.
