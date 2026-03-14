# Milestone Documentation — ATP v0 Family

## Mục đích

Thư mục này chứa bộ tài liệu milestone documentation cho từng version trong ATP v0 major family, tuân theo milestone template bundle tại:

- `docs/roadmap/templates/milestones/`

Các tài liệu ở đây được tổ chức theo version, mỗi version có thể dùng:

- **Dạng đầy đủ (full form)**: 4 tài liệu riêng biệt — Proposal, Execution Plan, Freeze Decision Record, Closeout
- **Dạng gộp (compact merged form)**: 2 tài liệu gộp — Proposal + Execution Plan, Freeze + Closeout

Lựa chọn dạng nào phụ thuộc vào chất lượng evidence và mức độ phức tạp của milestone.

## Cấu trúc

```
milestones/
├── v0_2/   — Runtime materialization baseline (frozen: v0.2.0)
├── v0_3/   — External boundary / continuation baseline (frozen: v0.3.0)
├── v0_4/   — Current-task persistence / recovery baseline (frozen: v0.4.0)
└── v0_5/   — Continuity completion của v0 major family (active planning)
```

## Quy tắc governance

- Tài liệu ở đây là backfill documentation continuity, không phải tái viết lịch sử.
- Mọi claim đều phải phân biệt rõ: đã xác nhận / suy luận hợp lý / tạm thời / cần xác nhận thêm.
- Nguồn chuẩn vẫn là các archive reports và freeze closeout docs trong `docs/archive/reports/`.
- Tài liệu này bổ sung cấu trúc milestone, không thay thế archive reports.

## Tài liệu liên quan

- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`
- `docs/roadmap/templates/milestones/` — template bundle
- `docs/archive/reports/` — freeze closeout và integration/consolidation reports
