# ATP v0 Major Roadmap

## 1. Ý nghĩa của v0 family

`v0` là major family shape-correct của ATP.

Mục tiêu của `v0` không phải mở rộng breadth tối đa, mà là thiết lập một control-plane baseline coherent, architecture-faithful, và có thể evolve có kiểm soát.

## 2. v0.x đã giải quyết gì

Từ evidence đã freeze trong repo:

- `v0.1.0` — hardening baseline cho docs, consistency, và repo-local flow
- `v0.2.0` — runtime materialization baseline consolidation
- `v0.3.0` — external boundary / continuation / reference completion
- `v0.4.0` — current-task persistence / recovery-entry / pointer / inspect hardening

Nhìn chung, v0 family đã xây được:

- stable core cho ATP control-plane
- runtime boundary rõ giữa repo và workspace
- exchange/current-task traceability tối thiểu
- versioned evolution discipline đã được chứng minh trong thực tế

## 3. v0 vẫn chưa bao gồm gì

`v0` vẫn chưa bao gồm:

- production persistence redesign
- scheduler / queue behavior
- remote orchestration plane hoàn chỉnh
- approval UI hoặc operator console rộng
- generalized registry/catalog/search subsystem
- broad lifecycle automation

Những phần này không bị “cấm vĩnh viễn”, nhưng chưa thuộc coherent maturity boundary của v0 hiện tại.

## 4. Cách hiểu đúng về v0

`v0` không phải phase “throwaway MVP”.

`v0` nên được hiểu là:

- stable core establishment
- boundary completion
- operational traceability hardening
- governance-backed evolution proof

Điểm quan trọng là v0 đã chứng minh ATP có thể evolve có kiểm soát mà không rơi vào ad hoc expansion.

## 5. Điều gì có thể justify chuyển sang major family tiếp theo

Chuyển từ `v0` sang major family tiếp theo chỉ nên xảy ra khi có evidence rằng:

- v0 family đã đạt coherent maturity boundary
- các seams hiện có không còn chỉ là hardening seams, mà bắt đầu đòi hỏi một capability horizon mới
- roadmap tiếp theo cần đổi tầng khái niệm, không chỉ thêm một minor extension

Ví dụ về dấu hiệu có thể justify major transition trong tương lai:

- ATP cần production-grade persistence model mới, không còn là hardening của current-task semantics
- ATP cần orchestration horizon mới với control contracts rộng hơn major v0
- ATP cần operator/runtime model mới vượt quá phạm vi current v0 discipline

Nếu chưa có bằng chứng kiểu này, ATP nên tiếp tục ở minor versions trong `v0`.

## 6. Quan hệ giữa v0 và v0.5

`v0.5` vì vậy phải được hiểu là:

- minor extension của current `v0` capability horizon
- kế thừa từ `v0.4.0` freeze + close-out + consolidation baseline
- không phải major reset hay architecture rewrite
