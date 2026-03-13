# Handoff Model

ATP v0 giu 4 handoff model co dinh:

- `inline_context`
- `evidence_bundle`
- `exchange_bundle`
- `manifest_reference`

Trong M4, `evidence_bundle` va `manifest_reference` bat dau co vai tro thuc te cho Context Packaging.

Evidence Bundle v0 chua:

- `bundle_id`
- `request_id`
- `product`
- `selected_artifacts`
- `authoritative_refs`
- `manifest_reference`
- `notes`

Manifest Reference v0 duoc dung de tro tu evidence bundle ve task manifest hien tai.

Deferred cho M5+:

- exchange bundle packaging
- remote transport
- cross-node synchronization
- execution-facing handoff materialization
