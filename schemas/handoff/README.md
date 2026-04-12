# Handoff Schemas

Defines the shapes of handoff payloads used for inter-phase and inter-system continuity.

| Schema | Purpose |
|---|---|
| `exchange_bundle.schema.yaml` | Full exchange bundle for cross-phase handoff |
| `evidence_bundle.schema.yaml` | Evidence packaging for review/validation |
| `inline_context.schema.yaml` | Inline context data carried within requests |
| `manifest_reference.schema.yaml` | References to task manifests |

- **Version:** 1.0
- **Used by:** `core/handoff/` modules
- **Discriminator:** `handoff_type` enum (`exchange_bundle`, `evidence_bundle`, `inline_context`, `manifest_reference`)
