# ATP v1 Major Roadmap

## 1. Mục tiêu của v1 family

`v1` là major family kế tiếp của ATP sau khi `v0` đã hoàn tất foundational lifecycle chain.

Vai trò của `v1` là bắt đầu và chứng minh:

- operational maturity trên stable core đã được `v0` chốt
- controlled operationalization thay vì foundational seam hardening
- các operational contracts rõ hơn cho review, approval gate, và lifecycle control hẹp
- một maturity horizon mới vẫn bám trục `requested user ⇄ ATP ⇄ products`

`v1` không phải architecture reset. `v1` kế thừa stable core, repo/workspace boundary, adapter shape, artifact discipline, và governance model đã được `v0` xác lập.

## 2. Vì sao `v1` bây giờ là bước đúng

Từ freeze close-out của `v0.5.0`, `v0.6.0`, và `v0.7.0`, ATP đã có:

- foundational request-to-product execution chain
- foundational closure chain
- foundational finalization / closure record seam đã được contract hóa

Điều này cho thấy phần còn lại không còn là “chốt nốt seam nền tảng của `v0`”, mà là bắt đầu harden một operational maturity horizon mới trên nền core đã ổn định.

Nói ngắn gọn:

- `v0` đã hoàn tất family goal của một foundational horizon
- bước tiếp theo không nên tiếp tục kéo dài `v0.x`
- `v1` là nơi đúng để bắt đầu operational maturity có kiểm soát

## 3. `v1` phải unlock điều gì

`v1` phải unlock ít nhất các hướng sau:

- operational gate semantics rõ hơn trên lifecycle chain đã có
- review / approval mediation được contract hóa ở mức bounded, file-based, và traceable
- operator-facing operational clarity tốt hơn mà không mở UI-first surface quá sớm
- evidence rằng ATP có thể vận hành như một operational control layer đáng tin cậy hơn, không chỉ là shape-correct baseline

## 4. `v1` chưa nên làm gì

`v1` chưa nên tự động mở sang:

- provider arbitration engine
- cost-aware routing expansion
- topology-aware orchestration
- distributed control
- broad operator UI
- generalized orchestration engine
- portfolio orchestration breadth của `v2`

`v1` phải tiếp tục giữ controlled operationalization, không drift thành breadth expansion.

## 5. Vấn đề đầu tiên của `v1`

Vấn đề đầu tiên của `v1` không còn là finalization seam, mà là operational gate seam sau finalization chain:

- ATP cần ghi explicit review / approval gate nào
- gate đó nằm ở đâu trong lifecycle continuity
- gate đó khác gì với approval UI, recovery engine, routing, provider selection, hay orchestration rộng

Đây là lý do Slice A của `v1.0` nên là `Review / Approval Gate Contract`.

## 6. Boundary của `v1`

Boundary thực tế của `v1` là:

- maturity tăng ở operational contracts, không ở breadth hệ thống
- stable core của `v0` phải được giữ nguyên và dùng như inheritance basis
- expansion của `v1` phải tiếp tục là governance-backed, slice-based, và file-based
- mọi step mới phải chứng minh rằng ATP đang làm mạnh hơn mediation giữa requested user, ATP, và products ở mức vận hành

## 7. Điều gì có thể justify chuyển từ `v1` sang `v2`

Chỉ nên rời `v1` khi có evidence rằng:

- operational gate / continuity / lifecycle contracts đã đủ trưởng thành
- bước tiếp theo đòi một orchestration horizon rộng hơn, không chỉ hardening operational control contracts
- ATP thật sự cần product-portfolio breadth hoặc orchestration bundles mới để tiếp tục tăng giá trị

Nếu chưa có evidence kiểu này, ATP nên tiếp tục ở minor versions trong `v1`.

## 8. Quan hệ giữa `v0` và `v1`

`v0` phải được hiểu là:

- foundational family đã hoàn tất qua `v0.7.0`
- family dùng để chốt stable core và foundational lifecycle chain
- không còn là nơi đúng để mở thêm operational maturity horizon mới

`v1` phải được hiểu là:

- continuation trực tiếp sau `v0.7.0`
- major family đầu tiên của operational maturity
- bước mở controlled operationalization trên nền core đã ổn định
- không phải reset kiến trúc và không phải breadth expansion
