# ATP v0 Major Roadmap

## 1. Mục tiêu của v0 family

`v0` là foundational major family của ATP.

Vai trò của `v0` là thiết lập và chứng minh:

- stable core của ATP control-plane
- boundary discipline giữa repo, workspace, handoff, exchange, projection, và runtime state
- extension seams đủ rõ để ATP có thể evolve theo versioned slices
- governance-backed evolution model có thể hoạt động trong thực tế
- trục vận hành `requested user ⇄ ATP ⇄ products` có thể được ATP mediate một cách coherent ở mức nền

`v0` không nhằm tối đa hóa feature breadth. `v0` nhằm tạo một nền đủ coherent để các horizon sau có thể xuất hiện hợp lệ.

## 2. Evidence hiện có từ v0.x

Từ frozen evidence trong repo:

- `v0.2.0` đã khóa runtime materialization baseline
- `v0.3.0` đã khóa external boundary / continuation / reference completion
- `v0.4.0` đã khóa current-task persistence / recovery-entry / pointer / inspect hardening

Điều này xác nhận rằng `v0` đã thiết lập được:

- stable core cho control-plane
- runtime boundary rõ giữa source repo và workspace
- operational traceability tối thiểu cho current-task family
- release discipline gồm planning -> slices -> consolidation -> freeze -> close-out

Các frozen facts này là inheritance evidence cho roadmap của `v0`, không phải narrative chính của major roadmap.

## 3. v0 còn phải hoàn tất điều gì

Để `v0` tiến gần hơn tới coherent maturity boundary, major family này vẫn cần:

- doctrine, roadmap, và release inheritance được làm rõ hơn như một phần active governance
- next capability horizon của `v0` được xác định bằng planning evidence, không bằng ad hoc expansion
- các seams hiện có được đánh giá xem còn là hardening seams hay đã tiến sát một new major horizon
- execution guidance cho các version tiếp theo phải nói rõ mỗi version unlock gì cho `v0`, thay vì chỉ nối thêm runtime detail
- các improvements phải tiếp tục chứng minh rằng ATP đang mạnh hơn trong việc nối requested user với products, không chỉ giàu internal state hơn

Nói cách khác, phần còn lại của `v0` không phải chỉ là “thêm feature”, mà là hoàn tất major family này như một disciplined capability horizon.

## 4. v0.5 cần unlock điều gì cho v0 family

`v0.5` nên unlock ít nhất ba việc cho `v0`:

- harden một request-to-product execution chain có contract rõ từ resolution tới bounded execution result
- làm rõ boundary semantics giữa resolution, handoff intent, execution preparation, và execution result mà không mở subsystem rộng hơn
- tăng traceability của ATP trên trục `requested user ⇄ ATP ⇄ products` ở mức contract chain dưới `SOURCE_DEV/workspace`
- giữ coherence giữa active doctrine/roadmap/governance baseline và runtime hardening thực tế của `v0`

Ở mức major-family logic, điều quan trọng không phải chỉ là thêm runtime detail, mà là harden đúng seams còn thuộc `v0` để minor versions tiếp theo vẫn nằm trong cùng capability horizon.

Nếu `v0.5` không unlock được chuỗi contract nền tảng này một cách coherent, `v0` sẽ tiếp tục có gap giữa resolution semantics và execution/result traceability, làm yếu operating axis của ATP ở mức nền.

## 5. v0.6 cần đóng nốt điều gì cho v0 family

Sau `v0.5.0`, `v0` vẫn còn một seam nền tảng chưa đóng đủ rõ: post-execution closure semantics.

`v0.6` nên được hiểu là version của foundational closure và transition-readiness preparation. Nó cần:

- harden bounded decision semantics ngay sau execution result
- làm rõ decision contract nối execution result với `close`, `close_rejected`, `continue_pending`, và review-escalation bounded semantics
- chứng minh rằng phần còn lại của `v0` vẫn là seam hardening, chưa đòi hỏi major horizon mới
- tạo evidence rõ hơn để đánh giá khi nào `v0` thật sự đủ maturity boundary cho `v1`

## 6. v0 vẫn chưa bao gồm gì

`v0` vẫn chưa bao gồm:

- production persistence redesign
- scheduler / queue behavior
- remote orchestration plane hoàn chỉnh
- approval UI hoặc operator console rộng
- generalized registry/catalog/search subsystem
- broad lifecycle automation

Những phần này không bị loại bỏ vĩnh viễn, nhưng hiện vẫn nằm ngoài maturity boundary của `v0`.

## 7. Điều gì có thể justify kết thúc v0 và chuyển sang v1

Chuyển từ `v0` sang major family tiếp theo chỉ nên xảy ra khi có evidence rằng:

- `v0` đã đạt coherent maturity boundary như một foundational family
- seams còn lại không còn là hardening của current `v0` contracts
- bước tiếp theo đòi hỏi một capability horizon mới, không chỉ một minor extension nữa

Ví dụ về dấu hiệu có thể justify transition:

- ATP cần production-grade persistence model mới thay vì hardening trên current-task semantics
- ATP cần orchestration horizon mới với control contracts rộng hơn major `v0`
- ATP cần operator/runtime model mới vượt quá phạm vi current `v0` discipline
- ATP cần capability bundles mới để mediate requested user tới products ở một maturity horizon khác, không còn chỉ là hardening trên baseline `v0`

Nếu chưa có evidence kiểu này, ATP nên tiếp tục ở minor versions trong `v0`.

Nói ngược lại, chỉ việc có thêm ý tưởng implementation chưa đủ để mở `v1`. `v1` chỉ hợp lệ khi next step đòi hỏi một horizon mới thay vì tiếp tục hardening trên current `v0` seams.

## 8. Quan hệ giữa v0, v0.5, và v0.6

`v0.5` phải được hiểu là:

- một guided step trong việc hoàn tất `v0`
- minor extension của current `v0` capability horizon
- kế thừa từ `v0.4.0` freeze + close-out + consolidation baseline
- không phải major reset và không phải architecture rewrite

`v0.6` phải được hiểu là:

- continuation trực tiếp sau `v0.5.0`
- version của foundational closure, không phải breadth expansion
- bước dùng để chốt nốt closure semantics còn thiếu trước khi cân nhắc `v1`
- minor extension cuối hoặc gần cuối của `v0` chỉ khi evidence vẫn cho thấy các seams còn lại là hardening seams, chưa phải horizon mới
