# Registry Model

M5 mo rong file-based registry cua ATP de phuc vu routing capability-based, van giu nhe va deterministic.

Registry phuc vu M5:

- Product Registry trong `registry/products`
- Policy Registry trong `registry/policies`
- Product Profiles trong `profiles/<product>/profile.yaml`
- Capability Registry trong `registry/capabilities`
- Provider Registry trong `registry/providers`
- Node Registry trong `registry/nodes`

Capability registry v0 chua:

- `capability`
- `description`
- `category`
- `supported_provider_types`
- `notes`

Provider registry v0 chua:

- `provider`
- `provider_type`
- `supported_capabilities`
- `supported_nodes`
- `interaction_pattern`
- `cost_profile`

Node registry v0 chua:

- `node`
- `node_type`
- `locality`
- `supported_provider_types`
- `status`

Route preparation se doc registry de tao:

- `required_capabilities`
- `candidate_providers`
- `candidate_nodes`
- `routing_policy_refs`
- `cost_policy_refs`

Route selection v0 chi dung luat don gian, local-first, khong co dynamic arbitration.
