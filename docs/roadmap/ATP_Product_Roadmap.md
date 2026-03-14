# ATP Product Roadmap

## 1. Vai trò của product roadmap

Product roadmap mô tả ATP sẽ evolve như thế nào trong dài hạn mà không phá kiến trúc đã freeze theo từng phase.

ATP không phát triển bằng arbitrary feature growth. ATP phát triển qua:

- stable core
- modular boundaries
- explicit extension seams
- composable capabilities
- controlled evolutionary governance

## 2. Doctrine nền

ATP là architecture-first, nhưng market-aware.

Điều này có nghĩa:

- ATP dựa trên một architecture baseline đã được tổng hợp và review cẩn thận
- ATP có thể hấp thụ better modern patterns và market practices
- nhưng chỉ qua controlled review, planning, verification, consolidation, freeze, close-out, và roadmap inheritance

Open evolution trong ATP không có nghĩa là arbitrary expansion. Modularization là điều kiện cần, nhưng không đủ. Sự “open” của ATP phải là:

- contract-driven
- composable
- governance-controlled

## 3. Tầng major generations

Trong ATP:

- **minor versions** mở rộng current major capability horizon
- **major versions** đánh dấu một capability horizon mới

Ví dụ:

- `v0` là major family shape-correct, architecture-disciplined, tập trung vào baseline coherence, runtime boundary completion, và operational traceability tối thiểu
- `v1` chỉ nên xuất hiện khi `v0` đã đạt một coherent maturity boundary đủ rõ để chuyển sang capability horizon mới
- `v2` và các major sau cũng phải được justified theo logic tương tự, không theo numbering pressure

## 4. Evolution model của ATP

ATP evolve qua các capability horizons có kiểm soát:

1. xác nhận current baseline và historical inheritance
2. đánh giá candidate scope dựa trên evidence và maturity hiện tại
3. chốt version planning baseline
4. chia thành slices nhỏ, testable, traceable
5. implementation + verification
6. integration review / consolidation
7. freeze + tag
8. freeze close-out
9. roadmap inheritance sang version tiếp theo

## 5. Điều ATP không làm ở tầng roadmap

Roadmap của ATP không phải:

- backlog tính năng ad hoc
- lời hứa market-facing không có evidence
- cách để lách governance hoặc bypass freeze discipline

Roadmap chỉ hợp lệ khi bám đúng:

- frozen facts
- current doctrine
- evidence-based change
- versioned slice planning

## 6. Quan hệ với v0 family hiện tại

Từ evidence hiện có trong repo:

- `v0.2.0` khép baseline runtime materialization
- `v0.3.0` khép external boundary / continuation / reference layer
- `v0.4.0` khép current-task persistence / recovery-entry / pointer / inspect hardening ở mức tối thiểu

Điều này cho thấy ATP đang evolve đúng theo hướng: stable core trước, rồi controlled operational extension sau.
