# ATP v0.3 Slice Proposal

- **Ngày:** 2026-03-14
- **Phạm vi:** Đề xuất slice breakdown cho scope v0.3
- **Mục tiêu:** Chia v0.3 thành các lát cắt nhỏ, ít rủi ro, dễ trace, không làm nở scope

## 1. Nguyên tắc chia slice

- mỗi slice chỉ chốt một semantic gap rõ ràng
- ưu tiên hoàn thiện boundary hơn là thêm capability rộng
- không trộn persistence/UI/orchestration vào cùng phase
- mỗi slice phải testable và không đòi redesign ATP

## 2. Slice structure đề xuất

## Slice A — Exchange boundary decision model

### Mục tiêu

Xác định rõ khi nào handoff vẫn ở `atp-runs/<run-id>/handoff/` và khi nào phải materialize thêm sang `SOURCE_DEV/workspace/exchange/`.

### Nội dung

- chốt decision rule tối thiểu cho external handoff boundary
- chốt semantic mapping giữa `handoff/` và `exchange/`
- chưa bàn đến persistence sâu hoặc cleanup engine

### Giá trị

Đây là lát cắt phải có đầu tiên, vì nếu chưa chốt rule này thì implementation exchange rất dễ drift.

## Slice B — Minimal exchange materialization

### Mục tiêu

Materialize `exchange/` ở mức tối thiểu cho boundary đã được Slice A chốt.

### Nội dung

- tạo current exchange payload theo boundary thật
- giữ trace về run nguồn và handoff source
- không mở rộng thành queue/subsystem rộng

### Giá trị

Đây là completion hợp logic của Slice 2, nhưng ở external boundary thay vì chỉ trong run tree.

## Slice C — Continue-pending operational continuity

### Mục tiêu

Làm rõ `continue_pending` sẽ giữ continuity set nào và boundary nào là current source cho bước tiếp theo.

### Nội dung

- rule tối thiểu cho continuity artifacts
- mapping giữa continue state và exchange/reference hiện hành
- giữ workflow states cũ, không tạo state mới

### Giá trị

Slice này giúp tránh drift operational khi ATP bắt đầu có external handoff boundary thật.

## Slice D — Minimal reference / index support

### Mục tiêu

Thêm lớp reference/index tối thiểu nếu thật sự cần để hỗ trợ Slice B-C.

### Nội dung

- current exchange reference
- current manifest/reference pointer ở mức tối thiểu
- không biến thành inventory database hay persistence layer

### Giá trị

Slice này nên là slice cuối hoặc conditional slice. Chỉ làm nếu thiếu nó thì exchange/continue semantics trở nên khó trace hoặc khó test.

## 3. Thứ tự khuyến nghị

Thứ tự khuyến nghị cho v0.3:

1. Slice A
2. Slice B
3. Slice C
4. Slice D nếu cần

Lý do:

- A chốt rule
- B materialize boundary
- C ổn định behavior của `continue_pending`
- D chỉ bổ sung reference support khi thật sự cần

## 4. Cái gì không nằm trong slice proposal này

Không thuộc v0.3 proposal này:

- persistence redesign
- approval UI
- remote orchestration
- advanced scheduling
- broad retention/cleanup automation
- artifact management subsystem lớn

## 5. Exit criteria cấp phase cho v0.3

v0.3 nên được coi là hoàn tất nếu đạt:

- external handoff boundary được materialize tối thiểu nhưng rõ ràng
- `continue_pending` có operational semantics ổn định hơn
- traceability giữa run tree, exchange, và authoritative references vẫn rõ
- không có scope creep sang production persistence hoặc orchestration expansion

## 6. Kết luận

Slice proposal tốt nhất cho v0.3 là một chuỗi ngắn, xoay quanh **exchange boundary completion**.

Nếu giữ kỷ luật slice như trên, v0.3 sẽ là bước nối tự nhiên sau v0.2 và vẫn bảo toàn shape-correct discipline của ATP.
