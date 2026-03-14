# Governance ATP

- **Mục đích:** Authority path cho governance; quy tắc vận hành cho hoạt động lặp lại, rủi ro cao, đa tác nhân.
- **Phạm vi:** Git, documentation, coding, release, AI collaboration; framework và reference.
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

- `framework/` - governance framework cấp cha
- `git/` - governance cho Git, branch, wrapper, và thao tác an toàn
- `documentation/` - governance cho biên soạn, review, promotion, và authority path của tài liệu
- `coding/` - governance cho triển khai và chỉnh sửa code
- `release/` - governance cho release, freeze, tag, và merge-to-main
- `ai-collaboration/` - quy tắc cộng tác với AI assistants
- `reference/` - tài liệu reference dùng chung, bao gồm shorthand và bootstrap template

## Thứ tự đọc khuyến nghị

1. `framework/Contextual_Project_Governance_Framework.md`
2. `git/Contextual_Git_Governance_Model.md`
3. `git/Git_Safety_Charter.md`
4. `git/Safe_Git_Workflow_Templates.md`
5. `git/AI_Branch_Operation_Rules.md`
6. `git/Safe_Git_Wrappers_Spec.md`
7. các bundle domain còn lại theo đúng ngữ cảnh công việc

## Quy tắc áp dụng

Mọi phase, process, module, hay workflow mang tính lặp lại, rủi ro, đa tác nhân, hoặc cần approval rõ ràng phải được điều phối bằng governance bundle thuộc đúng domain.

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
