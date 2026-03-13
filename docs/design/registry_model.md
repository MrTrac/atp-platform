# Registry Model

M3 dua Product Resolution vao file-based registry nhe, deterministic.

Registry phuc vu M3:

- Product Registry trong `registry/products`
- Policy Registry trong `registry/policies`
- Product Profiles trong `profiles/<product>/profile.yaml`

Product registry entry toi thieu:

- `product`
- `product_type`
- `repo_boundary`
- `profile_ref`
- `policy_refs`
- `status`

Policy loading trong v0 co nghia la:

- doc file policy theo `policy_refs`
- khong merge engine
- khong override chain
- khong policy evaluation runtime

ATP va TDF la hai product dau tien duoc support trong M3.
