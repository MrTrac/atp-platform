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

Mục tiêu của `v0.5` là biến roadmap/doctrine/release inheritance của ATP thành development guidance đủ rõ để các implementation bước sâu hơn vẫn bám đúng `v0` major horizon.

Vì vậy `v0.5` là execution horizon cho một planning-governance capability gap, không phải một broad feature horizon mới.

Ở góc nhìn operating purpose, `v0.5` phải giúp ATP giải thích rõ hơn các bước phát triển tiếp theo sẽ cải thiện mediation giữa requested user và products như thế nào.

## 4. Capability gap mà v0.5 cần address

Capability gap của `v0.5` không phải một missing runtime subsystem cụ thể, mà là một planning-governance gap:

- ATP cần một forward-looking roadmap layer đủ mạnh
- ATP cần logic major/minor transition rõ hơn
- ATP cần version inheritance và freeze continuity được đặt thành active discipline, không chỉ là practice ngầm
- ATP cần bộ lọc rõ hơn để chỉ giữ lại các capability directions thực sự làm mạnh hơn trục `requested user ⇄ ATP ⇄ products`

Nếu gap này không được address, các version sau của `v0` sẽ dễ drift thành chuỗi release retrospective thay vì một major family có development map rõ.

Đây là lý do `v0.5` vẫn là guided development step thực sự: nó giảm rủi ro architectural drift cho các implementation slices về sau.

## 5. v0.5 phải unlock điều gì cho v0 major roadmap

`v0.5` phải unlock:

- một development map rõ hơn cho phần còn lại của `v0`
- tiêu chí rõ hơn để phân biệt đâu là minor extension hợp lệ trong `v0`
- cơ sở tốt hơn để đánh giá khi nào `v0` đã gần đủ maturity boundary để cân nhắc `v1`
- logic rõ hơn để đánh giá capability bundle nào thực sự phục vụ requested user flow qua ATP vào products

## 6. Must-have

- doctrine alignment giữa architecture, governance, roadmap, và release inheritance
- roadmap reframing từ retrospective summary sang forward-looking development map
- freeze close-out continuity được backfill đủ tới `v0.4.0`
- version planning baseline đủ rõ để bước implementation sâu hơn không drift khỏi stable core
- strategic horizon và execution horizon được tách rõ trong roadmap layer
- request-driven, product-oriented operating axis được phản ánh rõ trong doctrine và roadmap docs

## 7. Good-to-have

Nếu còn capacity, `v0.5` có thể mở thêm:

- hardening nhỏ cho planning/consolidation discipline
- roadmap/report navigation clarity
- evidence alignment tốt hơn giữa active docs và release track history
- cách diễn đạt rõ hơn cho tiêu chí nào còn thuộc `v0` và tiêu chí nào bắt đầu chạm ngưỡng `v1`

## 8. Deferred areas

Vẫn defer beyond `v0.5` nếu chưa có evidence đủ mạnh:

- production persistence redesign
- scheduler / queue behavior
- remote orchestration
- approval UI hoặc broad operator surface
- generalized index/search/catalog subsystem
- broad subsystem expansion không bám slice planning

## 9. Slice structure

`v0.5` nên chia thành các slices nhỏ, mỗi slice unlock một phần của planning-governance maturity:

1. doctrine alignment và roadmap foundation
2. roadmap reframing và inheritance hardening
3. candidate next-scope selection dựa trên inherited evidence
4. chỉ sau đó mới mở deeper implementation track nếu planning baseline đã đủ rõ

Các slice này không nên bị hiểu là pseudo-implementation backlog. Chúng chỉ là execution structure để hoàn tất planning-governance horizon của `v0.5`.

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
