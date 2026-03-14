# Tài liệu ATP

- **Mục đích:** Cây tài liệu authoritative cho ATP; nguồn sự thật duy nhất cho kiến trúc, thiết kế, vận hành, governance.
- **Phạm vi:** Toàn bộ tài liệu dưới `docs/`, bao gồm active docs, frozen snapshot packs, và archive.
- **Trạng thái:** Active.

## Bản đồ tài liệu (Documentation Map)

| Miền | Mục đích | Active / Frozen / Archived |
|------|----------|----------------------------|
| `architecture/` | Kiến trúc, overview, flow, ranh giới repo; freeze records; snapshot bundles | Active + Frozen bundles |
| `design/` | Model thiết kế (artifact, handoff, registry, request, run); naming conventions | Active |
| `operators/` | Bootstrap, runbook, workspace layout | Active |
| `decisions/` | Chỉ mục decision records; authority path tới freeze artifact | Active |
| `governance/` | Framework, Git, documentation, coding, release, AI collaboration | Active |
| `archive/` | Tài liệu lịch sử; seed bundle; bản sao cũ không còn authority | Archived (không phải source of truth) |

## Đọc gì trước

1. **Mới vào dự án:** `architecture/overview.md` → `design/artifact_model.md` → `operators/local_bootstrap.md`
2. **Vận hành:** `operators/runbook_atp_v0.md` → `operators/workspace_layout.md`
3. **Governance:** `governance/README.md` → `governance/framework/Contextual_Project_Governance_Framework.md`
4. **Freeze / baseline:** `architecture/ATP_MVP_v0_Freeze_Decision_Record.md` và snapshot bundles trong `architecture/`

## Tài liệu liên quan

- `AGENTS.md` — hướng dẫn AI agents cho repo
- Snapshot bundles: `architecture/ATP_v0_final_snapshot_docs/`, `architecture/ATP_v0_1_hardening_snapshot_docs/` (Frozen)

---

## Cấu trúc chi tiết

- `architecture/` — tài liệu kiến trúc hiện hành, freeze records, và snapshot bundle có authority rõ ràng
- `design/` — model mức thiết kế, vocabulary ổn định, quy ước đặt tên
- `operators/` — bootstrap, runbook, hướng dẫn vận hành repo-local
- `decisions/` — chỉ mục cho decision records ngoài các mốc freeze chính
- `governance/` — governance framework và các bundle đang có hiệu lực
- `archive/` — tài liệu lịch sử hoặc bản sao cũ đã bị thay thế về authority path (không phải nguồn chuẩn hiện hành)

## Quy tắc authority và placement

- Snapshot kiến trúc của ATP phải đặt dưới `docs/architecture/`
- Governance document phải đặt dưới `docs/governance/` theo đúng domain
- Bản sao top-level hoặc bundle cũ không còn là authority path phải chuyển sang `docs/archive/`
- Không tạo vocabulary top-level mới nếu chưa có decision rõ ràng

## Chuẩn biên tập tài liệu hiện hành

- viết bằng tiếng Việt Unicode có dấu rõ ràng
- giữ các English technical terms cần thiết ở nguyên dạng khi điều đó giúp chính xác hơn
- phản ánh ATP MVP v0 như baseline đã hoàn tất đến M8, không dùng future tense cho phần đã triển khai
- self-review ít nhất 2 pass trước khi coi là hoàn tất
- dùng terminology ổn định: `artifact`, `authoritative`, `approval gate`, `finalization`, `evidence bundle`, `exchange bundle`, `manifest reference`
