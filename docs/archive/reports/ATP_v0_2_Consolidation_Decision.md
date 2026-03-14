# ATP v0.2 Consolidation Decision

- **Ngày:** 2026-03-14
- **Phạm vi quyết định:** Consolidation decision cho ATP v0.2 sau khi hoàn tất Slice 1-4 và pass integration review
- **Căn cứ:** `ATP_v0_2_Integration_Review.md` cùng các tài liệu authority của ATP

## 1. Trạng thái hiện tại của ATP v0.2

ATP v0.2 hiện đã có baseline runtime materialization tối thiểu, gồm:

- run tree materialization trong `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- handoff materialization tối thiểu trong `handoff/`
- authoritative projection tối thiểu trong `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- retention / cleanup semantics tối thiểu, explicit, không auto-delete

Baseline này vẫn giữ nguyên kiến trúc ATP đã freeze:

- platform-first
- provider-agnostic
- adapter-first
- artifact-centric
- human-gated
- boundary rõ giữa source repo và runtime workspace

## 2. Quyết định consolidation

### Quyết định

ATP v0.2 hiện **đủ điều kiện để được coi là consolidated baseline ready to freeze/integrate**.

### Lý do

- Slice 1-4 ghép lại thành một runtime model nhất quán
- boundary repo/workspace vẫn rõ và được test
- semantics giữa run tree, handoff, authoritative projection, và retention không chồng lấn sai
- không có blocker kỹ thuật rõ ràng trong pass integration review
- test hiện có xác nhận baseline hoạt động ổn định cho happy path, reject path, projection, và retention semantics hẹp

## 3. Blockers

Không có blocker nào được xác định trong pass consolidation này.

## 4. Minor deferred items

Các mục sau được defer mà không chặn consolidation:

- test integration riêng cho `continue_pending` path
- wording cleanup sâu hơn cho một số docs runtime v0.2 liên quan
- thiết kế và implementation của `exchange/` nếu sau này xuất hiện external handoff boundary thật
- retention engine rộng hơn hoặc automation cleanup

## 5. Điều không được suy diễn từ quyết định này

Quyết định consolidation này **không** có nghĩa ATP đã có:

- persistence redesign ở mức production
- UI cho approval/review
- remote orchestration plane hoàn chỉnh
- full artifact lifecycle management
- broad cleanup automation

Đây chỉ là xác nhận rằng baseline v0.2 hiện tại đủ nhất quán và đủ hẹp để freeze/integrate như một bước hợp lệ trong roadmap.

## 6. Recommended next step

Bước tiếp theo được khuyến nghị:

1. chốt freeze/integration cho baseline v0.2 hiện tại
2. nếu cần, mở một task nhỏ hậu consolidation chỉ để:
   - bổ sung test `continue_pending` integration
   - làm wording cleanup nhỏ trong docs active

Không nên mở feature slice mới hoặc redesign runtime model trong cùng pass consolidation này.
