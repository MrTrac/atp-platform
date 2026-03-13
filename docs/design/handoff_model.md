# Handoff Model

ATP v0 giu 4 handoff model co dinh cho cac milestone sau:

- `inline_context`
- `evidence_bundle`
- `exchange_bundle`
- `manifest_reference`

Muc tieu cua M1-M2:

- dong bo vocabulary giua docs, schema, va core code
- khoa shape toi thieu cho interface giua context packaging va execution/human gate
- giu duoc thong tin `authoritative`, `artifact_freshness`, `provider`, `adapter` khi can

M1-M2 chi can dataclass nhe hoac dict-builder. Chua co:

- artifact copy
- exchange packaging
- remote transport
- cross-node synchronization
