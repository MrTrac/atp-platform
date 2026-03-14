# ATP v0.5 Roadmap

## 1. Version goal

Mục tiêu của `v0.5` là tiếp tục minor extension của `v0` capability horizon theo hướng deepening có kiểm soát, không mở sang major reset.

Hướng ưu tiên là làm rõ hơn capability horizon kế tiếp sau current-task hardening của `v0.4.0`, nhưng vẫn giữ:

- stable core
- modular boundaries
- explicit extension seams
- composable capability growth
- governance-backed evolution discipline

## 2. Inheritance từ v0.4

`v0.5` phải kế thừa từ:

- `v0.4.0` freeze baseline
- `ATP_v0_4_Integration_Review.md`
- `ATP_v0_4_Consolidation_Decision.md`
- `ATP_v0_4_0_Freeze_Closeout.md`
- product/major roadmap active của ATP

`v0.5` không được diễn giải lại v0.4 như một unfinished broad platform phase. `v0.5` chỉ nên tiếp tục nơi v0.4 đã freeze một cách có kiểm soát.

## 3. Must-have direction

Must-have direction cho `v0.5` là:

- chốt doctrine alignment giữa architecture, governance, roadmap, và release inheritance
- xác định next capability horizon của `v0` dựa trên frozen evidence từ `v0.2.0` đến `v0.4.0`
- chuẩn bị planning baseline đủ rõ để implementation sâu hơn không drift khỏi stable core

## 4. Good-to-have direction

Nếu còn capacity, `v0.5` có thể mở thêm:

- hardening nhỏ cho planning/consolidation discipline
- roadmap/report navigation clarity
- evidence alignment tốt hơn giữa active docs và release track history

## 5. Deferred areas

Vẫn defer beyond `v0.5` nếu chưa có evidence đủ mạnh:

- production persistence redesign
- scheduler / queue behavior
- remote orchestration
- approval UI hoặc broad operator surface
- generalized index/search/catalog subsystem
- broad subsystem expansion không bám slice planning

## 6. Slice structure

Ở thời điểm roadmap này, v0.5 nên được chia theo các slice hẹp, bám doctrine-first:

1. doctrine alignment và roadmap foundation
2. planning baseline hardening nếu còn thiếu
3. candidate next-scope selection dựa trên inherited evidence
4. chỉ sau đó mới mở deeper implementation track nếu planning baseline đã đủ rõ

## 7. Freeze criteria

`v0.5` chỉ nên được coi là freeze-ready nếu:

- scope thực tế vẫn nằm trong current `v0` capability horizon
- implementation và docs vẫn bám stable core + controlled open evolution doctrine
- có integration review / consolidation pass rõ ràng
- có consolidation decision rõ ràng
- có freeze tag và formal freeze close-out
- README alignment được xử lý ở đúng level đã thay đổi

## 8. Integration criteria

`v0.5` chỉ nên integrate vào `main` nếu:

- test và verification evidence đủ cho phạm vi đã chọn
- docs active, roadmap docs, và close-out chain không mâu thuẫn nhau
- không có blocker về boundary correctness hoặc governance continuity
- merge candidate bảo toàn được historical traceability của `v0.2.0` -> `v0.5`
