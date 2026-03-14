# ATP Docs Review Report
## Rà soát và chuẩn hóa thư mục `docs/` trước khi tích hợp governance tree

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Scope:** `docs/` hiện tại trong ATP, trước khi giải nén bundle governance mới

## 1. Kết luận nhanh

Thư mục `docs/` hiện tại **đủ dùng như seed/baseline**, nhưng **chưa đạt trạng thái chuẩn hóa hoàn chỉnh** theo rule tài liệu mới.

Ba vấn đề lớn nhất:

1. **Nhiều tài liệu core đang viết bằng tiếng Việt không dấu**  
   Điều này không còn phù hợp với rule tài liệu vừa chốt.

2. **Một số tài liệu core đã lỗi thời theo milestone hiện tại**
   - `overview.md` còn dừng ở M6
   - `local_bootstrap.md` còn mô tả ATP M1-M2
   - một số mô tả vận hành chưa phản ánh ATP v0 đã khép kín đến M8

3. **Cấu trúc `docs/` chưa tích hợp governance tree mới**
   Hiện mới có:
   - `architecture/`
   - `design/`
   - `operators/`
   - `decisions/`

   nhưng chưa có:
   - `governance/`
   - `reference/` tương ứng theo mô hình mới

## 2. Điểm tốt hiện tại

- Có phân lớp cơ bản hợp lý: `architecture`, `design`, `operators`, `decisions`
- Có snapshot docs cho:
  - ATP v0 final
  - ATP v0.1 hardening
- Có các tài liệu kiến trúc nền quan trọng đã được giữ lại
- Có thể chuẩn hóa tiếp mà **không cần phá cấu trúc tổng thể hiện tại**

## 3. Điểm cần chuẩn hóa ngay

### 3.1. Nội dung
Cần chuẩn hóa sang:
- tiếng Việt Unicode có dấu rõ ràng
- giữ nguyên English technical terms cần thiết
- wording nhất quán theo ATP hiện tại

### 3.2. Tính cập nhật
Cần cập nhật các file core để phản ánh ATP đã hoàn tất đến M8, không còn chỉ là seed M1-M6.

### 3.3. Cách lưu trữ
Sau khi anh giải nén governance bundle, nên có tree mục tiêu:

```text
docs/
├── architecture/
├── design/
├── operators/
├── decisions/
├── governance/
└── archive/    (nếu cần)
```

## 4. Nhận định theo nhóm

### A. Nhóm cần chuẩn hóa ngay
- `docs/README.md`
- `docs/architecture/overview.md`
- `docs/architecture/repo_boundary.md`
- `docs/architecture/layered_architecture.md`
- `docs/architecture/orchestration_flow.md`
- `docs/architecture/workspace_artifact_handoff.md`
- `docs/design/*.md`
- `docs/operators/*.md`
- `docs/decisions/README.md`

### B. Nhóm nên giữ như snapshot / reference
- `docs/architecture/ATP_v0_final_snapshot_docs/*`
- `docs/architecture/ATP_v0_1_hardening_snapshot_docs/*`

### C. Nhóm kiến trúc lớn cần review riêng sau
- `ATP_AI_Workspace_Open_Rules.md`
- `ATP_Drawio_Style_Structure.md`
- `ATP_Glossary_VI.md`
- `ATP_So_do_gop_kien_truc_hien_tai_Super_Tree.md`
- `ATP_So_do_phan_lop_va_flow_truc_quan.md`
- `ATP_Workspace_Artifact_Handoff_Model.md`
- `ATP_MVP_v0_Freeze_Decision_Record.md`
- `ATP_MVP_v0_Implementation_Plan.md`

Các file này không nên sửa vội theo kiểu đại trà; nên review riêng theo bundle/scope.

## 5. Kết quả của lần `chk-docs` này

Tôi đã tạo sẵn một **normalized core docs bundle** cho phần tài liệu core nhỏ và trung bình, để anh có thể:
- copy đè vào repo nếu muốn
- hoặc dùng làm baseline chỉnh trực tiếp

## 6. Khuyến nghị thao tác tiếp theo

1. Anh giải nén governance bundle vào `docs/governance/...`
2. Áp normalized core docs bundle này vào phần core docs
3. Sau đó chạy tiếp một vòng `chk-docs` để:
   - rà authority path
   - rà naming
   - rà duplicate/superseded docs
   - chuẩn hóa toàn bộ tree `docs/` lần nữa

## 7. Chốt

`docs/` hiện tại **có thể chuẩn hóa rất tốt**, và chưa có dấu hiệu phải đập đi làm lại.  
Hướng đúng là:
- giữ cấu trúc nền
- chuẩn hóa core docs trước
- tích hợp governance tree
- rồi mới làm vòng cleanup sâu hơn cho toàn bộ `docs/`
