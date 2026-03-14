# AGENTS.md

This file is the mandatory governance file for AI agents operating in ATP. These rules are binding unless a human explicitly overrides them for the current task.

## Repository identity

ATP is a platform repository at `SOURCE_DEV/platforms/ATP`.

ATP v0 is a shape-correct MVP. Preserve its frozen boundary discipline, control-plane shape, registry shape, adapter shape, artifact lifecycle, and human-gated flow.

## Binding source-of-truth order

Apply this hierarchy in order:

1. human-approved current task instruction
2. `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
3. ATP v0 implementation plan and architecture docs
4. design, operators, and governance docs
5. existing code and file layout

This order must not be silently inverted.

## Mandatory repository boundaries

- `SOURCE_DEV/` is the logical workspace root
- `SOURCE_DEV/platforms/ATP` is the ATP source repo
- `SOURCE_DEV/products/TDF` is the product repo ATP resolves in v0
- `SOURCE_DEV/workspace` is the runtime zone for runs, artifacts, exchange, and logs

Runtime artifacts, run outputs, exchange bundles, logs, and similar operational output must not live in this repo.

## Documentation and naming rules

- Keep glossary, naming, schema, and artifact terminology aligned with ATP docs
- Do not invent new vocabulary when ATP already has a valid term
- Do not rename files, concepts, modules, or contracts casually
- If a rename is truly necessary, preserve traceability and keep the smallest justified change set

## Architecture and scope rules

- ATP v0 is a shape-correct MVP, not a license for scope drift
- Preserve repo boundary, control-plane shape, registry shape, adapter shape, artifact lifecycle, and human-gated flow
- Do not expand scope outside the frozen ATP v0 architecture unless a clear human-approved decision allows it
- Prefer refinement, normalization, and hardening over premature feature expansion

## Change behavior

- Prefer minimal justified churn
- Avoid speculative restructuring
- Avoid hidden behavior changes
- If a requested change conflicts with the ATP baseline, do not apply it silently; surface the conflict and propose the smallest valid next step

## Archive and artifact discipline

- `archive/` is for historical traceability, not active authority
- Frozen snapshot packs must remain frozen
- Generated bundles, temporary review outputs, and ad hoc working artifacts should not remain at repo root unless explicitly intended

## When uncertain

- Do not guess architecture
- Do not expand scope implicitly
- Do not invent new authority paths
- Do not create new modules or contracts without basis
- Prefer documenting the gap, conflict, or required decision

## Working principle

Preserve boundaries strictly. Follow the source of truth in order. Make the smallest justified change. Keep ATP human-gated.
