# Bản đồ lifecycle artifact của ATP

- **Mục đích:** Chuyển artifact semantics của ATP v0 thành lifecycle map có thể materialize an toàn trong v0.2.
- **Phạm vi:** Intermediate artifacts, validation artifacts, final artifacts, handoff artifacts, authoritative selection, và retention assumptions.
- **Trạng thái:** Planning for v0.2.
- **Tài liệu liên quan:** `artifact_model.md`, `handoff_model.md`, `ATP_Runtime_Materialization_Model.md`.

## Các nhóm artifact chính

### 1. Intermediate artifacts

Artifact phục vụ flow nội bộ trước khi chốt kết quả:

- raw request
- normalized request
- classification
- resolution
- task manifest
- product context
- routing preparation
- routing decision
- raw execution output
- filtered execution output

### 2. Validation artifacts

Artifact hoặc summary phản ánh bước review quyết định:

- validation summary
- review decision
- approval result

### 3. Final artifacts

Artifact chốt run hiện tại:

- finalization summary
- close-run / continue-run decision
- final manifest reference nếu có

### 4. Handoff artifacts

Artifact dùng cho bước tiếp theo:

- `inline_context`
- `evidence_bundle`
- `exchange_bundle`
- `manifest_reference`

## Lifecycle chuẩn

```text
raw -> filtered -> selected -> authoritative -> deprecated
```

## Ý nghĩa từng state trong runtime materialization

- `raw` - output vừa capture, chưa lọc
- `filtered` - đã rút gọn để phục vụ validation, review, summary
- `selected` - đã được chọn cho continuity hoặc handoff
- `authoritative` - artifact có hiệu lực hiện tại cho boundary đang xét
- `deprecated` - vẫn giữ traceability nhưng không còn là nguồn sự thật hiện hành

## Rule chọn authoritative artifact

- `selected` không tự động trở thành `authoritative`
- Một authoritative artifact phải gắn được với:
  - `run_id`
  - `source_stage`
  - `artifact_freshness`
  - decision boundary hoặc handoff boundary liên quan
- Mỗi boundary nên có tối đa một authoritative artifact chính cho cùng một semantic concern

## Mapping lifecycle sang runtime zones

| Lifecycle concern | Zone ưu tiên |
| --- | --- |
| intermediate flow artifacts | `atp-runs/<run-id>/request`, `manifests`, `routing`, `executor-outputs` |
| validation / approval artifacts | `atp-runs/<run-id>/validation`, `decisions` |
| final artifacts | `atp-runs/<run-id>/final` |
| handoff artifacts | `atp-runs/<run-id>/handoff` hoặc `exchange/` |
| projected authoritative artifacts | `atp-artifacts/<artifact-id>/` nếu slice sau yêu cầu |

## Retention assumptions cho v0.2 planning

- `raw` và `filtered` có thể giữ trong run tree để traceability
- `selected` và `authoritative` nên giữ lâu hơn `raw`
- `deprecated` có thể cleanup theo policy sau khi không còn cần traceability gần
- `cache` và `staging` không phải retention authority

## Deferred cleanup assumptions

- Cleanup không phải slice đầu
- v0.2 slice đầu chỉ cần materialize nhất quán trước
- retention policy đầy đủ chỉ nên bàn khi run tree đã ổn định
