# Request Model

Request la input control-plane cua ATP. Trong M4, request model van giu field shape cua M1-M3 va tro thanh dau vao cho Context Packaging.

Top-level fields toi thieu sau normalize:

- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `payload`
- `metadata`

M4 su dung request da normalize de:

- tao `task_manifest`
- gan `request_id` va `product` cho artifact context
- ghi nhan artifact refs dau vao cho continuity cua buoc tiep theo

Task Manifest v0 chua:

- `manifest_id`
- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `required_capabilities`
- `target_scope`
- `input_artifacts`
- `notes`

M4 chua lam request enrichment sau context packaging, routing, hay execution decisions.
