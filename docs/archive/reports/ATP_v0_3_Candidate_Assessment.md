# ATP v0.3 Candidate Assessment

- **Ngày:** 2026-03-14
- **Phạm vi:** Đánh giá candidate scope cho ATP v0.3 sau baseline runtime materialization v0.2
- **Mục tiêu:** Xác định hướng tiếp theo hợp lý nhất mà không làm drift kiến trúc ATP đã freeze

## 1. Tóm tắt current state sau v0.2

ATP v0.2 đã giải quyết bốn việc nền tảng:

- materialize run tree tối thiểu trong `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- materialize handoff tối thiểu trong `handoff/` của run tree
- project authoritative artifact sang `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- ghi retention / cleanup semantics tối thiểu, explicit, không auto-delete

Nhờ đó ATP hiện đã có baseline runtime materialization nhất quán, đủ để:

- xem toàn bộ run dưới workspace thật thay vì chỉ in-memory summary
- giữ boundary rõ giữa run-local state, handoff outputs, final outputs, và authoritative projection
- tránh blur giữa source repo và runtime zone

## 2. Những gì còn intentionally deferred sau v0.2

Các phần còn để lại có chủ ý:

- `exchange/` materialization khi handoff vượt ra ngoài run hiện tại
- operational model rõ hơn cho `continue_pending`
- manifest/index strategy để tra cứu run/artifact/handoff ổn định hơn
- persistence model ở mức production
- approval UI
- remote orchestration
- cleanup automation hoặc retention engine rộng hơn

## 3. Phân biệt “cần sớm” và “có thể chờ”

### Cần sớm sau v0.2

- exchange materialization boundary
- refinement cho `close-run / continue-run` ở mức operational handoff
- manifest/index strategy tối thiểu để hỗ trợ tra cứu boundary artifacts

### Có giá trị nhưng chưa cần ngay

- controlled persistence model
- orchestration control enhancements ở mức sâu hơn

### Chưa nên mở trong v0.3

- UI
- remote orchestration hoàn chỉnh
- broad lifecycle automation
- cleanup engine đầy đủ

## 4. Candidate areas

## Candidate A — Exchange materialization boundary

### Mô tả

Materialize `exchange/` một cách tối thiểu khi handoff thực sự vượt boundary của run hiện tại, thay vì luôn giữ mọi thứ trong `handoff/`.

### Vì sao quan trọng bây giờ

Đây là phần deferred rõ nhất còn lại ngay sau Slice 2. Runtime model v0.2 đã có run tree, handoff, projection, retention; nhưng boundary ngoài run tree vẫn mới dừng ở design intent.

### Phụ thuộc vào v0.2 baseline

- cần Slice 1 run tree ổn định
- cần Slice 2 handoff semantics đã rõ
- cần Slice 3 authoritative projection để tránh lẫn run-local vs stable reference
- cần Slice 4 retention semantics để không làm mờ traceability khi exchange xuất hiện

### Phân loại

**Must-have cho v0.3**

## Candidate B — Close-run / Continue-run operational refinement

### Mô tả

Làm rõ hành vi operational của `continue_pending`: artifact nào được giữ làm continuity set, handoff nào được coi là current-next-step payload, và boundary nào cần exchange thật.

### Vì sao quan trọng

v0.2 đã có decision semantics nhưng còn hẹp ở mức materialization và retention. Nếu mở `exchange/` mà không làm rõ `continue_pending`, ATP sẽ dễ drift ở logic continuity.

### Phụ thuộc vào v0.2 baseline

Phụ thuộc trực tiếp vào handoff materialization và retention semantics của v0.2.

### Phân loại

**Must-have cho v0.3**, nhưng nên đi kèm Candidate A thay vì tách thành theme riêng lớn

## Candidate C — Manifest / index strategy tối thiểu

### Mô tả

Thêm lớp reference/index tối thiểu để tra cứu:

- run nào đang current cho boundary nào
- handoff nào là current exchange payload
- authoritative artifact nào đang được trỏ ổn định

### Vì sao quan trọng

Khi ATP mới có run tree nội bộ, tra cứu bằng path trực tiếp còn chịu được. Khi bắt đầu có `exchange/`, thiếu index/reference strategy sẽ làm boundary tracking dễ rời rạc.

### Phụ thuộc vào v0.2 baseline

Phụ thuộc vào Slice 1-3 mạnh hơn Slice 4.

### Phân loại

**Good-to-have nếu capacity cho phép**, hoặc tích hợp ở mức rất nhỏ trong cùng hướng v0.3

## Candidate D — Controlled persistence model

### Mô tả

Bàn sâu hơn về persistence contract cho runtime state và artifact state.

### Vì sao chưa nên làm ngay

Đây là scope lớn hơn đáng kể so với baseline hiện tại. Nếu đưa vào v0.3 quá sớm sẽ có rủi ro kéo ATP vào persistence redesign.

### Phụ thuộc vào v0.2 baseline

Có phụ thuộc, nhưng chưa bị chặn bởi v0.2.

### Phân loại

**Defer beyond v0.3**

## Candidate E — Orchestration control enhancements

### Mô tả

Mở rộng control plane ở mức scheduling, arbitration, advanced dispatch, hoặc workflow control sâu hơn.

### Vì sao chưa nên làm ngay

Không phải gap gần nhất sau v0.2. Đây là nhánh mở rộng chức năng, không phải bước khép nốt runtime boundary model.

### Phân loại

**Defer beyond v0.3**

## 5. Kết luận đánh giá candidate

Hướng hợp lý nhất cho v0.3 không phải là mở thêm nhiều theme song song, mà là:

- hoàn thiện **boundary ngoài run tree** bằng exchange materialization tối thiểu
- đồng thời làm rõ operational semantics cho `continue_pending`
- chỉ thêm manifest/index/reference support ở mức đủ dùng để tránh drift

Nói ngắn gọn: v0.3 nên là phase **boundary-complete runtime handoff**, không phải phase persistence hay orchestration expansion.
