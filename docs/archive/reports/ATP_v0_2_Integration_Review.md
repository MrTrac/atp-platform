# ATP v0.2 Integration Review

- **Ngày:** 2026-03-14
- **Phạm vi:** Rà soát và consolidation baseline ATP v0.2 sau khi hoàn tất Slice 1-4
- **Mục tiêu:** Kiểm tra tính nhất quán giữa docs, code, tests, và runtime model đã materialize
- **Nguồn tham chiếu chính:** `README.md`, `docs/architecture/overview.md`, Freeze Decision Record, Implementation Plan, các tài liệu design/runtime v0.2, và implementation hiện tại trong `adapters/`, `cli/`, `tests/`

## 1. Phạm vi đã review

Pass này đã rà soát chéo bốn lát cắt:

- Slice 1: run tree materialization tối thiểu trong `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- Slice 2: handoff materialization tối thiểu trong `handoff/`
- Slice 3: authoritative projection tối thiểu trong `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- Slice 4: retention / cleanup semantics tối thiểu, explicit, không auto-delete

Đồng thời đã đối chiếu:

- boundary repo/workspace
- semantic-to-path mapping
- close / continue behavior
- authoritative vs selected vs final vs handoff semantics
- coverage hiện có của unit và integration tests

## 2. Kết quả rà soát cross-slice

### 2.1 Kết luận tổng quát

Baseline Slice 1-4 hiện tạo thành một runtime model nhất quán, hẹp scope, và bám đúng planning package v0.2:

- run-local state nằm dưới `atp-runs/<run-id>/`
- handoff outputs được tách rõ khỏi `final/` và `decisions/`
- authoritative projection được tách rõ khỏi run tree dưới `atp-artifacts/`
- retention semantics không làm suy yếu traceability vì không có automatic deletion

### 2.2 Semantic-to-path mapping

Mapping hiện tại phù hợp với planning docs:

- `request` -> `request/`
- `task manifest`, `product context`, `manifest_reference` runtime copy -> `manifests/`
- routing preparation và routing decision -> `routing/`
- execution result và artifact summary -> `executor-outputs/`
- validation summary -> `validation/`
- review / approval / close-or-continue / decision state -> `decisions/`
- `inline_context`, `evidence_bundle`, `manifest_reference` handoff copy -> `handoff/`
- finalization summary và retention summary -> `final/`
- execution/materialization/cleanup logs -> `logs/`
- authoritative artifacts -> `atp-artifacts/<artifact-id>/`

### 2.3 Close / continue và retention coherence

Hành vi hiện tại nhất quán với Slice 4 scope:

- `close` và `close_rejected`: giữ run tree và authoritative projection cho traceability
- `continue_pending`: giữ runtime materials cho continuity, không đánh dấu cleanup-eligible
- chỉ `deprecated` artifact mới được đánh dấu cleanup-eligible, và chỉ sau close path
- `cleanup_actions` vẫn rỗng; cleanup chỉ ở mức explicit semantics, chưa phải engine

### 2.4 Boundary correctness

Boundary vẫn rõ:

- runtime writes đi vào `SOURCE_DEV/workspace`
- integration tests dùng `TemporaryDirectory()` với `workspace_root` tách biệt
- không có runtime state mới nào bị ghi vào ATP source repo
- `tests/fixtures/outputs` không bị dùng như runtime production zone

## 3. Findings: docs / code / tests alignment

## P1 — Không có blocking gap ở baseline hiện tại

Không phát hiện blocking issue làm baseline v0.2 mất tính nhất quán hoặc vi phạm boundary/freeze semantics.

## P2 — Drift wording nhỏ giữa overview và implementation

### Mô tả

`docs/architecture/overview.md` trước pass này vẫn mô tả workspace materialization như một phần deferred nói chung, trong khi baseline v0.2 hiện đã có runtime materialization tối thiểu cho Slice 1-4.

### Xử lý trong pass này

Đã cập nhật wording tối thiểu để phân biệt rõ:

- baseline v0.2 runtime materialization tối thiểu đã có
- production-grade runtime materialization đầy đủ vẫn deferred

## P3 — Wording phụ trợ còn kẹt ở phase planning cũ

### Mô tả

Một số wording nhỏ trong docs/test vẫn bám nhãn Slice cũ hoặc nhấn mạnh quá mức “planning package” dù implementation baseline đã tồn tại.

### Xử lý trong pass này

Đã chỉnh tối thiểu:

- `docs/design/README.md`
- docstring trong `tests/unit/test_workspace_materialization.py`

## 4. Test coverage review

Coverage hiện có đã đủ để đại diện cho baseline v0.2 Slice 1-4 ở mức hẹp, cụ thể:

- runtime root resolution theo boundary `SOURCE_DEV/platforms/ATP -> SOURCE_DEV/workspace`
- run tree zone creation
- handoff materialization trong `handoff/`
- authoritative projection path và traceability metadata
- retention semantics cho `close_rejected` và `continue_pending`
- integration happy/reject path với isolated workspace

Khoảng trống còn lại hiện không blocking:

- chưa có test integration riêng cho `continue_pending` path materialization
- chưa có test riêng cho trường hợp nhiều authoritative artifacts cùng lúc
- chưa có test xác minh `exchange/` chỉ xuất hiện khi có external boundary thật, vì baseline hiện chưa materialize `exchange/`

Các khoảng trống này được xem là deferred nhỏ, chưa chặn consolidation hiện tại.

## 5. Những gì đã fix ngay trong pass này

- cập nhật `docs/architecture/overview.md` để phản ánh đúng baseline v0.2 runtime materialization
- cập nhật wording nhỏ trong `docs/design/README.md`
- cập nhật docstring stale trong `tests/unit/test_workspace_materialization.py`

Không có code/runtime behavior change ngoài wording alignment.

## 6. Những gì được defer

- test integration riêng cho `continue_pending`
- wording cleanup sâu hơn trên toàn bộ docs liên quan runtime v0.2
- consolidation note chi tiết hơn cho `exchange/` khi bước sang phase tiếp theo

## 7. Kết luận review

ATP v0.2 Slice 1-4 hiện tạo thành một baseline runtime materialization nhất quán, đúng boundary, và đủ chặt để coi là consolidated baseline.

Tại thời điểm pass này:

- không có blocker kỹ thuật rõ ràng
- không có drift semantics lớn giữa docs, code, và tests
- các deferred còn lại là minor follow-up, không buộc phải chặn freeze/integration
