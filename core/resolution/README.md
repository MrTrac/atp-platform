# Resolution

`core/resolution` chua implementation M3 cho Product Resolution.

M3 hien tai resolve:

- `ATP`
- `TDF`

Nguon resolve:

- product registry trong `registry/products`
- product profile trong `profiles/<product>/profile.yaml`
- policy registry seed trong `registry/policies`

Ket qua resolve gom:

- product da chon
- `repo_boundary`
- profile da load
- danh sach policy da load

Deferred ro rang cho M4+:

- context packaging
- routing
- execution
- validation/review
- approval/finalization
