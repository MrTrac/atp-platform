# Architecture Decision Records — ATP

> **Schema:** AI_OS Doctrine §3.9.1 + DP#78 + DP#123 (Phase 2 backfill 2026-04-28)
> **Template:** `~/AI_OS/10_TEMPLATES/ADR_TEMPLATE.md`

## Index

| # | Title | Status | Date | Tier |
|---|---|---|---|---|
| [0001](./ADR-0001-bounded-execution-model.md) | Bounded execution model (3 axioms + zero-deps Python) | Accepted | 2026-03-23 | 3 |
| [0002](./ADR-0002-triple-agent-runtime.md) | Triple agent runtime (Claude/Codex/Cursor + 3 isolation modes) | Accepted | 2026-04-19 | 3 |
| [0003](./ADR-0003-aokp-context-enrichment.md) | AOKP context enrichment (per-intent injection) | Accepted | 2026-04-15 | 3 |
| [0004](./ADR-0004-runs-migration-aios-state.md) | Runs migration to `~/.aios/atp/runs/` (DP#50) | Accepted | 2026-04-27 | 2 |

## Conventions
- Filename: `ADR-NNNN-<kebab-case-title>.md`
- Numbering: monotonic increment, never reuse
- Status flow: Proposed → Accepted → (Deprecated | Superseded by ADR-XXX)

## Future ADRs
- ADR-0005: Evaluator pattern adoption (DP#9 RESOLVED — 3 evaluator runners Phase 2)
- ADR-0006: 90-day prune logic for runs/ (DP#50 follow-up)
- ADR-0007: TDF integration (ATP_TDF_v1 contract added 2026-04-25)
