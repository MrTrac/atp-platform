# ATP Development Stage Roadmap

## 1. Mục đích của tài liệu

Tài liệu này mô tả ATP theo các development stages mang tính capability/maturity horizon.

Mục tiêu của stage roadmap là trả lời thực dụng:

- ATP trông như thế nào ở từng stage
- ATP làm được gì ở từng stage
- ATP chưa làm được gì ở từng stage
- nhu cầu thực tế nào đang được giải quyết ở từng stage
- điều kiện nào đủ để sang stage tiếp theo

Tài liệu này không thay thế architecture doctrine, major roadmap, version roadmap, hay freeze close-out. Nó dùng các lớp đó làm inheritance basis để mô tả ATP theo dạng dễ áp dụng hơn cho planning và expectation-setting.

Version lineage và documentation continuity không được theo dõi chính trong tài liệu này. Việc đó phải bám:

- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`

Nói ngắn gọn:

- stage roadmap theo dõi maturity horizon
- practical milestone map theo dõi lineage thực dụng và continuity status

---

## Giai đoạn 1: Foundational Baseline Horizon (`v0`)

### 1. Mục tiêu giai đoạn

Thiết lập ATP như một control-plane nền tảng, đủ coherent để mediate trục `requested user ⇄ ATP ⇄ products` ở mức tối thiểu nhưng đúng kiến trúc.

### 2. ATP có hình hài gì ở giai đoạn này

ATP ở giai đoạn này là:

- request-driven orchestration layer
- human-gated và artifact-centric
- local-first, provider-agnostic, adapter-first
- có runtime materialization và traceability tối thiểu
- có current-task semantics ở mức nền nhưng chưa phải production runtime system rộng

Frozen evidence của `v0.2.0` -> `v0.4.0` cho thấy horizon này đã có:

- runtime materialization baseline
- exchange boundary và continuation semantics
- current-task persistence/recovery/pointer/inspect hardening ở mức hẹp

### 3. Nhu cầu thực tế mà giai đoạn này nhắm tới

Giai đoạn này nhắm tới nhu cầu của team/operator đang cần:

- biến user request thành flow có kiểm soát thay vì thao tác thủ công rời rạc
- giữ boundary rõ giữa source repo, runtime workspace, và handoff/exchange state
- có traceability tối thiểu để review, approve, continue, hoặc inspect một run
- harden kiến trúc trước khi nghĩ tới production-scale expansion

### 4. ATP làm được gì ở giai đoạn này

ATP có thể:

- nhận request, normalize, classify, resolve product, package context, route, execute, validate, approve, finalize, handoff
- materialize run tree dưới workspace đúng boundary
- tạo exchange/current-task artifacts khi boundary yêu cầu
- giữ continuation/current-task traceability tối thiểu
- expose inspect surface read-only hẹp cho current-task state
- duy trì governance chain gồm planning, slices, consolidation, freeze, close-out

### 5. ATP chưa làm được gì ở giai đoạn này

ATP chưa làm tốt hoặc chưa nên hứa ở stage này:

- production persistence redesign
- scheduler/queue behavior
- remote orchestration plane hoàn chỉnh
- operator console hoặc broad UI
- large-scale portfolio orchestration
- distributed execution/control plane
- lifecycle automation rộng

### 6. Giới hạn thực tế / boundary của giai đoạn này

Boundary thực tế của stage này là:

- ATP mới ở mức foundational family, không phải production-capable maturity horizon
- traceability artifacts có mục tiêu rõ nhưng còn hẹp
- inspect chỉ đọc trạng thái đã materialize, không cung cấp control actions
- current-task semantics đủ cho coherence, chưa đủ cho broad runtime management

### 7. Giá trị thực tế đạt được

Giá trị thực tế của stage này là:

- team có một control-plane baseline rõ, không còn chỉ là ad hoc glue logic
- user request được nối với product execution qua một flow có governance
- repo/workspace boundary và artifact discipline đủ rõ để không drift
- ATP có foundation đúng để mở horizon tiếp theo mà không phải viết lại doctrine

### 8. Điều kiện để sang giai đoạn tiếp theo

ATP chỉ nên rời `v0` khi có evidence rằng:

- current `v0` seams đã được harden tới mức coherent maturity boundary
- `v0.5` đã làm rõ doctrine continuity, roadmap continuity, và next capability direction
- bước tiếp theo đòi hỏi capability horizon mới, không chỉ refinement thêm trong `v0`
- stage tiếp theo có thể được mô tả như nâng chất lượng mediation giữa requested user, ATP, và products lên mức vận hành cao hơn

---

## Giai đoạn 2: Operational Maturity Horizon (`v1`)

### 1. Mục tiêu giai đoạn

Nâng ATP từ foundational coherence lên operational maturity đủ mạnh để hỗ trợ request-to-product mediation ở mức đáng tin cậy hơn cho team vận hành thực tế.

### 2. ATP có hình hài gì ở giai đoạn này

ATP ở stage này nhiều khả năng là:

- vẫn giữ stable core của `v0`
- nhưng có contracts trưởng thành hơn cho current-task, persistence, continuity, và operator-facing inspection
- có orchestration semantics rõ hơn ở mức operational layer, không còn chỉ là minimal hardening

Đây là capability horizon tiếp theo sau `v0`, chưa phải distributed horizon.

### 3. Nhu cầu thực tế mà giai đoạn này nhắm tới

Stage này nhắm tới nhu cầu của team cần:

- vận hành ATP lặp lại với độ tin cậy cao hơn
- tiếp tục hoặc kiểm tra current-task state dễ hơn
- giảm ambiguity giữa “đã materialize được” và “vận hành được ở mức tin cậy”
- có operator/runtime contracts rõ hơn mà không phải nhảy thẳng sang distributed system

### 4. ATP làm được gì ở giai đoạn này

ATP ở stage này nên làm được:

- duy trì current-task state theo contract rõ và ổn định hơn
- hỗ trợ inspect/review/continuation clarity tốt hơn cho operator và team phát triển
- quản lý tốt hơn các capability bundles liên quan tới request mediation, handoff, exchange, continuity, và artifact traceability
- cung cấp product-oriented orchestration đủ trưởng thành để nhiều use cases thực tế không còn bị chặn bởi baseline-level ambiguity

### 5. ATP chưa làm được gì ở giai đoạn này

ATP ở stage này vẫn chưa nên hứa:

- distributed control plane hoàn chỉnh
- remote multi-node orchestration rộng
- large-scale scheduling/queueing
- broad UI-first operating model
- generalized platform catalog/search experience rộng

### 6. Giới hạn thực tế / boundary của giai đoạn này

Boundary của stage này là:

- ATP vẫn ưu tiên request-to-product mediation trước, không tối ưu cho platform breadth
- maturity tăng ở contracts và operational clarity, chưa phải scale-out horizon
- capability growth vẫn phải là contract-driven, không được biến thành framework accretion

### 7. Giá trị thực tế đạt được

Giá trị của stage này là:

- ATP bắt đầu đáng tin hơn như một control/orchestration layer dùng cho công việc thực tế có lặp lại
- user/team có thể kỳ vọng ít ambiguity hơn khi inspect, continue, và handoff work
- product-facing execution qua ATP trở nên rõ ràng và ổn định hơn, không chỉ “đúng shape”

### 8. Điều kiện để sang giai đoạn tiếp theo

Chỉ nên sang `v2` khi có evidence rằng:

- operational maturity đã đủ rõ ở current-task/product mediation layer
- ATP cần mở rộng từ “một product flow coherent” sang “portfolio/orchestration horizon rộng hơn”
- bước tiếp theo đòi hỏi capability bundles mới ở mức orchestration/product-portfolio, không chỉ hardening contracts hiện có

---

## Giai đoạn 3: Orchestration / Product-Portfolio Horizon (`v2`)

### 1. Mục tiêu giai đoạn

Mở ATP từ control layer cho các flows hẹp sang orchestration platform có thể điều phối portfolio capability surfaces rộng hơn giữa nhiều product contexts, nhưng vẫn giữ requested user là nguồn intent chính.

### 2. ATP có hình hài gì ở giai đoạn này

ATP ở stage này có thể được nhìn như:

- request-driven orchestration platform trưởng thành hơn
- có capability bundles rõ hơn cho multi-product mediation
- có product portfolio thinking, thay vì chỉ xử lý single-product path theo cách hẹp

Đây là stage mở rộng orchestration breadth, không phải distributed-control stage cuối cùng.

### 3. Nhu cầu thực tế mà giai đoạn này nhắm tới

Stage này nhắm tới nhu cầu của tổ chức/team cần:

- dùng ATP như lớp điều phối cho nhiều capability surfaces hoặc nhiều product lines hơn
- giữ một governance/control plane thống nhất thay vì có nhiều glue workflows rời rạc
- nối request từ user vào nhiều execution surfaces một cách có contract và traceability

### 4. ATP làm được gì ở giai đoạn này

ATP ở stage này nên làm được:

- organize capability bundles theo product/portfolio horizon rõ hơn
- route và govern các flows phức tạp hơn giữa ATP và product surfaces
- giữ continuity, traceability, và policy clarity khi phạm vi mediation mở rộng
- giúp team coi ATP là control plane dùng chung cho nhiều product-facing capabilities, không chỉ một hẹp path

### 5. ATP chưa làm được gì ở giai đoạn này

ATP ở stage này vẫn chưa nên hứa:

- distributed multi-node control maturity đầy đủ
- remote execution network quy mô lớn
- cluster-like control plane
- centralized global runtime plane cho môi trường phân tán rộng

### 6. Giới hạn thực tế / boundary của giai đoạn này

Boundary của stage này là:

- breadth của orchestration tăng, nhưng distributed-control complexity chưa phải trọng tâm
- ATP vẫn phải giữ human-gated, artifact-centric, governance-backed discipline
- expansion sang portfolio horizon không được phá stable core hay biến ATP thành generic platform for everything

### 7. Giá trị thực tế đạt được

Giá trị của stage này là:

- một team có thể dùng ATP như lớp điều phối cấp cao hơn giữa user requests và nhiều product capabilities
- product portfolio growth có thể đi qua ATP mà vẫn giữ control contracts và governance
- ATP bắt đầu đem lại giá trị tổ chức rõ hơn, không chỉ giá trị cục bộ cho một flow hẹp

### 8. Điều kiện để sang giai đoạn tiếp theo

Chỉ nên sang `v3+` khi có evidence rằng:

- portfolio orchestration horizon đã đủ coherent
- nhu cầu thực tế đã vượt khỏi một control plane tập trung/hẹp
- ATP thật sự cần distributed/control maturity mới để tiếp tục tăng giá trị trên trục `requested user ⇄ ATP ⇄ products`

---

## Giai đoạn 4: Distributed / Control Maturity Horizon (`v3+`)

### 1. Mục tiêu giai đoạn

Đưa ATP tới horizon nơi mediation giữa requested user, ATP, và products không còn bị giới hạn ở local/limited orchestration, mà có thể được vận hành qua các control surfaces rộng hơn.

### 2. ATP có hình hài gì ở giai đoạn này

ATP ở stage này chỉ nên được hiểu ở mức định hướng cao:

- control plane trưởng thành hơn
- distributed/runtime coordination rõ hơn
- policy, traceability, và governance vẫn là lớp giữ stable core

Đây chưa phải cam kết implementation cụ thể ở branch hiện tại.

### 3. Nhu cầu thực tế mà giai đoạn này nhắm tới

Stage này nhắm tới nhu cầu của tổ chức khi:

- nhiều nodes, nhiều environments, hoặc nhiều execution surfaces cần được điều phối có kiểm soát
- local-first/limited orchestration không còn đủ
- governance cần giữ nguyên ngay cả khi control scope rộng hơn

### 4. ATP làm được gì ở giai đoạn này

Nếu ATP tới được stage này, ATP nhiều khả năng sẽ làm được:

- điều phối control/runtime surfaces rộng hơn
- giữ governance continuity và artifact discipline trên phạm vi lớn hơn
- cho phép requested user flow được ATP mediate tới nhiều execution surfaces hơn mà vẫn có control semantics rõ

### 5. ATP chưa làm được gì ở giai đoạn này

Những chi tiết implementation cụ thể của stage này hiện chưa thể khẳng định chắc.

ATP hiện chưa có căn cứ để commit:

- exact distributed model
- exact remote-agent model
- exact UI/control console model
- exact persistence/scheduling architecture

### 6. Giới hạn thực tế / boundary của giai đoạn này

Boundary của `v3+` ở thời điểm hiện tại là:

- chỉ là high-level horizon
- không phải current planning commitment
- chỉ hợp lệ khi future evidence đủ mạnh và các stages trước đã đạt maturity boundary rõ

### 7. Giá trị thực tế đạt được

Nếu ATP đạt tới stage này, giá trị thực tế sẽ là:

- control plane có thể hỗ trợ operating environments rộng hơn
- mediation giữa requested user và products không còn gói trong phạm vi hẹp/local
- ATP có thể trở thành lớp điều phối có maturity cao hơn mà vẫn không bỏ doctrine gốc

### 8. Điều kiện để sang giai đoạn tiếp theo

Chưa xác định chắc ở thời điểm hiện tại.

Mọi bước sau `v3+` chỉ nên được mở khi:

- stage `v3+` đã có evidence thực
- current major family của horizon đó đã đạt coherent maturity boundary
- roadmap và governance của ATP đủ rõ để không drift thành speculative expansion

## Kết luận sử dụng

Stage roadmap này nên được dùng để:

- hiểu ATP đang ở maturity horizon nào
- kiểm tra một version hoặc slice đang unlock gì cho horizon lớn hơn
- đặt kỳ vọng thực tế cho user, operator, và team phát triển
- kiểm tra stage progression có còn phù hợp với doctrine đang active hay không

Mọi stage progression phải giữ:

- version lineage rõ
- documentation continuity rõ
- authority path rõ trước khi coi một milestone đã hoàn tất về mặt governance

Nó không nên được dùng như:

- release summary
- implementation backlog
- market promise document
