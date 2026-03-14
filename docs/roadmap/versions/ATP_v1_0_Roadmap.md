# ATP v1.0 Roadmap

## 1. Roadmap position

`v1.0` là version roadmap đầu tiên trong major family `v1`.

`v1.0` không phải major reset. Nó là major continuation đầu tiên sau `v0.7.0`, với vai trò:

- operational maturity baseline
- post-`v0` foundational completion continuation
- controlled operationalization
- khởi đầu cho major-transition đã được qualification qua `v0.7.0`

## 2. Inherited direction từ `v0.7.0`

`v1.0` phải kế thừa từ:

- `v0.7.0` freeze baseline
- `ATP_v0_7_Integration_Review.md`
- `ATP_v0_7_Consolidation_Decision.md`
- `ATP_v0_7_Freeze_Readiness_Assessment.md`
- `ATP_v0_7_Freeze_Decision.md`
- `ATP_v0_7_0_Freeze_Closeout.md`
- product roadmap, `v0` major roadmap, và `v1` major roadmap active

Điểm kế thừa cốt lõi là:

- `v0.5.0` đã harden foundational request-to-product execution chain
- `v0.6.0` đã harden foundational closure chain
- `v0.7.0` đã harden finalization / closure record seam cuối của `v0`
- bước tiếp theo phải bắt đầu operational maturity trên stable core, không kéo dài thêm `v0.x`

## 3. Version goal

Mục tiêu của `v1.0` là mở major family `v1` như operational maturity baseline đầu tiên của ATP, bằng cách contract hóa một review / approval gate layer bounded trên nền lifecycle chain đã hoàn tất ở `v0`.

`v1.0` vì vậy là version của controlled operationalization, không phải breadth expansion.

## 4. Vì sao `v1.0` tồn tại

Sau `v0.7.0`, ATP đã có một foundational lifecycle chain đủ coherent từ request tới finalization / closure record. Điều còn thiếu không còn là seam nền tảng của `v0`, mà là một operational gate layer rõ cho câu hỏi:

- ATP ghi explicit review / approval gate nào
- gate đó nằm ở đâu sau finalization / lifecycle continuity hiện có
- gate đó khác gì với approval UI, recovery engine, hay orchestration rộng

Gap này đủ để justify một major horizon mới vì nó chuyển trọng tâm từ foundational seam hardening sang operational maturity contracts.

## 5. Vì sao `v0.x` nên dừng ở `v0.7.0`

`v0.x` nên dừng ở `v0.7.0` vì:

- foundational request-to-product execution chain đã được chốt
- foundational closure chain đã được chốt
- foundational finalization / closure record seam đã được chốt
- bước tiếp theo không còn chỉ là “thêm một contract để hoàn tất lifecycle nền tảng”

Nếu tiếp tục kéo dài `v0.x`, ATP sẽ làm mờ boundary giữa foundational family và operational maturity family.

## 6. Maturity boundary đã đổi như thế nào giữa `v0` và `v1`

Khác biệt chính là:

- `v0` tập trung vào shape correctness, boundary discipline, artifact lifecycle, và foundational chain completion
- `v1` bắt đầu tập trung vào operational contracts dùng để kiểm soát và đánh giá lifecycle đã hoàn tất ở mức nền

Nói ngắn gọn:

- `v0` trả lời “ATP có một lifecycle chain nền tảng coherent hay chưa”
- `v1` bắt đầu trả lời “ATP có operational gate đủ rõ để vận hành chain đó một cách đáng tin hơn hay chưa”

## 7. Capability gap mà `v1.0` cần address

Capability gap của `v1.0` là thiếu một `review / approval gate` layer rõ, bounded, file-based, và traceable sau finalization / closure record.

Gap này nằm ở vùng semantics giữa:

- finalization / closure record đã có
- review / approval gate ATP cần ghi nhận
- operational decision boundary cần tồn tại trước khi nghĩ tới approval UI hay orchestration rộng hơn

Gap này không phải:

- approval UI gap
- provider routing gap
- recovery execution gap
- distributed control gap
- portfolio orchestration gap

## 8. `v1.0` phải unlock điều gì cho `v1` major roadmap

`v1.0` phải unlock:

- một operational gate boundary rõ hơn sau finalization layer
- một review / approval gate contract đủ bounded để nối lifecycle continuity với operational gate semantics
- cơ sở rõ hơn để harden operational maturity mà không mở breadth mới
- evidence rằng `v1` có thể tăng độ tin cậy vận hành trên stable core của `v0`

## 9. Must-have

- planning baseline rõ cho operational maturity của `v1`
- explicit framing rằng `v1.0` không phải architecture reset
- Slice A `Review / Approval Gate Contract`
- boundary semantics rõ giữa review / approval gate với approval UI, recovery engine, routing, và broader orchestration
- freeze/integration criteria vẫn bám controlled operationalization, không drift thành v2-style breadth

## 10. Good-to-have

Nếu còn capacity, `v1.0` có thể mở thêm:

- wording cleanup nhỏ giữa finalization semantics của `v0` và operational gate semantics của `v1`
- traceability alignment tốt hơn giữa `v0.7` finalization record và review / approval gate
- clarification tốt hơn cho threshold phân biệt `v1` operational maturity với `v2` orchestration breadth

## 11. Deferred areas

Vẫn defer beyond `v1.0` nếu chưa có evidence đủ mạnh:

- provider arbitration engine
- cost-aware routing expansion
- topology-aware orchestration
- approval UI hoặc broad operator surface
- recovery execution
- distributed control
- generalized orchestration engine hoặc portfolio orchestration
- broad `v2` functionality chưa có operational maturity evidence đủ mạnh

## 12. Slice structure

`v1.0` mở với một first slice rõ ràng:

1. Slice A: Review / Approval Gate Contract

Các slices tiếp theo, nếu có, chỉ nên được mở sau khi Slice A được implement và review, và chỉ khi chúng vẫn chứng minh được là controlled operationalization của `v1`, không phải breadth expansion.

## 13. Slice A — Review / Approval Gate Contract

Slice A của `v1.0` phải trả lời:

- ATP đang ghi explicit review / approval gate nào
- gate đó nằm ở đâu tương đối với `finalization / closure record` của `v0.7`
- gate đó nối thế nào với lifecycle continuity đã có
- gate đó traceable thế nào tới finalization chain của `v0`

Slice này phải giữ rõ separation với:

- approval UI
- recovery engine
- routing
- provider selection
- broader orchestration

Nó chỉ nên harden một `review / approval gate contract`, không biến ATP thành operator UI hay workflow engine mới.

## 14. Freeze criteria

`v1.0` chỉ nên được coi là freeze-ready nếu:

- scope thực tế vẫn nằm trong operational maturity horizon của current `v1`
- `Review / Approval Gate Contract` đủ bounded, explicit, và file-based
- docs và implementation vẫn bám stable core + controlled evolutionary governance doctrine
- có integration review / consolidation pass rõ ràng
- có consolidation decision rõ ràng
- README alignment được xử lý ở đúng level đã thay đổi

## 15. Integration criteria

`v1.0` chỉ nên integrate vào `main` nếu:

- evidence cho controlled operationalization scope là đủ
- active docs, roadmap docs, và close-out chain không mâu thuẫn nhau
- không có blocker về boundary correctness hoặc governance continuity
- narrative của `v1.0` vẫn là operational maturity baseline, không drift thành uncontrolled breadth expansion
