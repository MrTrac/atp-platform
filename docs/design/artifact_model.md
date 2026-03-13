# Artifact Model

Artifact la don vi dau ra/dua vao chinh cua ATP. Trong M4, artifact model bat dau co vai tro cu the hon cho Context Packaging.

Artifact seed fields:

- `artifact_id`
- `artifact_type`
- `run_id`
- `product`
- `artifact_freshness`
- `authoritative`
- `manifest_reference`
- `metadata`

Artifact types duoc dung trong M4:

- `request_raw`
- `request_normalized`
- `classification`
- `resolution`
- `task_manifest`
- `product_context`

Evidence Selection v0:

- chi chon artifact cot loi cho next-step continuity
- uu tien artifact co `authoritative: true`
- khong scan workspace hay repo ngoai ATP

M4 van chua co artifact store, retention, version chain, hay exchange materialization.
