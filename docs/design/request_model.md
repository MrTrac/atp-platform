# Request Model

Request la input control-plane cua ATP. Trong M1-M2, request model co muc tieu on dinh ten truong va cho phep load/normalize/classify som, chua enforce schema sau.

Top-level fields toi thieu sau normalize:

- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `payload`
- `metadata`

Nguon vao co the chua cac truong seed khac nhu:

- `product_hint`
- `input_text`
- `provider`
- `adapter`
- `capability`

Normalization rules trong M1-M2:

- `product` co the lay tu `product` hoac `product_hint`
- `payload` luon la object, co the chua `input_text`
- `metadata` luon la object
- field khong nhan dien van duoc giu lai de tranh mat thong tin

M2 chua lam:

- deep schema validation
- request enrichment tu registry
- product resolution
