# ATP v1.0 Slice D Decision Traceability Model

## 1. Mục đích

Tài liệu này định nghĩa traceability model của `ATP v1.0 Slice D` để ATP có thể reconstruct đầy đủ đường đi từ continuity state tới decision, permission/block result, transition, và resulting state / move.

Traceability model này tồn tại để:

- làm rõ minimum trace ATP phải giữ ở Slice D
- chặn các decision hoặc transition không đủ audit basis
- đảm bảo integration review, consolidation, freeze-readiness, và close-out của Slice D có evidence thật

## 2. Traceability chain definition

Traceability chain chuẩn của Slice D là:

`source state`
-> `decision actor / authority`
-> `decision rationale`
-> `permission / block result`
-> `transition`
-> `resulting state / move`

Trong ATP lineage hiện tại, `source state` của Slice D phải trace ngược về:

- `finalization / closure record`
- `review / approval gate`
- `gate outcome / operational follow-up`
- `operational continuity / gate follow-up state`

## 3. Minimum trace unit

`Minimum trace unit` của Slice D là đơn vị nhỏ nhất đủ để một reviewer hiểu và reconstruct một decision-controlled transition.

Một minimum trace unit phải có tối thiểu:

- source state identifier hoặc source state contract reference
- decision record identifier
- decision actor / authority source
- decision class
- requested transition
- permission / block result
- resulting state / move hoặc resulting status
- rationale summary
- evidence summary

Nếu thiếu một trong các trường này, trace unit bị coi là không hoàn chỉnh.

## 4. Decision record expectations

Mỗi decision record của Slice D phải đáp ứng tối thiểu:

- reference tới source state
- decision actor hoặc authority source explicit
- decision class explicit:
  - `observational decision`
  - `advisory decision`
  - `conditional binding decision`
  - `blocking decision`
- decision rationale summary
- evidence sufficiency summary
- requested transition explicit
- decision result explicit:
  - `allow`
  - `conditional`
  - `defer`
  - `block`
  - `loop-back`

Decision record không đạt nếu:

- decision class không rõ
- authority không rõ
- rationale chỉ là nhận xét mơ hồ
- requested transition không explicit
- decision result không explicit

## 5. Transition record expectations

Mỗi transition record của Slice D phải có:

- source state reference
- decision record reference
- transition class explicit:
  - `allowed transition`
  - `conditional transition`
  - `deferred transition`
  - `blocked transition`
  - `loop-back transition`
- permission / block basis
- resulting state / move explicit
- status summary sau transition

Transition record không đạt nếu:

- transition class không rõ
- resulting state / move không rõ
- không trace được decision record đã tạo transition
- không rõ transition bị permit hay bị block vì lý do gì

## 6. Evidence sufficiency

`Evidence sufficiency` ở Slice D phải đủ để trả lời các câu hỏi:

- source state nào đang được dùng
- ai hoặc authority nào đang ra decision
- decision đó thuộc class nào
- decision đó có đủ thẩm quyền hay không
- transition nào đang được xin phép hoặc bị chặn
- resulting state / move nào đang được tạo ra hoặc bị từ chối

Evidence đủ tối thiểu khi:

- source state traceable tới Slice C
- authority traceable
- rationale có nội dung kiểm chứng được
- requested transition và resulting state / move đều explicit

Evidence bị coi là không đạt khi:

- chỉ có kết luận mà không có rationale
- chỉ có authority wording mà không có authority basis
- chỉ có transition wording mà không có source state
- chỉ có resulting state nhưng không trace được decision path

## 7. Audit reconstruction rule

Audit reconstruction của Slice D phải cho phép reviewer đi theo cả hai hướng:

### 7.1 Forward reconstruction
Từ source state, reviewer phải reconstruct được:

`source state`
-> `decision actor / authority`
-> `decision rationale`
-> `permission / block result`
-> `transition`
-> `resulting state / move`

### 7.2 Backward reconstruction
Từ resulting state / move, reviewer phải reconstruct ngược được:

`resulting state / move`
-> `transition`
-> `decision result`
-> `decision record`
-> `source state`
-> prior lineage về Slice A / B / C

Nếu một trong hai chiều reconstruct không làm được, traceability của Slice D bị coi là không đạt audit-grade.

## 8. Traceability failure conditions

Traceability của Slice D bị coi là fail trong các trường hợp sau:

- decision không link tới source state
- transition không link tới decision
- resulting state / move không link tới transition
- authority không trace được
- rationale không đủ để giải thích permission/block result
- evidence summary quá mơ hồ để audit
- wording dùng lẫn giữa advisory và binding

## 9. Relation với governance, freeze, và audit

Traceability không chỉ là technical nicety. Trong ATP, nó là điều kiện governance.

Quan hệ với governance:

- governance-grade baseline yêu cầu decision path reconstruct được
- thiếu trace đồng nghĩa thiếu basis để consolidate hoặc freeze

Quan hệ với freeze-readiness:

- Slice D không thể freeze-ready nếu decision/transition trace chain bị đứt
- freeze-readiness chỉ hợp lệ khi trace đủ để chứng minh ATP đang kiểm soát transition, không chỉ ghi trạng thái

Quan hệ với audit:

- audit phải xác nhận được source state, authority, rationale, permission/block result, transition, và resulting state / move
- nếu reconstruct không làm được, audit không thể tin transition discipline của Slice D

## 10. Freeze-readiness implications

Slice D chỉ nên được coi là ready cho freeze-readiness khi:

- minimum trace unit đã đủ rõ
- decision record expectations đã operational
- transition record expectations đã operational
- evidence sufficiency không còn mơ hồ
- audit reconstruction làm được theo cả hai chiều

Ngược lại, Slice D chưa freeze-ready nếu:

- trace chain chỉ dừng ở state và decision
- permission / block result không explicit
- resulting state / move không explicit
- authority model chưa trace được

## 11. Kết luận

`ATP v1.0 Slice D Decision Traceability Model` biến decision discipline của Slice D thành một trace chain kiểm chứng được:

`source state`
-> `decision actor / authority`
-> `rationale`
-> `permission / block result`
-> `transition`
-> `resulting state / move`

Đây là điều kiện bắt buộc để Slice D có thể đi tiếp qua integration review, consolidation, freeze-readiness, và close-out mà không drift khỏi ATP governance discipline.
