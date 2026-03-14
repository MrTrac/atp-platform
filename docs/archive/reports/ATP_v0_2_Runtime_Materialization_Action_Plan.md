# ATP v0.2 Runtime Materialization Action Plan

- **Ngày:** 2026-03-14
- **Phạm vi:** Planning package cho ATP runtime materialization sau baseline v0.1.0
- **Nguyên tắc:** planning trước, implementation sau; không mở rộng kiến trúc đã freeze

## Phase opening note

- Repo state hiện tại sạch tại thời điểm mở phase planning
- Branch hiện tại đọc được từ repo là `main`
- Theo yêu cầu phase, v0.1.0 được coi là closed baseline để planning v0.2
- Pass này chỉ tạo planning package, không triển khai runtime materialization thật

## Mục tiêu của planning package

1. Chốt runtime workspace model dưới `SOURCE_DEV/workspace`
2. Làm rõ artifact lifecycle khi materialize
3. Map ATP semantics sang runtime path một cách nhất quán
4. Siết boundary repo/workspace rõ hơn trước khi code
5. Chia implementation v0.2 thành các slice nhỏ, ít rủi ro

## Immediate planning outputs

- `docs/design/ATP_Runtime_Materialization_Model.md`
- `docs/design/ATP_Artifact_Lifecycle_Map.md`
- `docs/design/ATP_Runtime_Boundary_Rules.md`

## Recommended implementation slices

### Slice 1 — Run tree materialization tối thiểu
- materialize run tree dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- ưu tiên `request`, `manifests`, `routing`, `executor-outputs`, `validation`, `decisions`, `final`
- không thêm retention engine
- không tách subsystem mới

### Slice 2 — Handoff materialization tối thiểu
- thêm `handoff/` trong run tree
- chỉ materialize `exchange/` khi boundary handoff thực sự cần

### Slice 3 — Authoritative artifact projection
- project authoritative artifact sang `SOURCE_DEV/workspace/atp-artifacts/`
- giữ mapping về `run-id` và `source_stage`

### Slice 4 — Retention và cleanup tối thiểu
- ghi chính sách giữ/xoá cơ bản
- vẫn tránh automation cleanup phức tạp

## Recommended first slice for v0.2

Slice nên làm đầu tiên là **Run tree materialization tối thiểu**.

Lý do:
- bám sát flow M1-M8 hiện có
- ít động đến contracts nhất
- giúp CLI và inspect có runtime target rõ hơn
- không buộc ATP phải mở rộng sang persistence architecture lớn

## Deferred questions

- Khi nào `manifest_reference` nên trỏ vào `manifests/` hay `final/`
- Có cần project mọi authoritative artifact sang `atp-artifacts/` ngay slice đầu hay chưa
- Mức retention tối thiểu nào là đủ cho close-run vs continue-run
- Khi nào `exchange/` là cần thiết thay vì chỉ `handoff/` trong run tree

## Next-step recommendation

Sau planning package này, bước tiếp theo nên là một implementation task hẹp cho Slice 1, với acceptance criteria chỉ xoay quanh:

- materialize đúng run tree
- không commit runtime output vào repo
- không đổi freeze semantics
- test được path mapping và boundary behavior
