# ATP v0.3.0 Freeze Close-out

## 1. Freeze identity

- **Version / tag:** `v0.3.0`
- **Freeze date:** 2026-03-14
  Ghi nhận được từ annotated tag `v0.3.0` với `TaggerDate: Sat Mar 14 15:59:49 2026 +0700`.
- **Merge commit trên `main`:** `36b6a757f8561f36626a6198425c9bdc4783f720`
  - subject: `merge: integrate ATP v0.3 consolidated baseline into main`
- **Source branch dùng để integrate:** có thể recover với độ tin cậy cao là `v0.3-planning`
  - căn cứ: merge commit `v0.3.0` có second parent `64da2bb0d40aa03e1f7294ee67a2cd71d83230c7`, trùng với tip đã lưu của branch `v0.3-planning`

## 2. Scope included

ATP v0.3.0 đóng băng baseline mở rộng trên nền v0.2.0, gồm:

- Slice A: exchange boundary decision model
- Slice B: minimal exchange materialization dưới `SOURCE_DEV/workspace/exchange/current-task/<run-id>/` khi boundary yêu cầu
- Slice C: continue_pending operational continuity state
- Slice D: minimal file-based reference / index support

Theo các tài liệu consolidation v0.3, baseline này giữ rõ các semantics:

- `run_local_handoff` khác với `external_exchange_candidate`
- `handoff/` khác với `exchange/current-task/`
- `final/` giữ continuation, retention, và reference artifacts của current run
- `atp-artifacts/` vẫn chỉ dành cho authoritative projection

## 3. Scope not included

ATP v0.3.0 không bao gồm:

- persistence redesign ở mức production
- generalized index / catalog subsystem
- search/query subsystem cho references
- queue, scheduler, hay continuation engine rộng
- approval UI
- remote orchestration
- broad workflow expansion hoặc operational automation

Các nội dung trên tiếp tục nằm ngoài baseline đã freeze của v0.3.0.

## 4. Verification / validation state

Các tài liệu hiện còn trong repo cho thấy:

- `ATP_v0_3_Integration_Review.md` kết luận Slice A-D tạo thành một runtime model nhất quán, không có blocker kiến trúc hay blocker test
- `ATP_v0_3_Consolidation_Decision.md` kết luận baseline v0.3 là `consolidated baseline ready to freeze/integrate`
- review v0.3 ghi nhận rõ:
  - exchange boundary decision, exchange payload, continuation state, và reference/index support vẫn tách biệt semantics
  - repo/workspace boundary vẫn đúng
  - traceability giữa exchange, continuation, manifest reference, và authoritative refs là coherent

**Lưu ý:** output test command chi tiết và số lượng test chính xác tại thời điểm freeze không được lưu như một freeze artifact riêng trong repo; close-out này chỉ ghi kết luận validation có thể recover chắc chắn từ docs và git history.

## 5. Governance closure statement

ATP v0.3.0 được coi là freeze-ready vì:

- các slice A-D ghép thành một baseline coherent trên nền v0.2.0
- không có scope creep sang persistence redesign, scheduling, UI, remote orchestration, hay broad subsystem expansion
- pass integration review và consolidation decision đều xác nhận không có blocker
- traceability và auditability vẫn được giữ trong runtime model đã freeze

Version này đã được:

- integrate vào `main` qua merge commit `36b6a757f8561f36626a6198425c9bdc4783f720`
- gắn annotated tag `v0.3.0`

## 6. Follow-on direction

Sau freeze v0.3.0, branch hiện tại chuyển sang pha planning cho v0.4.

Từ evidence đang có trong repo, có thể xác nhận chắc chắn rằng:

- `main` đã đứng tại merge commit của `v0.3.0`
- `v0.4-planning` hiện là branch làm việc sau thời điểm v0.3.0 freeze

Các chi tiết roadmap cụ thể của v0.4 không thuộc close-out này.

## 7. Notes

- Close-out này dựa trên git tag history, merge history, và các báo cáo planning / consolidation còn lưu trong `docs/archive/reports/`.
- Không có claim nào ở đây nhằm diễn giải lại scope của v0.3.0 vượt quá những gì có thể recover chắc chắn từ evidence hiện hữu.
