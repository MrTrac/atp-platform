# ATP Practical Capability Milestone Map
## Từ hiện tại đến mốc “multi-AI automation thực chiến đầu tiên”

## 1. Mục đích tài liệu

Tài liệu này trả lời một câu hỏi rất thực tế:

**Từ trạng thái hiện tại của ATP, còn khoảng bao nhiêu mốc phát triển nữa để ATP có thể tự động xử lý một task đơn giản như edit 1 file của TDF bằng cơ chế automation multi-AI, có dùng AI resources thực tế và có API/tool boundary giữa các AI?**

Tài liệu này không phải release note, cũng không phải planning chi tiết của từng slice.  
Đây là một **practical roadmap note** để nhìn nhanh:

- ATP đang ở đâu
- còn bao nhiêu chặng nữa
- các chặng đó thuộc version nào
- mỗi chặng mở ra được gì
- khi nào ATP mới chạm mốc “multi-AI automation thực chiến đầu tiên”

---

## 2. Câu trả lời ngắn nhất

Từ hiện tại đến mốc:

**ATP có thể tự động thực thi một task đơn giản của user như edit 1 file của TDF bằng automation multi-AI, có dùng AI resources thực tế và có API/tool boundary giữa các AI**

ATP còn cần khoảng:

## **10–14 slices nữa**

và các slices này hợp lý nhất sẽ trải qua:

- phần còn lại của **v0.5**
- phần chính của **v1**
- và chạm vào **v2.1**

---

## 3. Mốc đích cần hiểu đúng

Mốc đích không chỉ là:

- ATP “biết gọi nhiều AI”
- hoặc ATP “có thể gửi prompt sang nhiều nơi”

Mốc đích đúng phải là ATP có thể làm được chuỗi như sau:

1. nhận 1 request thực tế từ user  
2. hiểu task thuộc product nào  
3. hiểu ATP cần handoff intent gì  
4. chọn đúng AI / product execution surface phù hợp  
5. gửi task qua API hoặc tool boundary  
6. nhận output về  
7. nếu cần, chuyển bước tiếp theo sang AI khác  
8. edit file thật  
9. validate kết quả  
10. dừng ở approval gate hoặc hoàn tất task

Đây là mốc **multi-AI automation thực chiến đầu tiên**.

---

## 4. ATP đang ở đâu hiện tại

### ATP hiện đã có
ATP hiện đã có nền tảng mạnh ở các lớp:

- doctrine / roadmap / governance baseline
- runtime workspace model
- current-task baseline
- inspect baseline
- `v0.5 Slice A`: request-to-product resolution contract

### ATP hiện chưa có
ATP hiện vẫn chưa có đầy đủ các lớp cần thiết để automation multi-AI thật:

- resolution-to-handoff intent contract
- product execution preparation contract
- product execution result contract
- provider / agent registry usable
- provider selection logic
- execution delegation contract
- multi-step orchestration loop
- retry / review / reconcile semantics đủ mạnh

---

## 5. Roadmap tổng quan theo version

## Giai đoạn 1 — Hoàn tất `v0.5`

### Mục tiêu
Khóa nốt phần **foundational completion** của ATP.

### Số slices hợp lý còn lại
## **3–4 slices**

### ATP sẽ mở được gì sau giai đoạn này
ATP sẽ có đủ nền để biểu diễn trọn trục:

**request → product resolution → handoff intent → execution preparation → result traceability**

### Các slices hợp lý trong `v0.5`
- **Slice A** — Request-to-Product Resolution Contract  
  **Trạng thái:** đã xong
- **Slice B** — Resolution-to-Handoff Intent Contract
- **Slice C** — Product Execution Preparation Contract
- **Slice D** — Product Execution Result Contract
- có thể thêm **Slice E** — Minimal review/approval gate refinement hoặc task-state coherence

### ATP làm được gì sau khi xong `v0.5`
- hiểu request rõ hơn
- resolve tới product/capability rõ hơn
- biết handoff để làm gì
- chuẩn bị product execution rõ hơn
- nhận và giữ kết quả execution rõ hơn
- toàn bộ flow này có artifact contract rõ trong workspace

### ATP vẫn chưa làm được gì sau `v0.5`
- chưa orchestrate nhiều AI/provider thật
- chưa provider-aware thật
- chưa cost-aware / topology-aware
- chưa có automation multi-AI end-to-end

---

## Giai đoạn 2 — Đi qua `v1`

### Mục tiêu
Biến ATP từ “đúng hình và đủ contract” thành **operational maturity platform**.

### Số slices hợp lý
## **4–5 slices**

### Các hướng slices hợp lý trong `v1`
- production-grade persistence refinement
- recovery / resume semantics thực dụng hơn
- review / approval maturity
- inspect / explainability maturity
- execution-state / retry / operator usability refinement

### ATP làm được gì sau `v1`
- giữ state tốt hơn
- restart / continue workflow an toàn hơn
- review / approval rõ hơn
- operator nhìn hệ thống dễ hơn
- ATP bắt đầu usable hơn cho workflow vận hành thật, chứ không chỉ đúng kiến trúc

### ATP vẫn chưa làm được gì sau `v1`
- vẫn chưa phải multi-provider orchestration platform đầy đủ
- vẫn chưa thực sự chọn / gọi / phối hợp nhiều AI resources theo breadth lớn
- vẫn chưa là distributed control platform

---

## Giai đoạn 3 — Chạm `v2.1`

### Mục tiêu
Mở lớp **orchestration breadth tối thiểu** để ATP bắt đầu điều phối AI resources thực tế.

### Số slices hợp lý
## **3–5 slices**

### Các hướng slices hợp lý trong `v2.1`
- provider / agent registry contract
- provider selection / capability matching
- execution delegation contract
- multi-step orchestration loop
- có thể thêm policy / cost gate tối thiểu

### ATP làm được gì sau `v2.1`
Đây là mốc ATP **bắt đầu thực sự làm được** task kiểu đã nêu:

- giao bước 1 cho AI A
- nhận output
- giao bước 2 cho AI B
- quay lại ATP để quyết định bước tiếp
- edit 1 file thật
- có thể có approval gate trước khi finalize

### ATP vẫn chưa làm được gì sau `v2.1`
- chưa phải orchestration platform rất rộng
- chưa distributed control plane
- chưa multi-product portfolio maturity đầy đủ
- chưa scheduling / reconcile mạnh

---

## 6. Tổng hợp cực ngắn theo số mốc

### Phương án ngắn nhất, rất ép
- `v0.5`: còn **3 slices**
- `v1`: **4 slices**
- `v2.1`: **3 slices**

## Tổng:
## **10 slices**

### Phương án thực tế hơn
- `v0.5`: còn **4 slices**
- `v1`: **5 slices**
- `v2.1`: **4–5 slices**

## Tổng:
## **13–14 slices**

---

## 7. Mốc “demo được” và mốc “dùng ổn”

### Mốc demo được đầu tiên
Khoảng:

## **sau 8–10 slices nữa**

Khi đó ATP có thể:
- nhận task đơn giản
- route sang 1–2 AI surfaces
- edit 1 file đơn giản
- validate cơ bản
- dừng ở approval gate

Nhưng vẫn còn khá thô.

### Mốc dùng tương đối ổn
Khoảng:

## **sau 12–14 slices nữa**

Khi đó ATP mới có khả năng:
- automation multi-AI có kiểm soát hơn
- state rõ hơn
- review / retry / continue tốt hơn
- inspect tốt hơn
- boundary giữa ATP và AI resources thực tế rõ hơn

---

## 8. Bảng nhìn nhanh nhất

| Mốc | Thuộc version | ATP mở được gì |
|---|---|---|
| Hiện tại | `v0.5 Slice A` | request → product/capability resolution contract |
| + 3–4 slices | hết `v0.5` | request → product → handoff → execution prep/result coherence |
| + 4–5 slices | `v1.x` | operational maturity: persistence / recovery / review / inspect usable hơn |
| + 3–5 slices | `v2.1` | provider/agent selection + execution delegation + multi-step orchestration tối thiểu |
| Mốc đạt mục tiêu đầu tiên | khoảng `v2.1–v2.2` | ATP bắt đầu làm được simple multi-AI task automation thật |

---

## 9. Kết luận chốt

Nếu hỏi rất thực tế:

**“Từ bây giờ đến lúc ATP tự động edit 1 file của TDF bằng automation multi-AI có API giữa các AI thì còn bao xa?”**

Thì câu trả lời hợp lý nhất là:

## **còn khoảng 10–14 slices**
trải qua:
- phần còn lại của **`v0.5`**
- phần chính của **`v1`**
- và chạm **`v2.1`**

### Mốc sớm nhất có thể demo
## **`v2.1`**

### Mốc hợp lý để dùng ổn hơn
## **`v2.2` trở đi**

---

## 10. Cách sử dụng tài liệu này

Tài liệu này nên được dùng như:
- một **note roadmap thực dụng**
- một **tài liệu nhìn nhanh cho decision-making**
- một **cầu nối giữa roadmap doctrine và planning thực tế**

Tài liệu này **không thay thế**:
- product roadmap
- major roadmap
- version roadmap
- stage roadmap chi tiết

Mà đóng vai trò:
- trả lời nhanh câu hỏi thực tế: “ATP còn bao xa để làm được X?”
