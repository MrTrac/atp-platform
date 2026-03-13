# Artifact Model

Artifact la don vi dau ra/dua vao chinh cua ATP. Trong M1-M2, artifact model moi chi dung de khoa naming cho cac phase sau, chua co materialization logic.

Artifact seed fields:

- `artifact_id`
- `artifact_type`
- `run_id`
- `product`
- `capability`
- `artifact_freshness`
- `authoritative`
- `manifest_reference`
- `metadata`

Quy uoc seed:

- `artifact_freshness` mo ta do moi cua artifact, vi du `current` hoac `stale`
- `authoritative` danh dau artifact nao la nguon su that cua run hien tai
- `manifest_reference` cho phep tro den manifest artifact ma khong can no data duplication

M1-M2 chua co store, retention, version chain, hay bundle materialization.
