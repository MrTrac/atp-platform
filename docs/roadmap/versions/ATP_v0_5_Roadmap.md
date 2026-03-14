# ATP v0.5 Roadmap

## 1. Roadmap position

`v0.5` là một version roadmap thuộc current `v0` major family.

Nó không phải “the next thing to build” theo nghĩa ad hoc. Nó là một guided step để giúp `v0` tiến gần hơn tới coherent maturity boundary mà vẫn giữ stable core và controlled evolutionary governance.

## 2. Inherited direction từ v0.4

`v0.5` phải kế thừa từ:

- `v0.4.0` freeze baseline
- `ATP_v0_4_Integration_Review.md`
- `ATP_v0_4_Consolidation_Decision.md`
- `ATP_v0_4_0_Freeze_Closeout.md`
- product roadmap và v0 major roadmap active

Điểm kế thừa cốt lõi là:

- current-task hardening đã có baseline đủ coherent
- next step của `v0` không nên là ad hoc feature extension
- v0.5 phải giúp làm rõ next capability direction của `v0`, chứ không chỉ nối thêm runtime details rời rạc
- ATP phải giữ trục `requested user ⇄ ATP ⇄ products` như filter cho mọi bước phát triển tiếp theo

## 3. Version goal

Mục tiêu của `v0.5` là harden một foundational request-to-product execution chain có contract rõ, file-based, và traceable, nhưng vẫn nằm gọn trong current `v0` major horizon.

`v0.5` không mở broad runtime subsystem mới. Nó chỉ làm rõ các bước trung gian giữa request intent và bounded execution result, để ATP nối `requested user ⇄ ATP ⇄ products` mạch lạc hơn ở mức nền.

## 4. Capability gap mà v0.5 cần address

Capability gap của `v0.5` là thiếu một contract chain rõ giữa:

- request intent đã được resolve về product/capability
- bounded handoff intent mà ATP chuẩn bị
- execution preparation package trước routing/provider selection
- bounded execution result được ghi lại sau bước execution

Nếu gap này không được address, ATP sẽ tiếp tục dựa quá nhiều vào legacy payloads rời rạc giữa resolution, handoff, execution preparation, và execution result; như vậy trục `requested user ⇄ ATP ⇄ products` vẫn chưa đủ explicit ở mức contract chain.

## 5. v0.5 phải unlock điều gì cho v0 major roadmap

`v0.5` phải unlock:

- một request-to-product execution chain rõ và có traceability theo từng contract bước
- boundary semantics rõ hơn giữa resolution, handoff intent, execution preparation, và execution result
- runtime artifacts rõ hơn dưới `SOURCE_DEV/workspace`, không mờ với repo-local state
- cơ sở tốt hơn để đánh giá phần hardening nào còn thuộc `v0` và phần nào thực sự đòi hỏi horizon mới

## 6. Must-have

- explicit Slice A `request-to-product resolution` contract
- explicit Slice B `resolution-to-handoff intent` contract
- explicit Slice C `product execution preparation` contract
- explicit Slice D `product execution result` contract
- file-based runtime materialization của cả chain dưới `SOURCE_DEV/workspace`
- traceability links rõ giữa các contracts
- test coverage đủ để chứng minh shape, separation, artifact existence, và no hidden broader scope
- README/doc alignment đủ để scope thực tế không drift khỏi active roadmap

## 7. Good-to-have

Nếu còn capacity, `v0.5` có thể mở thêm:

- consolidation wording cleanup nhỏ giữa roadmap, code-local READMEs, và release-track reports
- report navigation clarity tốt hơn cho release chain `v0.4 -> v0.5`
- test assertions giàu hơn cho content-level traceability nếu thật sự có gap nhỏ còn sót

## 8. Deferred areas

Vẫn defer beyond `v0.5` nếu chưa có evidence đủ mạnh:

- provider arbitration engine
- cost-aware routing engine expansion
- topology-aware orchestration
- approval UI hoặc broad operator surface
- recovery execution
- distributed control
- generalized orchestration engine hoặc portfolio orchestration

## 9. Slice structure

`v0.5` được chia thành bốn slices runtime nhỏ, mỗi slice harden một contract step trong cùng chain:

1. Slice A: request-to-product resolution contract
2. Slice B: resolution-to-handoff intent contract
3. Slice C: product execution preparation contract
4. Slice D: product execution result contract

Các slice này không tạo orchestration engine mới. Chúng chỉ harden một foundational request-to-product execution chain ở mức contract, artifact, và traceability.

Mỗi slice cũng phải trả lời được: nó giúp ATP mạnh hơn ở đoạn nào trong trục `requested user ⇄ ATP ⇄ products`.

## 10. Freeze criteria

`v0.5` chỉ nên được coi là freeze-ready nếu:

- scope thực tế vẫn nằm trong current `v0` capability horizon
- docs và implementation vẫn bám stable core + controlled open evolution doctrine
- roadmap layer không còn chủ yếu là retrospective summary
- có integration review / consolidation pass rõ ràng
- có consolidation decision rõ ràng
- có freeze tag và formal freeze close-out
- README alignment được xử lý ở đúng level đã thay đổi

## 11. Integration criteria

`v0.5` chỉ nên integrate vào `main` nếu:

- evidence cho phạm vi đã chọn là đủ
- active docs, roadmap docs, và close-out chain không mâu thuẫn nhau
- không có blocker về boundary correctness hoặc governance continuity
- merge candidate bảo toàn được historical traceability của `v0.2.0` -> `v0.5`
- narrative của roadmap docs đã nghiêng rõ sang future guidance hơn là retrospective summary
