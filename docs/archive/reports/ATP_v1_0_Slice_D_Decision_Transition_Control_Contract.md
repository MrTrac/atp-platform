# ATP v1.0 Slice D Decision / Transition Control Contract

## 1. Trạng thái tài liệu

- Tài liệu: active baseline document
- Version target: `ATP v1.0.3`
- Slice: `Slice D`
- Trạng thái: proposed baseline for implementation, review, consolidation, và freeze path
- Branch baseline: `v1.0-slice-d`

## 2. Version / lineage context

`ATP v1.0 Slice D` là bước tiếp nối trực tiếp sau:

- `v1.0.0` — Slice A: `Review / Approval Gate Contract`
- `v1.0.1` — Slice B: `Gate Outcome / Operational Follow-up Contract`
- `v1.0.2` — Slice C: `Operational Continuity / Gate Follow-up State Contract`

Lineage logic hiện tại là:

`finalization / closure record`
-> `review / approval gate`
-> `gate outcome / operational follow-up`
-> `operational continuity / gate follow-up state`
-> `decision qualification`
-> `transition permission / block`
-> `next operational state / move`

Slice D không reset chain này. Slice D chỉ bổ sung lớp control-contract để ATP quyết định transition nào là hợp lệ sau khi continuity state đã được ghi nhận ở Slice C.

## 3. Executive Summary

`Operational Decision / State Transition Control Contract` là source-of-truth document của Slice D. Contract này tồn tại để ATP ghi lại một decision control layer hẹp, file-based, traceable, và audit-friendly sau Slice C, nhằm trả lời:

- ai hoặc lớp authority nào có quyền ra quyết định bước tiếp theo
- decision nào đủ qualification để làm phát sinh transition
- transition nào được phép, có điều kiện, bị chặn, bị defer, hay phải loop-back
- khi nào continuity state nhìn bề ngoài có vẻ hợp lệ nhưng transition vẫn phải bị chặn
- traceability tối thiểu nào phải tồn tại từ `state -> decision -> permission/block -> transition -> resulting state`

Slice D là một control-contract slice. Nó không phải approval UI, không phải workflow engine, không phải recovery execution layer, không phải routing/provider layer, và không phải orchestration engine.

## 4. Mục đích tài liệu

Tài liệu này được dùng để:

- xác lập semantic baseline cho Slice D
- giữ ATP `v1.0.3` bám đúng lineage của `v1.0.0` đến `v1.0.2`
- chặn scope creep khi ATP bắt đầu ghi nhận decision discipline sau continuity state
- làm authority document cho implementation, integration review, consolidation, freeze-readiness, và close-out của Slice D

## 5. Vị trí của Slice D trong ATP v1 lineage

Slice D nằm ngay sau `Operational Continuity / Gate Follow-up State Contract` của Slice C.

Placement logic:

1. `v0.7.0` chốt `finalization / closure record`.
2. Slice A thêm `review / approval gate`.
3. Slice B thêm `gate outcome / operational follow-up`.
4. Slice C thêm `operational continuity state`.
5. Slice D thêm `decision / transition control discipline` để kiểm soát bước dịch chuyển tiếp theo từ continuity state.

Slice D không thay thế Slice C. Slice D dùng Slice C như `source state anchor`.

## 6. Problem statement

Sau Slice C, ATP đã có một continuity state explicit và bounded. Tuy nhiên ATP vẫn thiếu một lớp control-contract rõ để trả lời các câu hỏi sau:

- continuity state nào thực sự đủ điều kiện để đi tiếp
- decision nào chỉ mang tính quan sát, decision nào advisory, decision nào binding có điều kiện, decision nào blocking
- authority nào là đủ để transition được phép xảy ra
- khi nào ATP phải `hold`, `block`, `escalate`, hoặc `loop-back`
- khi nào continuity state hợp lệ nhưng transition vẫn không được phép vì thiếu authority, thiếu evidence, hoặc thiếu qualification

Nếu không có Slice D, ATP sẽ có continuity state nhưng chưa có discipline để kiểm soát transition một cách governance-grade.

## 7. Scope

Slice D nằm trong scope sau:

- định nghĩa `decision authority model` cho bước sau Slice C
- định nghĩa `decision qualification rules`
- định nghĩa `state transition control rules`
- định nghĩa `guard / hold / block / escalation rules`
- định nghĩa `traceability expectations` cho decision và transition
- định nghĩa `compliance expectations` và `acceptance boundary`

Slice D chỉ làm việc ở mức control-contract semantics. Slice này không bao gồm subsystem thực thi transition.

## 8. Non-goals

Slice D không bao gồm:

- approval UI
- operator console
- workflow engine
- workflow queue
- recovery engine
- recovery execution
- provider selection
- provider arbitration
- routing expansion
- topology-aware orchestration
- distributed control
- generalized orchestration
- architecture reset
- bất kỳ planning line nào của `v1.1`

## 9. Core definitions / thuật ngữ

### 9.1 Source state
Continuity state đã được ghi ở Slice C và đang được dùng làm điểm xuất phát cho decision control.

### 9.2 Decision actor
Chủ thể phát sinh decision record. Trong Slice D, actor được hiểu ở mức traceable role hoặc authority source, không phải UI identity system.

### 9.3 Decision authority
Mức authority được gán cho decision record để xác định decision đó chỉ advisory hay có hiệu lực binding.

### 9.4 Decision qualification
Tập điều kiện tối thiểu để một decision được coi là hợp lệ cho control purpose.

### 9.5 Transition
Sự thay đổi có kiểm soát từ `source state` sang `next operational state / move`.

### 9.6 Transition class
Loại transition mà Slice D cho phép ATP ghi nhận:

- `allowed transition`
- `conditional transition`
- `deferred transition`
- `blocked transition`
- `loop-back transition`

### 9.7 Decision class
Loại decision mà Slice D cho phép ATP ghi nhận:

- `observational decision`
- `advisory decision`
- `conditional binding decision`
- `blocking decision`

## 10. Decision authority model

Slice D chuẩn hóa model authority ở mức bounded như sau:

### 10.1 Observational authority
- dùng để ghi nhận observation về continuity state
- không đủ để cho phép transition
- có thể tạo review signal nhưng không tạo permission

### 10.2 Advisory authority
- dùng để đưa ra khuyến nghị có traceability
- có thể tạo `advisory decision`
- không tự nó cho phép transition binding

### 10.3 Conditional binding authority
- cho phép tạo `conditional binding decision`
- chỉ có hiệu lực khi preconditions và evidence sufficiency đều đạt
- nếu thiếu một điều kiện bắt buộc, decision bị hạ xuống `invalid decision`

### 10.4 Blocking authority
- cho phép chặn transition
- có thể tạo `block`, `hold`, hoặc `escalation trigger`
- không tự động định nghĩa execution path; chỉ control permission boundary

### 10.5 Insufficient authority
Một decision bị coi là `insufficient authority` khi:

- actor không mang authority level phù hợp với decision class
- authority source không trace được
- decision cố tạo transition binding từ một authority chỉ ở mức observational hoặc advisory

Decision có insufficient authority phải bị coi là `invalid decision` cho transition control purpose.

## 11. Decision qualification rules

Một decision chỉ được coi là qualified khi đồng thời có:

- `source state` explicit và traceable
- decision actor / authority explicit
- decision class explicit
- decision rationale đủ tối thiểu
- required evidence đủ tối thiểu
- requested transition explicit
- decision result explicit: `allow`, `conditional`, `defer`, `block`, hoặc `loop-back`

Decision bị coi là `invalid decision` nếu rơi vào một trong các tình huống sau:

- thiếu source state reference
- thiếu authority reference
- decision class không rõ
- rationale không đủ để audit reconstruction
- requested transition không explicit
- decision conflict với transition matrix mà không có escalation basis

`Advisory decision` có thể hợp lệ như một advisory record nhưng không đủ để mở binding transition.

## 12. State transition control rules

Slice D dùng các transition classes sau:

### 12.1 Allowed transition
Được phép khi:

- source state thuộc loại cho phép đi tiếp
- decision là `conditional binding decision` hoặc stronger bounded control result
- authority hợp lệ
- evidence đủ
- không có hold/block active

### 12.2 Conditional transition
Được phép có điều kiện khi:

- direction nhìn chung là đúng
- còn một hoặc nhiều điều kiện cần xác nhận trước khi resulting state được chốt
- transition không được finalize như `allowed` cho đến khi điều kiện bổ sung đạt

### 12.3 Deferred transition
Được áp dụng khi:

- source state chưa đủ basis để đi tiếp hoặc chặn vĩnh viễn
- decision hợp lệ nhưng kết luận là chưa được phép move ngay
- ATP phải giữ traceability rằng move đã được hoãn có kiểm soát

### 12.4 Blocked transition
Được áp dụng khi:

- transition bị cấm theo matrix
- authority đủ để block
- hoặc decision qualification không đạt ở mức khiến move không thể tiếp tục

### 12.5 Loop-back transition
Được áp dụng khi:

- state cần quay lại review/follow-up/continuity clarification trước đó
- continuity state hiện tại không đủ để đi tiếp
- cần bổ sung evidence hoặc re-qualification trước khi mở move mới

Loop-back không phải recovery engine. Nó chỉ là transition result class ở mức control-contract.

## 13. Guard / hold / block / escalation rules

### 13.1 Guard
Guard là tập điều kiện bắt buộc ATP phải kiểm tra trước khi bất kỳ transition nào được ghi nhận như `allowed` hoặc `conditional`.

Guard tối thiểu gồm:

- source state explicit
- decision authority explicit
- evidence sufficiency đạt tối thiểu
- transition class explicit
- resulting state / move explicit

### 13.2 Hold
`Hold` được dùng khi:

- source state chưa sai nhưng chưa đủ basis để move
- evidence còn thiếu nhưng chưa đến mức block
- cần chờ clarification hoặc supplemental decision input

### 13.3 Block
`Block` được dùng khi:

- transition bị cấm theo matrix
- authority không đủ
- decision invalid
- evidence thiếu ở mức không thể permit move
- transition vi phạm acceptance boundary hoặc scope boundary

### 13.4 Escalation
`Escalation` được kích hoạt khi:

- decision conflict với transition matrix
- authority hiện tại không đủ nhưng issue có tác động governance đáng kể
- source state và requested transition tạo ambiguity không thể xử lý ở current layer
- có dấu hiệu drift sang workflow engine, recovery engine, hay broader orchestration

Escalation là control signal, không phải execution routing.

## 14. Traceability expectations

Slice D yêu cầu trace chain tối thiểu sau:

`source state`
-> `decision actor / authority`
-> `decision rationale`
-> `permission / block result`
-> `transition record`
-> `resulting state / move`

Traceability không đạt nếu thiếu bất kỳ mắt xích nào ở trên.

Required trace anchors tối thiểu:

- source state contract reference
- decision record identifier
- authority level / authority source
- decision class
- transition class
- required evidence summary
- permission / block result
- resulting state / move reference hoặc resulting status

## 15. Compliance expectations

Slice D được coi là compliant khi:

- terminology không drift với Slice A/B/C
- decision classes và transition classes được dùng nhất quán
- mọi binding transition đều có authority phù hợp
- advisory decision không bị dùng sai thành binding permission
- blocked / deferred / loop-back logic được trace được
- không có semantic blur sang UI, workflow engine, recovery execution, routing, hay orchestration

## 16. Acceptance boundary

Slice D chỉ nên được coi là đạt baseline khi:

- ATP có source-of-truth contract rõ cho decision / transition control
- transition matrix đủ để audit practical review
- traceability model đủ để reconstruct decision path
- scope/non-goals đủ rõ để chặn drift
- execution plan đủ nối với pattern integration review -> consolidation -> freeze-readiness -> close-out

Slice D chưa được coi là đạt nếu:

- authority model còn mơ hồ
- transition classes chưa usable
- advisory/binding/blocking boundary chưa rõ
- traceability model không reconstruct được path
- wording drift sang future architecture hay `v1.1`

## 17. Quan hệ với Slice A / B / C

### 17.1 Quan hệ với Slice A
Slice A định nghĩa `review / approval gate`. Slice D không thay thế gate.

### 17.2 Quan hệ với Slice B
Slice B định nghĩa `gate outcome / operational follow-up`. Slice D không thay thế follow-up.

### 17.3 Quan hệ với Slice C
Slice C định nghĩa `operational continuity state`. Slice D dùng state đó làm `source state` để quyết định transition có được phép hay không.

Nói ngắn gọn:

- Slice A: gate exists
- Slice B: gate produces bounded follow-up
- Slice C: follow-up yields bounded continuity state
- Slice D: continuity state now gets decision qualification and transition control

## 18. Anti-drift discipline

Slice D phải giữ các discipline sau:

- không chuyển ATP thành workflow engine
- không biến decision contract thành execution engine
- không biến transition matrix thành orchestration plan
- không dùng wording của advisory như binding authority
- không dùng continuity validity như permission tự động cho transition
- không kéo current `v1.0.3` baseline sang `v1.1` semantics

Một continuity state có thể nhìn hợp lệ nhưng transition vẫn phải bị chặn nếu:

- authority không đủ
- evidence không đủ
- requested transition bị cấm
- decision class không tương thích với requested transition
- escalation chưa được giải quyết

## 19. Forward linkage trong major line `v1.0`

Slice D mở forward linkage rất chặt cho các bước tiếp theo trong cùng major/version line nếu chúng thực sự cần thiết, nhưng không mở `v1.1`.

Forward linkage được phép chỉ ở mức:

- harden decision record shape
- harden resulting state / move traceability
- harden bounded transition compliance

Forward linkage không bao gồm:

- roadmap reset
- workflow engine rollout
- recovery engine rollout
- orchestration platform rollout
- future minor-line planning ngoài `v1.0`

## 20. Kết luận

Slice D là bước hợp lệ tiếp theo của ATP `v1.0.3` vì nó tiếp tục harden operational maturity theo đúng lineage đã chốt:

`gate`
-> `follow-up`
-> `continuity state`
-> `decision qualification`
-> `transition control`

Nó là control-contract slice hẹp, audit-friendly, governance-grade, và không phải capability expansion.
