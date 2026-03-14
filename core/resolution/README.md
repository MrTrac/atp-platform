# Resolution

`core/resolution` chứa implementation M3 cho Product Resolution.

Hiện hành resolve:

- `ATP`
- `TDF`

Nguồn resolve:

- product registry trong `registry/products`
- product profile trong `profiles/<product>/profile.yaml`
- policy registry seed trong `registry/policies`

Kết quả resolve gồm:

- product da chon
- `repo_boundary`
- profile da load
- danh sach policy da load

Deferred rõ ràng:

- context packaging
- routing
- execution
- validation/review
- approval/finalization
