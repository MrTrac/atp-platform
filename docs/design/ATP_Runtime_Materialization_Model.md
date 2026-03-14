# Mô hình runtime materialization của ATP

- **Mục đích:** Mô tả cách ATP materialize semantics vào `SOURCE_DEV/workspace` trong phase v0.2 mà không đổi kiến trúc đã freeze.
- **Phạm vi:** Runtime directory model, semantic-to-path mapping, và implementation slicing cho runtime materialization.
- **Trạng thái:** Planning for v0.2.
- **Tài liệu liên quan:** `artifact_model.md`, `handoff_model.md`, `../architecture/repo_boundary.md`, `../operators/workspace_layout.md`.

## Nguyên tắc nền

- ATP source repo vẫn là `SOURCE_DEV/platforms/ATP`
- Runtime artifact chỉ thuộc `SOURCE_DEV/workspace`
- Materialization là bước đưa semantics đã có của ATP v0 ra runtime layout rõ ràng hơn
- v0.2 planning không mở rộng sang UI, remote orchestration, hay persistence redesign

## Runtime workspace model đề xuất

ATP nên materialize dưới các zone ổn định sau:

```text
SOURCE_DEV/workspace/
├── atp-runs/
│   └── <run-id>/
│       ├── request/
│       ├── manifests/
│       ├── routing/
│       ├── executor-outputs/
│       ├── validation/
│       ├── decisions/
│       ├── handoff/
│       ├── final/
│       └── logs/
├── atp-artifacts/
│   └── <artifact-id>/
├── atp-cache/
├── atp-staging/
└── exchange/
    ├── current-task/
    ├── current-review/
    └── current-approval/
```

## Vai trò của từng zone

- `atp-runs/` - runtime record theo từng run; là nơi nhìn flow từ đầu đến cuối
- `atp-artifacts/` - vùng lưu artifact materialized theo `artifact_id` khi một artifact cần được tham chiếu ổn định ngoài run tree
- `atp-cache/` - cache tạm, có thể xoá; không phải authority
- `atp-staging/` - vùng chuẩn bị vật liệu trước khi promote sang run tree hoặc exchange
- `exchange/` - handoff zone cho task, review, approval theo boundary rõ ràng

## Semantic-to-path mapping mức run

| ATP semantic | Runtime path chính |
| --- | --- |
| request | `atp-runs/<run-id>/request/` |
| task manifest / product context | `atp-runs/<run-id>/manifests/` |
| routing preparation / route selection | `atp-runs/<run-id>/routing/` |
| execution output | `atp-runs/<run-id>/executor-outputs/` |
| validation output | `atp-runs/<run-id>/validation/` |
| approval state / review decision | `atp-runs/<run-id>/decisions/` |
| handoff package / references | `atp-runs/<run-id>/handoff/` hoặc `exchange/` nếu cần giao bước tiếp theo |
| finalization result | `atp-runs/<run-id>/final/` |
| log vận hành | `atp-runs/<run-id>/logs/` |

## Semantic-to-path mapping mức workspace

- `manifest_reference` có thể trỏ vào file trong `atp-runs/<run-id>/manifests/` hoặc `final/` tùy decision boundary
- `evidence_bundle` nên materialize ưu tiên trong `handoff/` của run hiện tại
- `exchange_bundle` chỉ nên xuất hiện trong `exchange/` khi thực sự cần handoff qua boundary ngoài run tree
- `authoritative artifact` có thể được materialize thêm trong `atp-artifacts/<artifact-id>/` nếu cần tham chiếu ổn định qua nhiều bước

## Boundary rules đi kèm

- Repo chỉ chứa code, schema, docs, tests, và planning artifact
- Workspace chỉ chứa runtime materialized outputs
- Repo có thể giữ path reference hoặc example shape, nhưng không giữ runtime state của run thật
- Không coi `tests/fixtures/outputs` là runtime zone; đó chỉ là test-safe fixture area

## Implementation slicing cho v0.2

### Slice 1 — Run tree materialization tối thiểu
- materialize `request/`, `manifests/`, `routing/`, `executor-outputs/`, `validation/`, `decisions/`, `final/`
- chưa tách `atp-artifacts/` riêng ngoài run tree
- chưa có retention engine

### Slice 2 — Handoff và exchange materialization tối thiểu
- materialize `handoff/` trong run tree
- chỉ tạo `exchange/` khi một handoff thật sự cần boundary ngoài run hiện tại

### Slice 3 — Authoritative artifact projection
- project selected authoritative artifact sang `atp-artifacts/`
- giữ mapping từ `artifact_id` về `run-id` và `source_stage`

### Slice 4 — Cleanup và retention rules tối thiểu
- ghi rõ artifact nào tạm thời
- quy định cái gì được cleanup sau close-run
- chưa cần automation cleanup phức tạp

## Khuyến nghị

Slice đầu tiên nên là **Run tree materialization tối thiểu**. Đây là slice ít rủi ro nhất vì bám trực tiếp flow M1-M8 hiện có và không ép ATP phải thiết kế lại artifact store hay exchange model.
