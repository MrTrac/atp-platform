# Quy tắc boundary runtime của ATP

- **Mục đích:** Chốt rõ boundary giữa source repo và runtime workspace khi ATP bước sang v0.2 planning.
- **Phạm vi:** Repo vs workspace, cross-boundary references, và các điều cấm về runtime state.
- **Trạng thái:** Planning for v0.2.
- **Tài liệu liên quan:** `../architecture/repo_boundary.md`, `../operators/workspace_layout.md`, `ATP_Runtime_Materialization_Model.md`.

## Boundary nền

- `SOURCE_DEV/platforms/ATP` là source repo của ATP
- `SOURCE_DEV/workspace` là runtime zone của ATP
- `SOURCE_DEV/products/TDF` là product repo ATP có thể resolve, nhưng không phải runtime zone

## Cái gì thuộc repo

- source code ATP
- schemas
- tests
- docs và governance
- fixture examples
- planning packages và reference models

## Cái gì thuộc workspace

- request materialized cho từng run
- execution outputs của run thật
- validation, review, approval, finalization outputs của run thật
- handoff bundles và exchange materials
- logs vận hành
- cache và staging runtime

## Cái gì có thể đi qua boundary

- path reference
- `manifest_reference`
- `artifact_id`
- summary metadata
- explicit handoff payload được ATP chọn lọc

## Cái gì không được coi là repo-local runtime state

- run tree của run thật
- authoritative artifact của run thật
- logs vận hành thật
- exchange bundle đang dùng trong workflow thật
- approval/finalization state của run thật

## Quy tắc cross-reference

- Repo có thể trỏ đến workspace bằng reference hoặc documented path shape
- Workspace không phải nơi chứa source-of-truth cho architecture docs
- Một runtime file chỉ trở thành nguồn sự thật cục bộ cho run của nó, không thay thế authority docs trong repo

## Quy tắc anti-blur

- Không dùng `tests/fixtures/outputs` như runtime production zone
- Không commit runtime outputs vào ATP repo
- Không đọc toàn bộ workspace một cách mù để giao cho executor hoặc AI
- Không coi cache hoặc staging là authoritative artifact zone

## Rule cho v0.2 implementation slices

- Slice đầu chỉ materialize những semantic đã có trong ATP v0
- Không thêm runtime subsystem mới chỉ để “cho đủ”
- Nếu một runtime output chưa có semantic ổn định trong v0, chưa materialize nó ở slice đầu
