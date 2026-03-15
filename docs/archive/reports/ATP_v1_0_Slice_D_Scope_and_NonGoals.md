# ATP v1.0 Slice D Scope and Non-Goals

## 1. Why Slice D exists

Slice D tồn tại vì sau Slice C ATP đã có `operational continuity state`, nhưng vẫn chưa có một control-contract rõ để kiểm soát:

- decision nào đủ qualification để đi tiếp
- authority nào là đủ
- transition nào được phép hoặc bị chặn
- khi nào phải `hold`, `block`, `defer`, hoặc `escalate`

Slice D vì vậy là bước hợp lý tiếp theo trong cùng lineage `v1.0`:

- Slice A: gate
- Slice B: outcome / follow-up
- Slice C: continuity state
- Slice D: decision / transition control

## 2. What Slice D includes

Slice D bao gồm:

- decision authority model
- decision qualification rules
- transition control rules
- transition classes
- guard / hold / block / escalation semantics
- traceability requirements từ state -> decision -> transition -> resulting state
- baseline execution plan để đưa Slice D qua review, consolidation, freeze-readiness, và close-out

## 3. What Slice D excludes

Slice D không bao gồm:

- approval UI
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
- platform capability expansion
- architecture redesign
- roadmap redesign

## 4. Boundary with Slice C

Boundary với Slice C phải được giữ rõ:

- Slice C ghi `operational continuity state`
- Slice D dùng state đó như `source state` cho decision control

Slice D không thay thế Slice C và không được viết như thể Slice C đã bao gồm decision discipline.

Nói ngắn gọn:

- Slice C trả lời: ATP đang ở continuity state nào
- Slice D trả lời: ATP có được phép chuyển từ state đó sang bước tiếp theo hay không

## 5. Boundary with Slice A và Slice B

Boundary với Slice A:

- Slice A định nghĩa `review / approval gate`
- Slice D không tái định nghĩa gate

Boundary với Slice B:

- Slice B định nghĩa `gate outcome / operational follow-up`
- Slice D không tái định nghĩa follow-up

Slice D chỉ dùng kết quả của Slice A/B/C như prior chain inputs.

## 6. Boundary with later v1.0 slices

Slice D là `control-contract slice`.

Điều đó có nghĩa:

- Slice D có thể làm rõ decision discipline và transition control
- Slice D không tự động mở future slice nếu chưa có proven gap

Nếu về sau có slice tiếp theo trong `v1.0`, slice đó chỉ được justified khi:

- có evidence rằng current Slice D baseline vẫn còn gap bounded
- gap đó không biến ATP thành broader orchestration system

## 7. Boundary with future v1.1 planning

Slice D không phải:

- `v1.1-planning`
- bước khởi động minor-line mới
- justification để mở roadmap mới

Slice D vẫn nằm hoàn toàn trong current `v1.0` line và chỉ harden operational maturity theo lineage đã chốt.

Mọi wording hoặc planning đụng tới `v1.1` đều nằm ngoài scope tài liệu này.

## 8. Slice D là gì về bản chất

Slice D là:

- control-contract slice
- decision discipline slice
- state transition control slice
- governance-grade operational hardening slice

Slice D không phải:

- execution engine implementation slice
- platform capability expansion slice
- roadmap/new architecture slice

## 9. In-scope examples

Các ví dụ in-scope:

- định nghĩa `observational decision` khác gì với `conditional binding decision`
- định nghĩa khi nào `approved_continuity_ready` vẫn phải bị block vì thiếu authority
- định nghĩa `allowed transition` khác gì với `conditional transition`
- định nghĩa khi nào phải `loop-back` về clarification path
- định nghĩa traceability chain tối thiểu cho decision-controlled transition
- định nghĩa matrix cấm reopen một `rejected_continuity_closed` state nếu không có exception basis

## 10. Out-of-scope examples

Các ví dụ out-of-scope:

- thiết kế approval dashboard
- triển khai workflow assignment queue
- tạo recovery executor
- điều phối provider/model routing
- xây orchestration graph
- định nghĩa distributed state controller
- mở planning cho `v1.1`
- hợp nhất ATP thành broad control plane mới

## 11. Scope creep guardrails

Các guardrails bắt buộc của Slice D:

- không dùng từ ngữ của workflow engine để mô tả transition control
- không dùng từ ngữ của execution engine để mô tả decision result
- không xem `loop-back` như recovery execution
- không xem `conditional transition` như orchestration plan
- không suy diễn rằng mọi continuity state hợp lệ đều có thể đi tiếp

## 12. Kết luận

Slice D tồn tại để ATP đi từ:

`có continuity state`

sang:

`có decision discipline và transition control cho continuity state`

Đó là hardening hợp lệ trong cùng `v1.0` line. Nó không phải capability expansion và không phải roadmap mới.
