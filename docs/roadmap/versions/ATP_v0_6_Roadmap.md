# ATP v0.6 Roadmap

## 1. Roadmap position

`v0.6` là version roadmap tiếp theo trong current `v0` major family.

`v0.6` không phải major reset. Nó là minor continuation sau `v0.5.0`, với vai trò:

- foundational closure
- post-v0.5 continuation
- transition-readiness preparation cho `v1`

## 2. Inherited direction từ v0.5.0

`v0.6` phải kế thừa từ:

- `v0.5.0` freeze baseline
- `ATP_v0_5_Integration_Review.md`
- `ATP_v0_5_Consolidation_Decision.md`
- `ATP_v0_5_Freeze_Readiness_Assessment.md`
- `ATP_v0_5_Freeze_Decision.md`
- `ATP_v0_5_0_Freeze_Closeout.md`
- product roadmap và `v0` major roadmap active

Điểm kế thừa cốt lõi là:

- `v0.5.0` đã harden request-to-product execution chain tới bounded execution result
- `v0` vẫn chưa nên nhảy sang `v1` nếu phần closure sau execution chưa được contract hóa rõ
- bước tiếp theo phải tiếp tục làm mạnh trục `requested user ⇄ ATP ⇄ products`, không mở breadth mới

## 3. Version goal

Mục tiêu của `v0.6` là đóng nốt các foundational gaps còn lại ngay sau bounded execution result, để `v0` tiến gần hơn tới coherent closure boundary và đủ evidence cho transition-readiness sang `v1`.

`v0.6` vì vậy là version của foundational closure, không phải version của breadth expansion.

## 4. Vì sao `v0.6` tồn tại

Sau `v0.5.0`, ATP đã có chain contract rõ từ request tới bounded execution result. Tuy vậy, baseline hiện tại vẫn còn thiếu một lớp contract rõ cho câu hỏi:

- sau execution result thì ATP đang ghi nhận quyết định bounded nào
- quyết định đó nối thế nào tới `close`, `close_rejected`, `continue_pending`, hoặc một trạng thái review escalation bounded
- quyết định đó khác gì với approval UI, recovery engine, hay orchestration rộng

Nếu bước này chưa được harden, `v0` vẫn còn một gap giữa execution result và closure semantics. Gap đó còn đủ nhỏ để vẫn thuộc `v0`, nên `v1.0` chưa phải bước đúng ở thời điểm này.

## 5. Vì sao `v1.0` chưa phải bước tiếp theo đúng

`v1.0` chưa nên mở khi:

- closure semantics sau execution vẫn chưa được contract hóa rõ
- evidence cho maturity boundary của `v0` vẫn chưa đủ
- ATP còn đang harden seams nền tảng thay vì đòi một capability horizon mới

Nói ngắn gọn, `v0.6` tồn tại để hoàn tất nốt phần foundational closure mà `v0.5.0` chưa chốt xong, thay vì đẩy ATP sang horizon mới quá sớm.

## 6. Capability gap mà `v0.6` cần address

Capability gap của `v0.6` là thiếu một `post-execution decision` layer rõ, bounded, file-based, và traceable sau Slice D.

Gap này nằm ở vùng semantics giữa:

- execution result đã có
- quyết định bounded ATP ghi nhận sau execution
- close / close_rejected / continue_pending / review escalation semantics

Gap này không phải:

- provider routing gap
- approval UI gap
- recovery execution gap
- distributed control gap

## 7. `v0.6` phải unlock điều gì cho `v0` major roadmap

`v0.6` phải unlock:

- một closure boundary rõ hơn ngay sau execution result
- một decision contract đủ bounded để nối execution result với close/continue semantics
- cơ sở tốt hơn để đánh giá `v0` đã đủ coherent maturity boundary hay chưa
- transition-readiness evidence cho `v1`, thay vì chỉ thêm runtime detail rời rạc

## 8. Must-have

- planning baseline rõ cho foundational closure của `v0`
- explicit framing rằng `v0.6` không phải breadth expansion
- Slice A `Post-Execution Decision Contract`
- boundary semantics rõ giữa post-execution decision với approval UI, recovery engine, routing, và broader orchestration
- freeze/integration criteria vẫn bám current `v0` horizon

## 9. Good-to-have

Nếu còn capacity, `v0.6` có thể mở thêm:

- wording cleanup nhỏ giữa closure semantics và release-track docs
- traceability alignment tốt hơn giữa execution-result contract và close/continue path
- clarification tốt hơn cho maturity criteria của `v0 -> v1`

## 10. Deferred areas

Vẫn defer beyond `v0.6` nếu chưa có evidence đủ mạnh:

- provider arbitration engine
- cost-aware routing expansion
- topology-aware orchestration
- approval UI hoặc broad operator surface
- recovery execution
- distributed control
- generalized orchestration engine hoặc portfolio orchestration
- broad `v1` functionality chưa có transition evidence đủ mạnh

## 11. Slice structure

`v0.6` mở với một first slice rõ ràng:

1. Slice A: Post-Execution Decision Contract

Các slices tiếp theo, nếu có, chỉ nên được mở sau khi Slice A được implement và review, và chỉ khi chúng vẫn chứng minh được là foundational closure của `v0`, không phải mở rộng breadth.

## 12. Slice A — Post-Execution Decision Contract

Slice A của `v0.6` phải trả lời:

- ATP đang ghi nhận bounded decision nào sau execution result
- decision đó nối thế nào tới `close`, `close_rejected`, `continue_pending`, và `escalate_review` hoặc bounded review-escalation semantics tương đương
- decision đó traceable thế nào tới Slice D execution result contract

Slice này phải giữ rõ separation với:

- approval UI
- recovery engine
- routing
- provider selection
- broader orchestration

Nó chỉ nên harden một `post-execution decision contract`, không biến ATP thành workflow engine mới.

## 13. Freeze criteria

`v0.6` chỉ nên được coi là freeze-ready nếu:

- scope thực tế vẫn nằm trong current `v0` capability horizon
- `Post-Execution Decision Contract` đủ bounded, explicit, và file-based
- docs và implementation vẫn bám stable core + controlled evolutionary governance doctrine
- có integration review / consolidation pass rõ ràng
- có consolidation decision rõ ràng
- README alignment được xử lý ở đúng level đã thay đổi
- evidence cho transition-readiness của `v0 -> v1` rõ hơn sau `v0.6`, dù chưa tự động mở `v1`

## 14. Integration criteria

`v0.6` chỉ nên integrate vào `main` nếu:

- evidence cho foundational closure scope là đủ
- active docs, roadmap docs, và close-out chain không mâu thuẫn nhau
- không có blocker về boundary correctness hoặc governance continuity
- narrative của `v0.6` vẫn là foundational closure, không drift thành breadth expansion
