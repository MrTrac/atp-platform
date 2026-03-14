# Kiến trúc ATP

- **Mục đích:** Tài liệu kiến trúc, overview, flow, ranh giới; freeze records và snapshot bundles.
- **Phạm vi:** Kiến trúc ATP; doctrine active; baseline v0; hardening v0.1; tài liệu tham chiếu freeze và active architecture orientation.
- **Trạng thái:** Active (tài liệu nền); Frozen (snapshot bundles).

## Active vs Frozen vs Reference

| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| **Active** | Tài liệu nền, đọc trước; cập nhật khi kiến trúc tiến hóa | `overview.md`, `layered_architecture.md`, `orchestration_flow.md`, `repo_boundary.md`, `workspace_artifact_handoff.md` |
| **Frozen** | Snapshot bundle cố định; không sửa nội dung; baseline cho release track | `ATP_v0_final_snapshot_docs/`, `ATP_v0_1_hardening_snapshot_docs/` |
| **Reference** | Tài liệu hỗ trợ ổn định; tham chiếu khi cần chi tiết; không phải luồng đọc đầu tiên | `ATP_Workspace_Artifact_Handoff_Model.md`, `ATP_Glossary_VI.md`, `ATP_AI_Workspace_Open_Rules.md`, `ATP_Drawio_Style_Structure.md` |

Reference artifacts là tài liệu hỗ trợ ổn định, không phải luồng đọc đầu tiên. Đọc Active trước, tham chiếu khi cần chi tiết.

## Đọc gì trước

1. `overview.md` — tổng quan ATP, baseline M8
2. `layered_architecture.md` — kiến trúc phân lớp
3. `orchestration_flow.md` — flow điều phối 14 bước
4. `repo_boundary.md` — ranh giới repo và workspace
5. các freeze close-out reports trong `docs/archive/reports/` khi cần historical release closure
6. `docs/roadmap/` khi cần doctrine continuity giữa architecture, freeze history, và roadmap inheritance

Architecture doctrine active cũng là nơi neo trục vận hành `requested user ⇄ ATP ⇄ products` của ATP trước khi đi xuống roadmap hay implementation planning.

## Tài liệu liên quan

- `design/` — model thiết kế (artifact, handoff, registry, request, run)
- `operators/` — runbook, bootstrap, workspace layout
- `docs/decisions/` — chỉ mục tới freeze record
- `docs/roadmap/` — roadmap layer cho product, major, và version evolution
