# Governance ATP

- **Mục đích:** Authority path cho governance; quy tắc vận hành cho hoạt động lặp lại, rủi ro cao, đa tác nhân.
- **Phạm vi:** Git, documentation, coding, release, roadmap continuity, AI collaboration; framework và reference.
- **Trạng thái:** Active.
- **Version:** v1.0
- **Date:** 2026-03-14

`docs/governance/` là authority path cho toàn bộ governance document của ATP.

## Phân loại: mandatory vs guidance vs template vs reference

| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| **Mandatory** | Quy tắc bắt buộc, phải tuân theo | Git Safety Charter, AI Branch Rules |
| **Guidance** | Hướng dẫn khuyến nghị | Framework principles |
| **Template** | Mẫu dùng chung | Safe_Git_Workflow_Templates, AI_Session_Bootstrap_Template |
| **Reference** | Tài liệu tham khảo | Global_Shorthand_Agreements |

Cây này định nghĩa các quy tắc vận hành authoritative cho các hoạt động lặp lại, rủi ro cao, có nhiều actor, hoặc có approval-sensitive gate.

## Cấu trúc governance hiện hành

- `ATP_3_Role_Workflow.md` - workflow governance cho mô hình Multi-AI của ATP: Architect -> Executor -> Verifier
- `ATP_Development_Ruleset.md` - ruleset vận hành development bắt buộc xuyên suốt version opening, slice execution, consolidation, freeze, và close-out, bao gồm global pre-implementation gate: tạo/switch/verify đúng slice branch trước khi bắt đầu slice mới
- `Global_Safe_Git_Branch_Guard_Rule.md` - global safe Git governance rule cho production `gsgr` runtime, alias layer, branch guard pattern `Check -> Switch -> Re-check -> Execute`, slice branch-lineage gate trước first pass của mọi slice mới, và current action surface như `start-slice`, `publish-branch`, `fetch`, `diff`, `log`, `branch-info`, `delete-branch`, `prune`
- `framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md` - rule bắt buộc để mọi milestone/version có lineage và documentation continuity rõ
- `framework/` - governance framework cấp cha
- `git/` - governance cho Git, branch, wrapper, và thao tác an toàn
- `documentation/` - governance cho biên soạn, review, promotion, và authority path của tài liệu
- `coding/` - governance cho triển khai và chỉnh sửa code
- `release/` - governance cho release, freeze, tag, và merge-to-main
- roadmap continuity và freeze close-out discipline áp dụng xuyên suốt release governance
- `ai-collaboration/` - quy tắc cộng tác với AI assistants
- `reference/` - tài liệu reference dùng chung, bao gồm shorthand/alias authority reference và bootstrap template

## Thứ tự đọc khuyến nghị

1. `framework/Contextual_Project_Governance_Framework.md`
2. `ATP_Development_Ruleset.md`
3. `Global_Safe_Git_Branch_Guard_Rule.md` cho `gsgr` runtime, alias layer, branch guard toàn cục trước mọi Git combo quan trọng, canonical `start-slice` flow, và pre-implementation gate cho mọi slice mới
4. `git/Contextual_Git_Governance_Model.md`
5. `git/Git_Safety_Charter.md`
6. `git/Safe_Git_Workflow_Templates.md`
7. `git/AI_Branch_Operation_Rules.md`
8. `git/Safe_Git_Wrappers_Spec.md`
9. `ATP_3_Role_Workflow.md` khi phase liên quan phối hợp nhiều AI hoặc verification workflow
10. các bundle domain còn lại theo đúng ngữ cảnh công việc
11. `reference/ATP_Global_Shorthand_and_Alias_Rules.md` khi cần diễn giải shorthand / alias đang dùng trong ATP

## Quy tắc áp dụng

Mọi phase, process, module, hay workflow mang tính lặp lại, rủi ro, đa tác nhân, hoặc cần approval rõ ràng phải được điều phối bằng governance bundle thuộc đúng domain.

Trong ATP, roadmap cũng là governance artifact bắt buộc:

- product roadmap
- major roadmap
- version roadmap

Mỗi version mới phải kế thừa từ previous frozen version và close-out/consolidation evidence của version trước đó.

`ATP_Development_Ruleset.md` là operational ruleset chính để biến các doctrine và roadmap principles này thành gates/checklist áp dụng được trong thực tế.

`framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md` là rule governance chuyên biệt để chuẩn hóa version lineage, documentation continuity, backfill, và authority path của từng milestone.

Các governance artifact trong cây này áp dụng cho:

- user
- AI assistants
- wrappers và scripts
- automation trong tương lai
- các thành viên dự án khác

## Quy tắc authority

- Khi một governance document trong cây này được review và promote thành authoritative, mọi actor tham gia phải tuân theo tài liệu đó cho đến khi có revision mới thay thế
- Governance reference document phải sống dưới `docs/governance/reference/`, không tách sang domain khác nếu không có quyết định mới
- Tài liệu seed hoặc tài liệu lịch sử không còn là authority path phải nằm trong `docs/archive/`
