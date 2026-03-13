# ATP – Mô hình Handoff Artifact trong Workspace

## 1. Mục đích tài liệu

Tài liệu này mô tả mô hình **Workspace Artifact Handoff** của ATP, nhằm trả lời rõ các câu hỏi:

- output của từng task/run được lưu ở đâu;
- output nào được xem là quan trọng;
- output nào được chọn để dùng cho step kế tiếp;
- ATP sẽ đưa output đó trở lại cho AI/executor như thế nào;
- khi nào dùng inline context, khi nào dùng evidence bundle, exchange bundle hoặc manifest reference.

Tài liệu này là phần bổ sung chi tiết cho kiến trúc ATP V1.3 Draft.

---

## 2. Bài toán kiến trúc cần giải quyết

Trong ATP, AI coding thường sẽ mở **root repo của thực thể đang được chỉnh sửa**, ví dụ:

- làm ATP → mở `SOURCE_DEV/platforms/ATP`
- làm TDF → mở `SOURCE_DEV/products/TDF`
- làm shared → mở `SOURCE_DEV/shared`

Trong khi đó, output runtime của từng run/task lại không nên nằm lẫn trong repo source, mà nên nằm trong:

```text
SOURCE_DEV/workspace/
```

Điều này dẫn tới một câu hỏi thực tế:

> Nếu AI đang mở repo source, còn output lại nằm trong `workspace/`, thì AI làm sao dùng được output đó để làm tiếp?

Câu trả lời của ATP là:

# AI không cần tự nhìn toàn bộ `workspace/`
# ATP phải chọn đúng artifact và handoff lại cho AI theo cơ chế có kiểm soát

---

## 3. Nguyên tắc cứng của Workspace Artifact Handoff

### 3.1 Source và runtime phải tách riêng
- source code nằm trong repo đang mở;
- runtime outputs nằm trong `SOURCE_DEV/workspace/...`.

### 3.2 Không đưa toàn bộ runtime zone cho AI
ATP không được mặc định cấp cả `workspace/` cho AI/executor.  
ATP phải chọn lọc artifact liên quan.

### 3.3 Artifact phải có trạng thái
Không phải mọi output đều có cùng giá trị.  
ATP phải phân biệt:
- raw;
- filtered;
- selected;
- authoritative.

### 3.4 Handoff phải có kiểm soát
ATP phải biết:
- artifact nào được chọn;
- artifact đó dùng cho step nào;
- artifact đó giao cho executor nào;
- artifact đó còn hiệu lực hay đã bị thay thế.

---

## 4. Output được lưu ở đâu?

Tôi đề xuất mô hình lưu output theo từng run như sau:

```text
SOURCE_DEV/workspace/
└── atp-runs/
    └── <run-id>/
        ├── request/
        ├── manifests/
        ├── planning/
        ├── routing/
        ├── executor-outputs/
        ├── validation/
        ├── decisions/
        ├── final/
        └── logs/
```

---

## 5. Ý nghĩa từng vùng trong run

### `request/`
Chứa input ban đầu của run:
- `request.md`
- `normalized_request.yaml`

### `manifests/`
Chứa các manifest điều phối:
- `task_manifest.yaml`
- `product_context.yaml`
- `provider_selection.yaml`

### `planning/`
Chứa output planning:
- `plan.md`
- dependency notes
- step graph

### `routing/`
Chứa output route:
- routing decision
- provider choice
- fallback choice
- cost decision

### `executor-outputs/`
Chứa output thô từ từng executor:
- chatgpt output
- cursor patch
- claude rewrite
- local AI result
- shell result

### `validation/`
Chứa output kiểm tra:
- lint result
- test result
- review result
- validation summary

### `decisions/`
Chứa các quyết định:
- accept/reject note
- escalation decision
- approval gate note

### `final/`
Chứa output cuối cùng của run:
- final patch
- final report
- final package
- final summary

### `logs/`
Chứa:
- run log
- execution trace
- route log

---

## 6. Phân loại artifact theo giá trị sử dụng

ATP nên phân loại artifact thành 4 cấp.

### 6.1 Raw Artifact
Là output thô vừa sinh ra.

Ví dụ:
- full AI response
- full shell output
- raw diff
- raw test log

### 6.2 Filtered Artifact
Là output đã được cắt gọn/lọc bớt phần dư.

Ví dụ:
- log excerpt
- cleaned diff summary
- condensed response

### 6.3 Selected Artifact
Là artifact ATP chọn để dùng tiếp ở step kế tiếp.

Ví dụ:
- selected patch
- selected architecture option
- selected validation summary

### 6.4 Authoritative Artifact
Là artifact chuẩn có hiệu lực cho run hiện tại.

Ví dụ:
- final approved plan
- final patch
- final validation summary
- final routing decision

---

## 7. Tiêu chí chọn artifact để handoff

ATP chỉ nên handoff artifact cho step sau nếu nó thỏa ít nhất một trong các tiêu chí sau:

- là output chính của step trước;
- là input bắt buộc cho step kế tiếp;
- là bằng chứng validation/review cần thiết;
- là decision ảnh hưởng logic tiếp theo;
- là version đã được chọn hoặc đã được approve trong số nhiều phương án.

---

## 8. Các cơ chế handoff chính

ATP nên hỗ trợ 4 cơ chế handoff chính.

### 8.1 Inline Context
ATP lấy phần nội dung quan trọng và nhúng trực tiếp vào task package/prompt.

#### Dùng khi:
- nội dung ngắn;
- summary;
- decision note;
- short validation result;
- short patch excerpt.

#### Ưu điểm:
- nhanh;
- ít nhiễu;
- dễ đọc.

#### Nhược điểm:
- không phù hợp với artifact dài.

---

### 8.2 Evidence Bundle
ATP chọn một nhóm artifact file và giao như một bundle logic.

#### Dùng khi:
- cần nhiều file liên quan;
- cần cross-check giữa plan/result/validation;
- AI cần đủ ngữ cảnh nhưng không quá nhiều.

#### Ví dụ bundle:
- `plan.md`
- `selected_patch.diff`
- `validation_summary.md`

#### Ưu điểm:
- cân bằng giữa đủ dữ liệu và kiểm soát phạm vi.

#### Nhược điểm:
- cần ATP curate tốt.

---

### 8.3 Exchange Bundle
ATP materialize các artifact cần thiết vào một vùng handoff chuyên dụng.

Ví dụ:
```text
SOURCE_DEV/workspace/exchange/current-task/
```

#### Dùng khi:
- workflow file-based;
- dùng UI-based AI tools;
- cần mở trực tiếp file handoff;
- cần chuyển dữ liệu giữa nhiều executor.

#### Ưu điểm:
- thực dụng;
- dễ dùng với semi-automated flow.

#### Nhược điểm:
- nếu quản lý kém sẽ lẫn file cũ/mới.

---

### 8.4 Manifest Reference
ATP không đưa toàn bộ nội dung, mà đưa manifest chỉ rõ:
- artifact nào là authoritative;
- file nào bắt buộc đọc;
- file nào chỉ là tham khảo;
- version nào đang có hiệu lực.

#### Dùng khi:
- workflow dài;
- nhiều artifact cùng loại;
- cần authoritative control;
- cần audit chặt.

#### Ưu điểm:
- rất sạch về kiến trúc;
- phù hợp với stateful workflow dài.

#### Nhược điểm:
- cần ATP kỷ luật tốt.

---

## 9. Khi nào dùng cơ chế nào?

### Dùng Inline Context khi:
- artifact ngắn;
- chỉ cần summary;
- step tiếp theo cần ít dữ liệu.

### Dùng Evidence Bundle khi:
- cần 2–5 artifact quan trọng;
- cần đối chiếu giữa plan, patch, validation.

### Dùng Exchange Bundle khi:
- workflow file-based;
- dùng UI-based AI tools;
- cần mở trực tiếp file handoff.

### Dùng Manifest Reference khi:
- run dài;
- nhiều vòng decision;
- nhiều artifact cạnh tranh;
- cần authoritative control.

---

## 10. Cấu trúc đề xuất cho vùng handoff

```text
SOURCE_DEV/workspace/
├── atp-runs/
├── atp-artifacts/
├── atp-cache/
├── atp-staging/
└── exchange/
    ├── current-task/
    ├── current-review/
    └── current-approval/
```

### Ý nghĩa
- `current-task/` = handoff cho executor đang xử lý
- `current-review/` = handoff cho reviewer
- `current-approval/` = handoff cho bước user approval

---

## 11. Vai trò của ATP trong handoff

ATP phải là thành phần chịu trách nhiệm:

- chọn artifact đúng;
- loại bỏ artifact dư thừa;
- đảm bảo artifact đúng run;
- đảm bảo artifact đúng step;
- đóng gói handoff đúng executor;
- ghi nhận artifact nào đã được dùng ở step nào.

ATP không nên để AI/executor tự đi mò artifact trong `workspace/`.

---

## 12. Kết luận chốt

> AI coding mở root repo của thực thể đang được chỉnh sửa; còn runtime outputs được ATP lưu trong `workspace/` và tái cấp phát cho các step sau thông qua inline context, evidence bundles, exchange bundles hoặc manifest references.

Đây là câu chốt của Workspace Artifact Handoff Model.
