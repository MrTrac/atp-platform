# Flow orchestration

ATP v0 giữ nguyên flow orchestration đã được khóa ở mức kiến trúc, và baseline hiện tại đã bao phủ trọn 14 bước đến M8.

## Flow chuẩn đang có hiệu lực

1. Request Intake
2. Normalize
3. Input Classification
4. Product Resolution
5. Context Packaging
6. Routing Preparation
7. Route Selection
8. Execution via Adapter
9. Capture Output
10. Validation / Review
11. Approval Gate
12. Finalization
13. Handoff to Next Step
14. Close Run or Continue

## Trạng thái implementation hiện tại

ATP MVP v0 đã có baseline repo-local cho toàn bộ flow trên. Điều này có nghĩa là ATP đã đi hết chuỗi điều phối logic, dù một số phần vẫn dừng ở mức summary hoặc placeholder thay vì production side effect.

## Vai trò của M8 trong baseline

M8 chốt phần cuối của flow bằng cách bổ sung:

- `approval gate` summary với các trạng thái như `approved`, `rejected`, `needs_attention`
- các handoff output chuẩn:
  - `inline_context`
  - `evidence_bundle`
  - `exchange_bundle`
  - `manifest_reference`
- `finalization` summary
- quyết định `close-run` hoặc `continue-run`

## Các giới hạn còn giữ nguyên sau M8

ATP v0 vẫn chưa có:

- human approval UI
- production workspace materialization
- remote orchestration plane đầy đủ
- advanced scheduling
- inspect plane backed bởi persistence ở mức production
