# ATP v0.4 Candidate Assessment

## 1. Tóm tắt current state sau v0.3

ATP v0.3.0 đã khép lại baseline boundary và continuity ở mức tối thiểu trên `SOURCE_DEV/workspace`, gồm:

- exchange boundary decision model
- minimal exchange materialization dưới `exchange/current-task/<run-id>/`
- continue-pending operational continuity state
- minimal file-based reference / index support

Nhờ đó ATP hiện đã có:

- phân biệt rõ `run_local_handoff` và `external_exchange_candidate`
- external exchange payload tối thiểu có traceability về run nguồn
- continuation state explicit cho `continue_pending`
- reference/pointer đủ để nối current exchange, continuation, manifest reference, và authoritative refs

## 2. Những gì còn intentionally deferred sau v0.3

Các phần còn để lại có chủ ý:

- controlled persistence model ở mức operational, không phải production redesign
- quy tắc rõ hơn cho current-task replacement / coexistence khi có nhiều run liên tiếp
- recovery / resume contract tối thiểu cho continuation state
- generalized index / catalog subsystem
- search/query subsystem cho references
- queue, scheduler, continuation engine rộng
- approval UI
- remote orchestration

## 3. Phân biệt “cần sớm” và “có thể chờ”

### Cần sớm sau v0.3

- controlled persistence / recovery semantics cho current-task và continuation
- quy tắc current-task pointer / replacement nhất quán khi nhiều run cùng chạm `exchange/current-task/`
- manual resume contract tối thiểu để một `continue_pending` run có thể được pick up lại mà không phải suy diễn từ nhiều file rời

### Có giá trị nhưng chưa cần ngay

- inspect/trace tooling giàu hơn cho operator
- index/reference hardening rộng hơn cho nhiều current-task hoặc nhiều views

### Chưa nên mở trong v0.4

- production persistence redesign
- scheduling / queue / automation
- remote orchestration hoàn chỉnh
- approval UI
- broad metadata registry hoặc search subsystem

## 4. Candidate areas

## Candidate A — Controlled current-task persistence contract

### Mô tả

Chốt một persistence contract hẹp, file-based, cho `exchange/current-task/` và các pointer liên quan, để current-task state không chỉ tồn tại như tập hợp file rời mà có quy tắc ghi/đọc/replace rõ ràng.

### Vì sao quan trọng bây giờ

Sau v0.3, ATP đã materialize exchange và reference tối thiểu, nhưng chưa chốt rõ:

- current-task nào là authoritative operational pointer
- khi run mới đến thì current-task cũ được supersede ra sao
- trạng thái nào phải được giữ để operator có thể inspect hoặc resume an toàn

Nếu bỏ qua bước này và nhảy sang orchestration hay automation, ATP sẽ xây trên một current-task contract còn mơ hồ.

### Phụ thuộc vào v0.3 baseline

- dựa trực tiếp trên Slice B exchange materialization
- dùng Slice C continuation state làm input chính
- dùng Slice D reference/index support làm base traceability

### Phân loại

**Must-have cho v0.4**

## Candidate B — Continue-pending recovery / resume contract

### Mô tả

Làm rõ continuation nào là recoverable, file nào là entry point chính, và operator hoặc step kế tiếp phải dựa vào contract nào để resume một `continue_pending` run.

### Vì sao quan trọng

v0.3 đã có continuation state nhưng vẫn thiên về traceability. ATP chưa có một resume contract rõ ở mức operational, dù chưa cần scheduler hay remote execution.

### Phụ thuộc vào v0.3 baseline

Phụ thuộc trực tiếp vào Slice C và các pointer của Slice D.

### Phân loại

**Must-have cho v0.4**, nhưng nên đi cùng Candidate A thay vì tách thành theme lớn riêng

## Candidate C — Current-task reference / index hardening

### Mô tả

Bổ sung reference/index support hẹp hơn nhưng rõ hơn cho current-task lifecycle:

- active pointer
- superseded pointer hoặc close-out marker
- trace refs đủ để operator lần lại current task chain

### Vì sao quan trọng

Slice D mới chỉ đủ cho một current-task tối thiểu. Khi ATP bắt đầu có nhiều run và continuation nối tiếp nhau, traceability chỉ bằng path trực tiếp có thể trở nên mỏng.

### Phụ thuộc vào v0.3 baseline

Phụ thuộc trực tiếp vào Slice D.

### Phân loại

**Good-to-have nếu capacity cho phép**, hoặc tích hợp ở mức rất nhỏ vào Candidate A-B

## Candidate D — Operator-facing inspect / resume commands

### Mô tả

Thêm surface nhỏ ở CLI để inspect current task hoặc chỉ ra entry point resume.

### Vì sao chưa nên là trọng tâm

Giá trị có thật, nhưng nếu chưa chốt persistence/recovery contract bên dưới thì surface CLI sẽ chỉ bọc quanh semantics chưa ổn định.

### Phân loại

**Good-to-have nếu capacity cho phép**, không nên là theme trung tâm của v0.4

## Candidate E — Production persistence / orchestration expansion

### Mô tả

Mở rộng sang persistence layer ở mức production, queueing, scheduling, remote follow-up, hay orchestration control sâu hơn.

### Vì sao chưa nên làm ngay

Đây là bước nhảy phạm vi lớn. Sau v0.3, ATP vẫn còn thiếu current-task persistence/recovery contract hẹp. Nếu đi thẳng sang production persistence hay orchestration, rủi ro scope drift là rất cao.

### Phân loại

**Defer beyond v0.4**

## 5. Kết luận đánh giá candidate

Hướng hợp lý nhất cho v0.4 không phải là mở rộng platform breadth, mà là:

- chốt current-task persistence / recovery contract ở mức hẹp
- làm rõ resume semantics cho `continue_pending`
- harden reference/index support chỉ đến mức cần để contract đó operationally coherent

Nói ngắn gọn: v0.4 nên là phase **operational persistence-and-recovery hardening**, không phải phase UI, scheduler, hay production persistence redesign.
