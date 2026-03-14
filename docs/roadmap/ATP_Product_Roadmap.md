# ATP Product Roadmap

## 1. Vai trò của product roadmap

Product roadmap mô tả ATP đang hướng tới capability horizons nào trong dài hạn, bằng logic nào, và theo điều kiện chuyển tiếp nào.

Tài liệu này là strategic roadmap của ATP. Nó không tồn tại để tóm tắt retrospective release history. Lịch sử frozen chỉ được dùng như evidence để định hướng future development.

## 2. ATP đang hướng tới điều gì theo thời gian

ATP hướng tới một control-plane architecture đủ trưởng thành để:

- giữ stable core trong khi capability surface tăng dần
- mở rộng qua modular boundaries và explicit extension seams thay vì feature accretion tùy hứng
- tăng composable capabilities theo từng maturity horizon
- hấp thụ better modern patterns từ market mà không phá architecture doctrine
- làm mạnh hơn trục vận hành `requested user ⇄ ATP ⇄ products`

Nói ngắn gọn, ATP hướng tới một platform architecture có thể evolve lâu dài, nhưng chỉ qua governance-backed change.

Product roadmap vì vậy phải trả lời được bốn câu hỏi:

- ATP đang đi tới capability horizon nào
- horizon đó khác horizon hiện tại ở điểm nào
- cần maturity evidence nào để chuyển horizon
- đâu là phần còn mở theo thị trường nhưng chưa đủ căn cứ để commit

Ở cấp product, ATP không tối ưu cho internal mechanism growth đơn thuần. ATP tối ưu cho việc request từ requested user được ATP biến thành product-facing execution/control flow rõ hơn, an toàn hơn, và dễ kế thừa hơn.

## 3. Doctrine chi phối product roadmap

ATP là architecture-first, nhưng market-aware.

Điều này có nghĩa:

- architecture specification vẫn là north star chính
- roadmap phải phục vụ architecture, không dẫn architecture theo implementation convenience
- ATP có thể hấp thụ better market patterns
- nhưng chỉ khi các pattern đó đi qua controlled review, planning, verification, consolidation, freeze, close-out, và roadmap inheritance

Open evolution trong ATP không có nghĩa là arbitrary expansion. “Open” chỉ hợp lệ khi:

- contract-driven
- composable
- governance-controlled

Điều này cũng có nghĩa ATP có thể học từ những platform builders hiện đại ở các pattern như:

- capability bundling
- stable core với expandable surfaces
- composable capability growth

Nhưng ATP không sao chép consumer AI builder narratives, không đi theo UI-first framing, và không tự định nghĩa như no-code builder. ATP giữ vai trò request-driven, product-oriented orchestration platform.

## 4. Các capability horizons cấp product

### v0 family

`v0` là foundational major family.

Vai trò của `v0` là:

- chứng minh stable core
- hoàn thiện boundary discipline
- làm rõ runtime traceability và operational seams tối thiểu
- chứng minh ATP có thể evolve bằng versioned slices và freeze discipline
- chứng minh rằng ATP có thể mediate đúng trục `requested user ⇄ ATP ⇄ products` ở mức nền tảng

`v0` vì vậy là baseline-forming family, không phải throwaway MVP line.

### v1 family

`v1` là major horizon tiếp theo sau `v0`, nhưng vẫn còn provisional.

Ở mức định hướng, `v1` chỉ nên xuất hiện khi ATP cần một capability horizon mới vượt quá hardening của current `v0` seams. Nếu điều đó xảy ra, `v1` nhiều khả năng sẽ là giai đoạn:

- nâng từ operationally coherent sang production-capable contracts
- mở rộng một số seams hiện có thành maturity-grade capability layers
- vẫn giữ architecture-first discipline
- làm cho mediation giữa requested user, ATP, và products trở nên production-grade thay vì chỉ coherent ở mức nền

`v1` hiện chưa phải implementation commitment. Nó chỉ là strategic horizon tiếp theo nếu `v0` thực sự chạm maturity boundary của mình.

### v2 family và các major sau

`v2+` hiện chỉ nên được hiểu ở mức horizon khái quát:

- các major sau sẽ chỉ hợp lệ khi ATP tiếp tục vượt qua những maturity boundaries mới
- không nên gán promise chi tiết cho các major này trước khi evidence đủ mạnh

## 5. Logic chuyển tiếp giữa major families

Minor versions mở rộng current major capability horizon.

Major transition chỉ nên xảy ra khi có evidence rằng:

- current major family đã đạt coherent maturity boundary
- seams hiện tại không còn là hardening seams mà bắt đầu đòi hỏi capability horizon mới
- bước tiếp theo không còn là refinement tự nhiên của current major
- trục `requested user ⇄ ATP ⇄ products` cần một lớp capability mới chứ không chỉ một refinement cục bộ

Với ATP hiện tại, evidence mới chỉ đủ để tiếp tục trong `v0`. Product roadmap chưa có căn cứ để coi `v1` là ready-to-open implementation family.

Điều này giúp ATP giữ visible future direction mà không biến roadmap thành lời hứa triển khai cho những horizon còn chưa được quyết định.

## 6. Cách ATP giữ doctrine trong khi vẫn market-aware

ATP vẫn mở với market, nhưng openness không được đo bằng số lượng feature ideas có thể nhận vào. Openness được đo bằng khả năng:

- nhận diện pattern nào thực sự tốt hơn
- kiểm tra pattern đó có khớp stable core và modular boundaries hay không
- hấp thụ pattern đó qua versioned planning và verification
- chứng minh pattern mới không làm đứt historical continuity hoặc freeze discipline

ATP vì vậy có thể học từ modern platform/AI patterns, nhưng chỉ như framing influence. ATP không sao chép literal market roadmaps và không dùng market motion để bypass architecture doctrine.

Các bài học được giữ lại cho ATP là:

- tổ chức capability theo bundles/horizons thay vì feature pile
- dùng platform surface có seams rõ thay vì expansion tùy hứng
- giữ product orientation thay vì xây cơ chế nội bộ không gắn với requested user flow

## 7. Điều product roadmap không làm

Product roadmap không phải:

- backlog implementation
- retrospective changelog
- market promise document
- cách bypass architecture doctrine hoặc release governance

Product roadmap chỉ nên phát biểu:

- future capability horizons
- transition logic
- doctrine-constrained direction
- các điều kiện maturity để future horizons trở nên hợp lệ hơn
