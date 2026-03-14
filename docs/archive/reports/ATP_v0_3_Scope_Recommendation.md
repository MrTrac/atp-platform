# ATP v0.3 Scope Recommendation

- **Ngày:** 2026-03-14
- **Phạm vi:** Đề xuất scope chính thức cho ATP v0.3
- **Căn cứ:** `ATP_v0_3_Candidate_Assessment.md` cùng các tài liệu authority hiện hành của ATP

## 1. Recommended v0.3 direction

ATP v0.3 nên tập trung vào một hướng hẹp và liên tục với v0.2:

**Hoàn thiện runtime handoff boundary ngoài run tree bằng exchange materialization tối thiểu, đi kèm refinement nhỏ cho `continue_pending` và reference/index support đủ dùng.**

## 2. Vì sao đây là bước tiếp theo đúng nhất

Sau v0.2, ATP đã có:

- run tree rõ
- handoff trong run tree rõ
- authoritative projection rõ
- retention semantics tối thiểu rõ

Phần còn hở đáng kể nhất của runtime model là:

- khi nào handoff phải rời `handoff/` trong run tree
- `exchange/` được materialize ra sao mà không biến thành subsystem rộng
- `continue_pending` bám boundary nào ở mức operational

Nếu bỏ qua gap này và nhảy sang persistence, UI, hay orchestration expansion, ATP sẽ mở rộng trên một boundary model chưa khép nốt.

## 3. Scope được khuyến nghị cho v0.3

### Must-have

- exchange materialization tối thiểu khi có external handoff boundary thật
- rule rõ cho `continue_pending` gắn với handoff / exchange boundary
- reference/index tối thiểu để trỏ tới current exchange payload hoặc current next-step manifest/reference

### Good-to-have nếu capacity cho phép

- inspect/trace summary nhỏ cho exchange boundary
- test coverage rộng hơn cho nhiều authoritative artifacts hoặc nhiều handoff case

### Không nên đưa vào v0.3

- persistence redesign
- approval UI
- remote orchestration hoàn chỉnh
- advanced scheduling
- broad cleanup automation
- artifact management subsystem rộng

## 4. Scope statement đề xuất cho v0.3

ATP v0.3 là phase:

**“minimal external handoff boundary completion”**

chứ không phải:

- “production persistence phase”
- “UI phase”
- “remote orchestration phase”

## 5. Expected outcome nếu chọn scope này

Nếu đi theo hướng trên, ATP sẽ đạt được:

- boundary model hoàn chỉnh hơn giữa run-local handoff và external handoff
- semantics rõ hơn cho `continue_pending`
- traceability tốt hơn khi bước tiếp theo không còn nằm hoàn toàn trong run tree hiện tại

Đây là bước hợp logic nhất sau v0.2 vì vẫn bám:

- artifact-centric
- human-gated
- boundary-first
- scope hẹp, ít rủi ro

## 6. Recommendation summary

Khuyến nghị chính thức:

ATP v0.3 nên chọn **exchange boundary + continue operational refinement** làm scope trung tâm.

Manifest/index/reference support chỉ nên đi kèm ở mức tối thiểu để phục vụ scope này, không tách thành một initiative lớn riêng.
