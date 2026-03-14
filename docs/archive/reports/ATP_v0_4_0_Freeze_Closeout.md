# ATP v0.4.0 Freeze Close-out

## 1. Freeze identity

- **Version / tag:** `v0.4.0`
- **Freeze date:** 2026-03-14
  Ghi nhận được từ annotated tag `v0.4.0` với `TaggerDate: Sat Mar 14 19:39:28 2026 +0700`.
- **Merge commit trên `main`:** `6985db68ac7e5975dc8335a0f7025702926293a2`
  - subject: `merge: integrate ATP v0.4 consolidated baseline into main`
- **Source branch dùng để integrate:** có thể recover với độ tin cậy cao là `v0.4-planning`
  - căn cứ: merge commit `v0.4.0` có second parent `f6953421c13b1f1c4d659ef8d21834be4fca0930`, trùng với tip đã lưu của branch `v0.4-planning`

## 2. Scope included

ATP v0.4.0 đóng băng baseline mở rộng trên nền v0.3.0, gồm:

- Slice A: current-task persistence contract
- Slice B: continue-pending recovery contract
- Slice C: active/supersede pointer traceability
- Slice D: read-only inspect surface

Theo các tài liệu consolidation v0.4, baseline này giữ rõ các semantics:

- current-task persistence khác với recovery contract
- recovery contract khác với recovery execution
- active pointer và supersede trace chỉ là traceability artifacts, không phải pointer management subsystem
- inspect surface chỉ là read-only view lên runtime artifacts đã materialize

## 3. Scope not included

ATP v0.4.0 không bao gồm:

- production persistence redesign
- scheduler / queue behavior
- remote orchestration
- approval UI hoặc broad operator console
- generalized pointer/index/search subsystem
- recovery execution engine
- pointer cleanup hoặc management subsystem rộng

Các nội dung trên tiếp tục nằm ngoài baseline đã freeze của v0.4.0.

## 4. Verification / validation state

Các tài liệu hiện còn trong repo cho thấy:

- `ATP_v0_4_Integration_Review.md` kết luận Slice A-D tạo thành một operational runtime model nhất quán, không có blocker kiến trúc hay blocker test
- `ATP_v0_4_Consolidation_Decision.md` kết luận baseline v0.4 là `consolidated baseline ready to freeze/integrate`
- review v0.4 ghi nhận rõ:
  - current-task persistence, recovery contract, active pointer, supersede trace, và inspect vẫn tách biệt semantics
  - repo/workspace boundary vẫn đúng
  - inspect surface vẫn read-only

**Lưu ý:** output test command chi tiết tại đúng thời điểm freeze không được lưu như một freeze artifact riêng trong repo; close-out này chỉ ghi kết luận validation có thể recover chắc chắn từ docs và git history.

## 5. Governance closure statement

ATP v0.4.0 được coi là freeze-ready vì:

- các slice A-D ghép thành một baseline coherent trên nền v0.3.0
- không có scope creep sang production persistence redesign, scheduler/queue, UI, remote orchestration, hay broad subsystem expansion
- pass integration review và consolidation decision đều xác nhận không có blocker
- traceability, inspect clarity, và boundary discipline vẫn được giữ trong runtime model đã freeze

Version này đã được:

- integrate vào `main` qua merge commit `6985db68ac7e5975dc8335a0f7025702926293a2`
- gắn annotated tag `v0.4.0`

## 6. Follow-on direction

Sau freeze v0.4.0, branch hiện tại chuyển sang pha planning cho v0.5.

Từ evidence đang có trong repo, có thể xác nhận chắc chắn rằng:

- `main` đã đứng tại merge commit của `v0.4.0`
- `v0.5-planning` hiện là branch làm việc sau thời điểm v0.4.0 freeze

Chi tiết implementation scope của v0.5 phải được xác định qua planning baseline riêng, không suy diễn từ close-out này.

## 7. Notes

- Close-out này dựa trên git tag history, merge history, và các báo cáo planning / consolidation còn lưu trong `docs/archive/reports/`.
- Không có claim nào ở đây nhằm diễn giải lại scope của v0.4.0 vượt quá những gì có thể recover chắc chắn từ evidence hiện hữu.
