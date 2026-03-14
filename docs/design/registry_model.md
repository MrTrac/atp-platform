# Mô hình registry

ATP dùng file-based registry để phục vụ resolution, routing, và policy lookup theo hướng nhẹ, deterministic, và dễ kiểm soát authority.

## Các registry chính trong ATP v0

- Product Registry trong `registry/products`
- Policy Registry trong `registry/policies`
- Product Profiles trong `profiles/<product>/profile.yaml`
- Capability Registry trong `registry/capabilities`
- Provider Registry trong `registry/providers`
- Node Registry trong `registry/nodes`

## Capability registry trong v0

Tối thiểu chứa:

- `capability`
- `description`
- `category`
- `supported_provider_types`
- `notes`

## Provider registry trong v0

Tối thiểu chứa:

- `provider`
- `provider_type`
- `supported_capabilities`
- `supported_nodes`
- `interaction_pattern`
- `cost_profile`

## Node registry trong v0

Tối thiểu chứa:

- `node`
- `node_type`
- `locality`
- `supported_provider_types`
- `status`

## Route preparation lấy gì từ registry

Để tạo ra:

- `required_capabilities`
- `candidate_providers`
- `candidate_nodes`
- `routing_policy_refs`
- `cost_policy_refs`

## Ghi chú

Route selection trong ATP v0 vẫn là rule-based, local-first, và chưa có arbitration engine động.
