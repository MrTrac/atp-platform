# ATP – Quy tắc mở Workspace cho AI trong hệ sinh thái ATP

## 1. Mục đích tài liệu

Tài liệu này quy định cách hiểu và cách mở workspace/repo cho AI trong hệ sinh thái ATP.

Mục tiêu là làm rõ:

- khi nào mở repo ATP;
- khi nào mở repo TDF;
- khi nào mở repo shared;
- khi nào mở repo utility;
- khi nào mới mở cả `SOURCE_DEV`;
- vì sao “mở thư mục chứa dự án” gần như phải hiểu là “mở root repo của thực thể đang làm việc”.

---

## 2. Nguyên tắc gốc

# Với một project/product/platform có Git riêng, “mở thư mục chứa dự án” trong ngữ cảnh AI/IDE gần như nên hiểu là “mở root repo của thực thể đó”.

Điều này áp dụng cho:
- ATP
- TDF
- shared
- utilities độc lập
- các product khác về sau

---

## 3. Vì sao nên mở root repo?

Khi mở đúng root repo, AI/IDE có thể nhìn được:

- cấu trúc thư mục của thực thể đó;
- file cấu hình;
- docs liên quan;
- dependency logic;
- tests/build scripts;
- Git context trong đúng boundary.

Điều này giúp AI:
- hiểu đúng phạm vi;
- không bị thiếu context;
- không bị kéo nhầm sang repo khác.

---

## 4. Quy tắc tổng quát

### 4.1 Ưu tiên mở repo hẹp nhất nhưng đủ ngữ cảnh
Không mở rộng hơn mức cần thiết.

### 4.2 Không dùng `SOURCE_DEV` làm workspace mặc định
`SOURCE_DEV` chỉ nên mở khi task thật sự ở cấp toàn hệ sinh thái.

### 4.3 Không dùng `workspace/` làm coding workspace chính
`workspace/` là runtime zone, không phải source repo.

### 4.4 Khi cần runtime artifacts, ATP phải handoff có kiểm soát
Không giải quyết bằng cách mở toang cả `workspace/`.

---

## 5. Khi nào mở repo ATP

Mở:
```text
SOURCE_DEV/platforms/ATP
```

### Dùng khi:
- sửa ATP core;
- sửa provider registry;
- sửa adapter/routing/cost/policy;
- sửa docs kiến trúc ATP;
- sửa scripts/templates/tests của ATP.

### Không nên mở ATP repo khi:
- task chỉ thuộc TDF;
- task chỉ thuộc shared;
- task chỉ thuộc utility riêng.

---

## 6. Khi nào mở repo TDF

Mở:
```text
SOURCE_DEV/products/TDF
```

### Dùng khi:
- sửa framework TDF;
- sửa docs TDF;
- sửa modules trong TDF;
- sửa `TDF/tools/*`;
- review/refactor/release TDF.

### Lưu ý
Các tool trong `TDF/tools/*` là component của TDF, nên mặc định vẫn mở **repo TDF**, không mở một thư mục con riêng lẻ làm workspace chính.

---

## 7. Khi nào mở repo shared

Mở:
```text
SOURCE_DEV/shared
```

### Dùng khi:
- sửa standards;
- sửa templates;
- sửa schemas;
- sửa prompt-kits;
- sửa glossaries;
- sửa common-libs dùng chung.

### Ví dụ:
- update `common.sh`;
- sửa template manifest;
- sửa schema provider registry;
- nâng version prompt-kit dùng chung.

---

## 8. Khi nào mở repo utility riêng

Mở:
```text
SOURCE_DEV/utilities/<utility-name>
```

### Dùng khi:
- utility đó là repo riêng;
- task chỉ thuộc utility đó;
- không cần context toàn ATP/TDF/shared.

### Ví dụ:
- sửa `trace_log`;
- sửa helper tool độc lập;
- review release của một utility riêng.

---

## 9. Khi nào mới mở cả SOURCE_DEV

Mở:
```text
SOURCE_DEV
```

### Chỉ dùng khi task thực sự ở cấp toàn hệ sinh thái, ví dụ:
- rà kiến trúc liên repo;
- migration storage model;
- soát boundary giữa ATP / TDF / shared / utilities;
- audit cross-repo dependencies;
- thiết kế portfolio governance;
- chuẩn bị di chuyển cả workspace sang node khác.

### Không nên dùng cho:
- coding task thông thường;
- sửa 1 product cụ thể;
- sửa 1 platform cụ thể;
- sửa 1 utility cụ thể.

---

## 10. Quy tắc ra quyết định mở workspace

Dùng 3 câu hỏi sau:

### Câu 1
Task này đang sửa **source chính** của thực thể nào?
- ATP
- TDF
- shared
- utility riêng
- ecosystem-level

### Câu 2
Task có cần context toàn repo của thực thể đó không?
- nếu có → mở root repo
- nếu không → vẫn thường nên mở root repo, trừ case cực hẹp

### Câu 3
Task có phải task cross-repo / ecosystem-level không?
- nếu có → mới cân nhắc mở `SOURCE_DEV`

---

## 11. Quy tắc an toàn cho AI coding

### Quy tắc 1
Mở **repo root của thực thể đang làm việc** là lựa chọn mặc định an toàn nhất.

### Quy tắc 2
Không mở `SOURCE_DEV` chỉ vì “cho chắc”.
Điều đó thường làm AI bị nhiễu hơn.

### Quy tắc 3
Không dùng `workspace/` làm coding workspace chính.
Runtime artifacts phải được handoff có kiểm soát.

### Quy tắc 4
Không mở thư mục con quá hẹp nếu task có liên hệ với nhiều phần trong cùng repo.
Ưu tiên đủ context hơn là quá bó hẹp.

---

## 12. Bảng quy tắc nhanh

| Loại task | Workspace nên mở |
|---|---|
| Sửa ATP core | `SOURCE_DEV/platforms/ATP` |
| Sửa TDF / TDF tools | `SOURCE_DEV/products/TDF` |
| Sửa shared standards/templates/common libs | `SOURCE_DEV/shared` |
| Sửa utility độc lập | `SOURCE_DEV/utilities/<utility-name>` |
| Audit / migration / cross-repo architecture | `SOURCE_DEV` |

---

## 13. Hai câu chốt cần nhớ

### Câu chốt 1
> Với một project/product/platform có Git riêng, “thư mục chứa dự án” trong ngữ cảnh AI/IDE gần như nên hiểu là “root repo của thực thể đó”.

### Câu chốt 2
> Runtime output không cần nằm trong repo đang mở; ATP sẽ handoff output từ `workspace/` sang step sau bằng cơ chế có kiểm soát.

---

## 14. Kết luận

Bộ quy tắc này giúp ATP và người vận hành:
- mở đúng workspace;
- giữ đúng boundary;
- tránh AI bị nhiễu context;
- tận dụng đúng repo context;
- và không lẫn giữa source repo với runtime workspace.
