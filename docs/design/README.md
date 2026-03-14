# Thiết kế ATP

- **Mục đích:** Model mức thiết kế, vocabulary ổn định, quy ước đặt tên cho ATP.
- **Phạm vi:** Artifact, handoff, registry, request, run; naming conventions.
- **Trạng thái:** Active.

## Tài liệu trong miền

| Tài liệu | Mục đích |
|----------|----------|
| `artifact_model.md` | Đơn vị artifact, trường seed, trạng thái |
| `ATP_Artifact_Lifecycle_Map.md` | Bản đồ lifecycle artifact cho phase runtime materialization v0.2 |
| `ATP_Runtime_Materialization_Model.md` | Mô hình runtime workspace và semantic-to-path mapping cho v0.2 |
| `ATP_Runtime_Boundary_Rules.md` | Quy tắc boundary giữa repo và workspace cho runtime materialization |
| `handoff_model.md` | Bốn cơ chế handoff: inline_context, evidence_bundle, exchange_bundle, manifest_reference |
| `registry_model.md` | Registry providers, products, capabilities |
| `request_model.md` | Model request, intake |
| `run_model.md` | Model run, lifecycle |
| `naming_conventions.md` | Quy ước đặt tên |

## Đọc gì trước

1. `artifact_model.md` — nền cho execution output và continuity
2. `handoff_model.md` — cơ chế handoff giữa các bước
3. `ATP_Runtime_Materialization_Model.md` — planning package cho phase v0.2 khi cần runtime workspace model

## Tài liệu liên quan

- `architecture/workspace_artifact_handoff.md` — tóm tắt handoff sang workspace
- `architecture/ATP_Workspace_Artifact_Handoff_Model.md` — model chi tiết (reference freeze)
