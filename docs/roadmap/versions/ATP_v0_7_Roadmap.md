# ATP v0.7 Roadmap

## 1. Roadmap position

`v0.7` là version roadmap tiếp theo trong current `v0` major family.

`v0.7` không phải major reset. Nó là minor continuation sau `v0.6.0`, với vai trò:

- foundational finalization
- post-`v0.6.0` continuation
- major-transition qualification preparation cho `v1`

## 2. Inherited direction từ v0.6.0

`v0.7` phải kế thừa từ:

- `v0.6.0` freeze baseline
- `ATP_v0_6_Integration_Review.md`
- `ATP_v0_6_Consolidation_Decision.md`
- `ATP_v0_6_Freeze_Readiness_Assessment.md`
- `ATP_v0_6_Freeze_Decision.md`
- `ATP_v0_6_0_Freeze_Closeout.md`
- product roadmap và `v0` major roadmap active

Điểm kế thừa cốt lõi là:

- `v0.5.0` đã harden foundational request-to-product execution chain tới bounded execution result
- `v0.6.0` đã harden foundational closure chain tới bounded closure / continuation state
- `v0` vẫn chưa nên nhảy sang `v1` nếu finalization / closure recording seam chưa được contract hóa rõ
- bước tiếp theo phải tiếp tục làm mạnh trục `requested user ⇄ ATP ⇄ products`, không mở breadth mới

## 3. Version goal

Mục tiêu của `v0.7` là đóng nốt seam foundational finalization còn lại của `v0`, đồng thời tạo qualification evidence rõ hơn cho quyết định `v0 -> v1`.

`v0.7` vì vậy là version của foundational finalization và major-transition qualification, không phải version của breadth expansion.

## 4. Vì sao `v0.7` tồn tại

Sau `v0.6.0`, ATP đã có closure chain bounded từ execution result tới closure / continuation state. Tuy vậy, baseline hiện tại vẫn còn thiếu một lớp contract rõ cho câu hỏi:

- khi closure path thật sự được finalize thì ATP đang ghi record chính thức nào
- record đó nối thế nào với bounded closure / continuation state từ `v0.6`
- record đó khác gì với approval UI, recovery engine, hay orchestration rộng

Nếu bước này chưa được harden, `v0` vẫn còn một seam giữa bounded closure state và finalized closure record. Gap đó vẫn đủ nhỏ để tiếp tục thuộc `v0`, nên `v1.0` chưa phải bước đúng ở thời điểm này.

## 5. Vì sao `v1.0` chưa phải bước tiếp theo đúng

`v1.0` chưa nên mở khi:

- finalization / closure record semantics vẫn chưa được contract hóa rõ
- evidence cho major-transition qualification của `v0` vẫn chưa đủ
- ATP còn đang harden seam nền tảng cuối của `v0` thay vì đòi một capability horizon mới

Nói ngắn gọn, `v0.7` tồn tại để chốt nốt seam finalization còn thiếu của `v0.6.0`, đồng thời cung cấp evidence tốt hơn cho việc kết thúc major family `v0`.

## 6. Capability gap mà `v0.7` cần address

Capability gap của `v0.7` là thiếu một `finalization / closure record` layer rõ, bounded, file-based, và traceable sau closure / continuation state contract (`v0.6` Slice C).

Gap này nằm ở vùng semantics giữa:

- closure / continuation state đã có
- record finalization / closure ATP cần ghi nhận chính thức
- close / close_rejected / continue_pending semantics ở mức finalized record

Gap này không phải:

- provider routing gap
- approval UI gap
- recovery execution gap
- distributed control gap

## 7. `v0.7` phải unlock điều gì cho `v0` major roadmap

`v0.7` phải unlock:

- một finalization boundary rõ hơn sau closure / continuation state
- một closure record contract đủ bounded để nối state semantics với finalized record semantics
- cơ sở rõ hơn để đánh giá `v0` đã đạt major-transition qualification hay chưa
- evidence tốt hơn để xác nhận bước tiếp theo có còn là minor hardening hay đã thật sự đòi horizon `v1`

## 8. Must-have

- planning baseline rõ cho foundational finalization của `v0`
- explicit framing rằng `v0.7` không phải breadth expansion
- Slice A `Finalization / Closure Record Contract`
- boundary semantics rõ giữa finalization record với approval UI, recovery engine, routing, và broader orchestration
- freeze/integration criteria vẫn bám current `v0` horizon
- major-transition qualification logic rõ hơn cho câu hỏi khi nào `v0` đủ điều kiện sang `v1`

## 9. Good-to-have

Nếu còn capacity, `v0.7` có thể mở thêm:

- wording cleanup nhỏ giữa finalization semantics và transition-readiness docs
- traceability alignment tốt hơn giữa `v0.6` closure state và finalized closure record
- clarification tốt hơn cho evidence threshold của `v0 -> v1`

## 10. Deferred areas

Vẫn defer beyond `v0.7` nếu chưa có evidence đủ mạnh:

- provider arbitration engine
- cost-aware routing expansion
- topology-aware orchestration
- approval UI hoặc broad operator surface
- recovery execution
- distributed control
- generalized orchestration engine hoặc portfolio orchestration
- broad `v1` functionality chưa có transition evidence đủ mạnh

## 11. Slice structure

`v0.7` mở với một first slice rõ ràng:

1. Slice A: Finalization / Closure Record Contract

Các slices tiếp theo, nếu có, chỉ nên được mở sau khi Slice A được implement và review, và chỉ khi chúng vẫn chứng minh được là foundational finalization của `v0`, không phải mở rộng breadth.

## 12. Slice A — Finalization / Closure Record Contract

Slice A của `v0.7` phải trả lời:

- ATP đang ghi finalization / closure record nào khi closure path thật sự được finalize
- record đó nối thế nào với `closure / continuation state` của `v0.6`
- record đó phản ánh `close`, `close_rejected`, `continue_pending`, hoặc bounded finalized semantics tương đương như thế nào
- record đó traceable thế nào tới closure chain đã có của `v0.6`

Slice này phải giữ rõ separation với:

- approval UI
- recovery engine
- routing
- provider selection
- broader orchestration

Nó chỉ nên harden một `finalization / closure record contract`, không biến ATP thành workflow engine hay lifecycle engine mới.

## 13. Freeze criteria

`v0.7` chỉ nên được coi là freeze-ready nếu:

- scope thực tế vẫn nằm trong current `v0` capability horizon
- `Finalization / Closure Record Contract` đủ bounded, explicit, và file-based
- docs và implementation vẫn bám stable core + controlled evolutionary governance doctrine
- có integration review / consolidation pass rõ ràng
- có consolidation decision rõ ràng
- README alignment được xử lý ở đúng level đã thay đổi
- evidence cho `v0 -> v1` qualification rõ hơn sau `v0.7`, dù chưa tự động mở `v1`

## 14. Integration criteria

`v0.7` chỉ nên integrate vào `main` nếu:

- evidence cho foundational finalization scope là đủ
- active docs, roadmap docs, và close-out chain không mâu thuẫn nhau
- không có blocker về boundary correctness hoặc governance continuity
- narrative của `v0.7` vẫn là foundational finalization, không drift thành breadth expansion
