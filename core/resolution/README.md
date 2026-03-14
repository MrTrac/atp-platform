# Resolution

`core/resolution` chứa resolution boundary của ATP.

Phạm vi hiện hành:

- file-based product resolution cho `ATP` và `TDF`
- load registry entry, product profile, và policy refs tối thiểu
- build explicit v0.5 Slice A `request-to-product` resolution contract

Resolution boundary này phải giữ rõ separation với:

- classification
- routing
- provider selection
- broader product-portfolio orchestration

Nguồn resolve:

- product registry trong `registry/products`
- product profile trong `profiles/<product>/profile.yaml`
- policy registry seed trong `registry/policies`

Kết quả hiện hành gồm hai lớp:

- legacy resolution payload dùng cho flow hiện có
- request-to-product resolution contract với:
  - `product_target`
  - `capability_target`
  - `resolution_rationale`
  - `resolution_scope`
  - `traceability`

Deferred rõ ràng:

- context packaging
- routing
- execution
- validation/review
- approval/finalization
- product portfolio orchestration
