# Request Model

Request la input control-plane cua ATP. Trong M3, request model tiep tuc giu field shape cua M1-M2 va them vai tro cho Product Resolution.

Top-level fields toi thieu sau normalize:

- `request_id`
- `product`
- `request_type`
- `execution_intent`
- `payload`
- `metadata`

Field lien quan den resolve:

- `product` la nguon uu tien cao nhat neu co
- `product_hint` co the duoc normalizer map sang `product`
- classification co the lap lai `product` de resolver dung khi can

M3 Product Resolution se:

- chon product tu request da normalize
- load product registry entry
- load product profile lien ket
- load policy refs toi thieu

M3 chua lam request enrichment sau resolution hay context packaging.
