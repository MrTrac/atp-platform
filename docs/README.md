# Tài liệu ATP

- **Mục đích:** Cây tài liệu authoritative cho ATP; nguồn sự thật duy nhất cho kiến trúc, thiết kế, vận hành, governance.
- **Phạm vi:** Toàn bộ tài liệu dưới `docs/`, bao gồm active docs, frozen snapshot packs, và archive.
- **Trạng thái:** Active.

## Bản đồ tài liệu (Documentation Map)

| Miền | Mục đích | Active / Frozen / Archived |
|------|----------|----------------------------|
| `architecture/` | Kiến trúc, overview, flow, ranh giới repo; freeze records; snapshot bundles | Active + Frozen bundles |
| `design/` | Model thiết kế (artifact, handoff, registry, request, run); naming conventions | Active |
| `operators/` | Bootstrap, runbook, workspace layout, ATP-side AI_OS thin integration | Active |
| `decisions/` | Chỉ mục decision records; authority path tới freeze artifact | Active |
| `governance/` | Framework, Git, documentation, coding, release, AI collaboration | Active |
| `roadmap/` | Product roadmap, stage roadmap, major roadmap, version roadmap, và inheritance rules | Active |
| `execution/` | ATP project-instance execution plan layer: roadmap execution + prompt-cmd feature programs | Active |
| `archive/` | Tài liệu lịch sử; seed bundle; bản sao cũ không còn authority | Archived (không phải source of truth) |

## Đọc gì trước

1. **Mới vào dự án:** `architecture/overview.md` → `design/artifact_model.md` → `operators/local_bootstrap.md`
2. **Vận hành:** `operators/runbook_atp_v0.md` → `operators/workspace_layout.md`
   ATP-side AI_OS bridge: `operators/ai_os_thin_integration.md`
3. **Governance:** `governance/README.md` → `governance/framework/Contextual_Project_Governance_Framework.md` → `governance/ATP_3_Role_Workflow.md` khi phase dùng workflow Multi-AI
   Rule execution baseline: `governance/ATP_Development_Ruleset.md`
   Global Git branch guard runtime: `governance/Global_Safe_Git_Branch_Guard_Rule.md`
   Global shorthand / alias reference: `governance/reference/ATP_Global_Shorthand_and_Alias_Rules.md`
   Lineage continuity rule: `governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
4. **Freeze / baseline:** `architecture/ATP_MVP_v0_Freeze_Decision_Record.md` và snapshot bundles trong `architecture/`
5. **Historical close-out:** các freeze close-out reports trong `archive/reports/`
6. **Roadmap continuity:** `roadmap/README.md` và các roadmap documents theo product/major/version
   Practical lineage map: `roadmap/stages/ATP_Practical_Milestone_Map.md`
   Milestone templates: `roadmap/templates/milestones/`
7. **Execution planning hiện hành:** `execution/v1_3/ROADMAP_EXECUTION.md` → `execution/v1_3/PROMPT_CMD/INDEX.md`
   Completed baseline v1.2: `execution/v1_2/ROADMAP_EXECUTION.md` → `execution/v1_2/PROMPT_CMD/INDEX.md`
   Completed baseline v1.1: `execution/ROADMAP_EXECUTION.md` → `execution/PROMPT_CMD/INDEX.md`
   v1.3 freeze close-out artifact: `archive/reports/ATP_v1_3_Freeze_Closeout.md`

Roadmap continuity phải luôn bám trục vận hành `requested user ⇄ ATP ⇄ products`, không chỉ bám release chronology.

## Tài liệu liên quan

- `AGENTS.md` — hướng dẫn AI agents cho repo
- `operators/ai_os_thin_integration.md` — ATP-side bridge surface và verifier hooks cho AI_OS
- Snapshot bundles: `architecture/ATP_v0_final_snapshot_docs/`, `architecture/ATP_v0_1_hardening_snapshot_docs/` (Frozen)
- Freeze close-out reports: `archive/reports/ATP_v0_2_0_Freeze_Closeout.md`, `archive/reports/ATP_v0_3_0_Freeze_Closeout.md`, `archive/reports/ATP_v0_4_0_Freeze_Closeout.md`
- Current close-out / freeze artifact for execution generation v1.3: `archive/reports/ATP_v1_3_Freeze_Closeout.md`
- Roadmap layer: `roadmap/ATP_Product_Roadmap.md`, `roadmap/majors/`, `roadmap/versions/`
- Stage roadmap: `roadmap/stages/ATP_Development_Stage_Roadmap.md`
- Practical milestone map: `roadmap/stages/ATP_Practical_Milestone_Map.md`
- Milestone template bundle: `roadmap/templates/milestones/`
- Execution-plan instance layer:
  - Current generation v1.3: `execution/v1_3/ROADMAP_EXECUTION.md`, `execution/v1_3/PROMPT_CMD/`
  - Completed baseline v1.2: `execution/v1_2/ROADMAP_EXECUTION.md`, `execution/v1_2/PROMPT_CMD/`
  - Completed baseline v1.1: `execution/ROADMAP_EXECUTION.md`, `execution/EXECUTION_MODEL_SOURCE.md`, `execution/PROMPT_CMD/`

---

## Cấu trúc chi tiết

- `architecture/` — tài liệu kiến trúc hiện hành, freeze records, và snapshot bundle có authority rõ ràng
- `design/` — model mức thiết kế, vocabulary ổn định, quy ước đặt tên
- `operators/` — bootstrap, runbook, hướng dẫn vận hành repo-local
- `decisions/` — chỉ mục cho decision records ngoài các mốc freeze chính
- `governance/` — governance framework và các bundle đang có hiệu lực
- `roadmap/` — roadmap layer cho product, major family, và version planning/inheritance
- `execution/` — execution-plan instance layers cho ATP theo AI_OS canonical execution model; v1.1 và v1.2 retained as completed baselines, v1.3 là generation hiện hành
- `archive/` — tài liệu lịch sử hoặc bản sao cũ đã bị thay thế về authority path (không phải nguồn chuẩn hiện hành)

## Quy tắc authority và placement

- Snapshot kiến trúc của ATP phải đặt dưới `docs/architecture/`
- Governance document phải đặt dưới `docs/governance/` theo đúng domain
- Bản sao top-level hoặc bundle cũ không còn là authority path phải chuyển sang `docs/archive/`
- Không tạo vocabulary top-level mới nếu chưa có decision rõ ràng

## Chuẩn biên tập tài liệu hiện hành

- viết bằng tiếng Việt Unicode có dấu rõ ràng
- giữ các English technical terms cần thiết ở nguyên dạng khi điều đó giúp chính xác hơn
- phản ánh đúng active baseline và frozen baselines hiện có; không dùng future tense cho phần đã freeze hoặc đã được consolidation xác nhận
- self-review ít nhất 2 pass trước khi coi là hoàn tất
- dùng terminology ổn định: `artifact`, `authoritative`, `approval gate`, `finalization`, `evidence bundle`, `exchange bundle`, `manifest reference`
