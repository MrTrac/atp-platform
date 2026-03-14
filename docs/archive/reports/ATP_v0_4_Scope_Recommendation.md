# ATP v0.4 Scope Recommendation

## 1. Recommended v0.4 direction

ATP v0.4 nên tập trung vào một hướng hẹp và nối tự nhiên từ v0.3:

**Hoàn thiện controlled current-task persistence và continue-pending recovery contract ở mức operational, file-based, không mở sang production persistence hay orchestration expansion.**

## 2. Vì sao đây là bước tiếp theo đúng nhất

Sau v0.3, ATP đã có:

- boundary decision rõ
- external exchange payload tối thiểu
- continuation state rõ
- reference/index support tối thiểu

Phần còn hở đáng kể nhất không còn là “có boundary hay chưa”, mà là:

- current-task nào là operationally current
- khi có run tiếp theo thì pointer nào bị supersede và được ghi nhận ra sao
- một `continue_pending` run phải được resume từ entry point nào mà không cần suy đoán thủ công từ nhiều file

Nếu bỏ qua gap này và nhảy sang UI, scheduling, hay production persistence, ATP sẽ mở rộng trên một operational contract còn chưa đủ chặt.

## 3. Scope được khuyến nghị cho v0.4

### Must-have

- controlled persistence contract tối thiểu cho `exchange/current-task/` và các current pointers liên quan
- continue-pending recovery / resume contract rõ ràng ở mức file-based
- traceability rule cho supersede / replace / active current-task pointer

### Good-to-have nếu capacity cho phép

- inspect surface nhỏ ở CLI cho current-task / resume entry point
- index/reference hardening nhỏ để lần chain giữa current, superseded, và originating run

### Không nên đưa vào v0.4

- production persistence redesign
- search/index subsystem rộng
- queue hoặc scheduler
- remote orchestration
- approval UI
- broad workflow automation

## 4. Scope statement đề xuất cho v0.4

ATP v0.4 là phase:

**“minimal current-task persistence and recovery hardening”**

chứ không phải:

- “database phase”
- “scheduler phase”
- “remote execution phase”

## 5. Expected outcome nếu chọn scope này

Nếu đi theo hướng trên, ATP sẽ đạt được:

- current-task operational state rõ hơn và ít suy diễn hơn
- `continue_pending` có resume contract hẹp nhưng usable
- traceability giữa run tree, exchange, continuation, và current pointer ổn định hơn
- nền tảng tốt hơn cho các phase sau mà không phá boundary discipline đã freeze

## 6. Recommendation summary

Khuyến nghị chính thức:

ATP v0.4 nên chọn **current-task persistence + continue-pending recovery hardening** làm scope trung tâm.

CLI inspect hoặc index hardening chỉ nên đi kèm ở mức nhỏ để phục vụ scope này, không tách thành initiative rộng.
