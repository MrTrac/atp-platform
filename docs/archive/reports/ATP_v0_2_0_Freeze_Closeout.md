# ATP v0.2.0 Freeze Close-out

## 1. Freeze identity

- **Version / tag:** `v0.2.0`
- **Freeze date:** 2026-03-14
  Ghi nhận được từ annotated tag `v0.2.0` với `TaggerDate: Sat Mar 14 15:25:58 2026 +0700`.
- **Merge commit trên `main`:** `022b18fb48cc2a28dee9eaa60938c3c418ee6816`
  - subject: `merge: integrate ATP v0.2 consolidated baseline into main`
- **Source branch dùng để integrate:** có thể recover với độ tin cậy cao là `v0.2-slice4-retention-cleanup`
  - căn cứ: merge commit `v0.2.0` có second parent `fdbeaf6571b3cf8badf64a881f0278f8886d0644`, trùng với tip đã lưu của branch `v0.2-slice4-retention-cleanup`

## 2. Scope included

ATP v0.2.0 đóng băng baseline runtime materialization tối thiểu dưới `SOURCE_DEV/workspace`, gồm:

- Slice 1: run tree materialization dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- Slice 2: handoff materialization tối thiểu trong `handoff/`
- Slice 3: authoritative projection tối thiểu dưới `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- Slice 4: retention / cleanup semantics tối thiểu, explicit, không auto-delete

Theo các tài liệu consolidation v0.2, baseline này cũng giữ rõ các ranh giới sau:

- repo/workspace boundary không bị blur
- run-local artifacts, handoff outputs, final outputs, và authoritative projections là các lớp khác nhau
- cleanup chỉ dừng ở mức semantics explicit, chưa phải engine

## 3. Scope not included

ATP v0.2.0 không bao gồm:

- `exchange/` materialization cho external handoff boundary
- continue-pending operational continuity state ở mức runtime riêng
- reference / index support file-based cho exchange và continuation
- persistence redesign ở mức production
- approval UI
- remote orchestration plane hoàn chỉnh
- advanced scheduling
- broad artifact lifecycle management hoặc cleanup automation

Các nội dung trên chỉ xuất hiện ở pha sau hoặc tiếp tục được defer sau v0.2.0.

## 4. Verification / validation state

Các tài liệu hiện còn trong repo cho thấy:

- `ATP_v0_2_Integration_Review.md` kết luận Slice 1-4 tạo thành một runtime model nhất quán, đúng boundary, và không có blocker kỹ thuật rõ ràng
- `ATP_v0_2_Consolidation_Decision.md` kết luận baseline v0.2 là `consolidated baseline ready to freeze/integrate`
- review v0.2 ghi nhận coverage đã có cho:
  - runtime root resolution
  - run tree zone creation
  - handoff materialization
  - authoritative projection path và traceability metadata
  - retention semantics cho close path và continue path ở mức hẹp
  - happy path / reject path integration với isolated workspace

**Lưu ý:** output test command chi tiết và số lượng test chính xác tại thời điểm freeze không được lưu rõ trong freeze-closeout evidence hiện có, nên không ghi suy diễn ở đây.

## 5. Governance closure statement

ATP v0.2.0 được coi là freeze-ready vì:

- bốn slice tạo thành một baseline runtime materialization hẹp, coherent, và bám đúng frozen ATP architecture
- repo/workspace boundary vẫn explicit
- semantics giữa run tree, handoff, projection, và retention không chồng lấn sai
- pass integration review và consolidation decision đều xác nhận không có blocker

Version này đã được:

- integrate vào `main` qua merge commit `022b18fb48cc2a28dee9eaa60938c3c418ee6816`
- gắn annotated tag `v0.2.0`

## 6. Follow-on direction

Sau freeze v0.2.0, hướng tiếp theo trở thành ATP v0.3 planning, tập trung vào:

- exchange boundary decision model
- minimal exchange materialization
- continue_pending operational continuity
- minimal reference / index support

Điều này khớp với bộ tài liệu planning và consolidation v0.3 hiện có trong `docs/archive/reports/`.

## 7. Notes

- Close-out này được dựng từ git tag history, merge history, và các báo cáo planning / consolidation còn lưu trong repo.
- Nếu cần audit sâu hơn về test command output tại thời điểm freeze, repo hiện không giữ một freeze artifact riêng cho transcript đó; vì vậy close-out này chỉ ghi những gì recover được với độ tin cậy đủ cao.
