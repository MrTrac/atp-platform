# ATP v1.0 Slice E Closure State Model

## 1. Mục đích

Tài liệu này định nghĩa closure state model cho `ATP v1.0 Slice E`, để ATP có thể diễn giải resulting operational state và move closure theo cách bounded, audit-friendly, và không nhập nhằng với workflow execution.

## 2. Source input từ Slice D

Slice E dùng các input tối thiểu từ Slice D:

- `source state`
- `decision actor / authority`
- `decision class`
- `decision result`
- `transition class`
- `transition rationale`
- `resulting state / move` ở mức transition output

Slice E không tự tạo decision authority mới. Slice E chỉ dùng Slice D như input contract anchor để chốt closure interpretation.

## 3. Closure-state categories

Slice E chuẩn hóa bốn closure-state categories:

- `provisional_result_state`
- `acknowledged_result_state`
- `unresolved_result_state`
- `closed_result_state`

## 4. Ý nghĩa của từng category

### 4.1 `provisional_result_state`
Được dùng khi:

- transition đã sinh ra một resulting direction
- resulting state candidate đã thấy rõ
- ATP chưa có đủ basis để ghi acknowledgment ổn định

### 4.2 `acknowledged_result_state`
Được dùng khi:

- resulting state explicit
- linkage về source state, decision, và transition đủ
- ATP cần ghi nhận result này như một state đã được nhận diện hợp lệ

### 4.3 `unresolved_result_state`
Được dùng khi:

- resulting state đã explicit hoặc đã được acknowledge
- closure chưa thể complete vì còn unresolved guard, hold, clarification gap, hoặc pending closure condition

### 4.4 `closed_result_state`
Được dùng khi:

- resulting state explicit
- move closure explicit
- closure basis đủ để boundedly conclude move đã khép

## 5. Closure categories

Bên cạnh state categories, Slice E dùng closure categories sau:

- `intermediate_result`
- `acknowledged_move`
- `unresolved_move`
- `closed_move`

State category và closure category phải đi cùng nhau một cách nhất quán:

- `provisional_result_state` <-> `intermediate_result`
- `acknowledged_result_state` <-> `acknowledged_move`
- `unresolved_result_state` <-> `unresolved_move`
- `closed_result_state` <-> `closed_move`

## 6. Khi nào state là provisional / acknowledged / closed / unresolved

### 6.1 Provisional
State là provisional khi:

- Slice D đã có decision/transition result
- resulting state mới ở mức candidate interpretation
- acknowledgment chưa đủ basis

### 6.2 Acknowledged
State là acknowledged khi:

- source state traceable
- decision result traceable
- transition traceable
- resulting state summary explicit
- ATP chấp nhận rằng result này đã tồn tại như một record hợp lệ

### 6.3 Unresolved
State là unresolved khi:

- resulting state đã thấy rõ
- ATP chưa thể coi move là closed
- unresolved condition vẫn còn active

### 6.4 Closed
State là closed khi:

- acknowledgment đã có
- closure basis explicit
- không còn unresolved/hold condition active trong boundary hiện hành

## 7. Allowed transitions giữa các closure/result states

Các transition được phép trong Slice E:

- `provisional_result_state -> acknowledged_result_state`
- `provisional_result_state -> unresolved_result_state`
- `acknowledged_result_state -> unresolved_result_state`
- `acknowledged_result_state -> closed_result_state`
- `unresolved_result_state -> acknowledged_result_state`
- `unresolved_result_state -> closed_result_state`

Diễn giải:

- provisional có thể đi sang acknowledged nếu acknowledgment basis đạt
- provisional có thể đi thẳng sang unresolved nếu ATP thấy kết quả nhưng closure gap cũng đã explicit
- acknowledged có thể đi sang unresolved nếu phát hiện closure chưa complete
- acknowledged có thể đi sang closed nếu closure basis đã đủ
- unresolved có thể quay về acknowledged khi unresolved condition đã được thu hẹp nhưng closure vẫn chưa complete
- unresolved có thể đi sang closed khi unresolved condition không còn active

## 8. Forbidden closure interpretations

Các diễn giải sau là forbidden:

- `allowed transition` của Slice D tự động đồng nghĩa với `closed_result_state`
- `blocked transition` tự động đồng nghĩa với `closed_move`
- `acknowledged_result_state` bị diễn giải như full execution complete
- `unresolved_result_state` bị mô tả như workflow backlog engine state
- `loop-back transition` bị mô tả như recovery executor

## 9. Practical review matrix

| Source from Slice D | Resulting-state interpretation | Closure interpretation | Governance reading |
| --- | --- | --- | --- |
| `allowed transition` với closure basis chưa đủ | `provisional_result_state` hoặc `acknowledged_result_state` | `intermediate_result` hoặc `acknowledged_move` | Move có thể đi đúng hướng nhưng chưa chắc đã closed |
| `allowed transition` với closure basis đủ | `closed_result_state` | `closed_move` | Result đã được neo và bounded closure đạt |
| `conditional transition` | `provisional_result_state` hoặc `unresolved_result_state` | `intermediate_result` hoặc `unresolved_move` | Chưa đủ để close vì còn điều kiện active |
| `deferred transition` | `unresolved_result_state` | `unresolved_move` | Result direction bị hoãn ở lớp closure |
| `blocked transition` | không tạo `closed_result_state` mặc định | không tự động tạo `closed_move` | Block là permission outcome, không phải closure outcome |
| `loop-back transition` | `unresolved_result_state` | `unresolved_move` | Cần quay lại clarification path, chưa phải closure |

## 10. Governance / audit usable state model

Để usable cho governance và audit, mỗi state trong Slice E phải trả lời được:

- state này phát sinh từ source state nào
- decision nào của Slice D dẫn tới interpretation hiện tại
- transition nào đang được closure layer diễn giải
- vì sao state đang là provisional, acknowledged, unresolved, hoặc closed
- closure class nào đang đúng

## 11. Anti-drift guardrails

Slice E state model phải giữ:

- state categories là closure semantics, không phải workflow runtime stages
- không gán execution meaning vượt quá contract boundary
- không dùng `closed_result_state` để suy diễn platform execution đã hoàn tất
- không dùng `unresolved_result_state` để mở subsystem mới
- không chuyển ngầm model này thành design foundation cho `v1.1`

## 12. Kết luận

Closure state model của Slice E biến kết quả sau Slice D thành một state model bounded:

- đủ rõ để review
- đủ chặt để audit
- đủ hẹp để không drift sang engine design

Model này là lớp chốt meaning cho `resulting operational state / move closure`, không nhiều hơn và không ít hơn.
