# ATP v0.1 Hardening Backlog

- **Title:** ATP v0.1 Hardening Backlog
- **Version:** v0.1 R2
- **Status:** Draft-Baseline
- **Date:** 2026-03-14

## Priority map

- **P0:** H-01, H-04
- **P1:** H-02, H-03, H-05
- **P2:** H-06, H-07
- **P3:** H-08

## H-01 — Docs baseline cleanup
**Priority:** P0  
**Objective:** make the documentation set match the implemented ATP v0 baseline exactly.

**Scope:**
- `README.md`
- Freeze Decision Record
- Implementation Plan
- runbook docs
- local bootstrap docs

**Done criteria:**
- no wording mismatch between docs and implemented ATP v0 baseline

---

## H-02 — CLI summary normalization
**Priority:** P1  
**Objective:** make `validate`, `run`, and `inspect` summaries more consistent.

**Scope:**
- normalize summary keys and ordering
- normalize wording for status fields
- reduce noisy or inconsistent formatting

**Done criteria:**
- operator-facing CLI outputs are easier to compare across flows

---

## H-03 — Inspect hardening
**Priority:** P1  
**Objective:** make `inspect` more useful within current MVP limits.

**Scope:**
- clarify what inspect can read
- improve practical summary behavior
- document what remains deferred

**Done criteria:**
- inspect is no longer merely placeholder-grade

---

## H-04 — Schema / model consistency pass
**Priority:** P0  
**Objective:** improve naming consistency across docs, schemas, core modules, and CLI summaries.

**Scope:**
- request/run/artifact/handoff naming
- review/approval/finalization naming
- artifact-state wording

**Done criteria:**
- one concept maps to one primary term

---

## H-05 — Error handling & exit behavior
**Priority:** P1  
**Objective:** make CLI errors shorter, clearer, and more consistent.

**Scope:**
- request parse failures
- product resolution failures
- route selection failures
- unsupported execution cases
- validation/review edge cases

**Done criteria:**
- error paths are understandable and predictable

---

## H-06 — Fixture cleanup
**Priority:** P2  
**Objective:** make fixtures easier to understand and maintain.

**Scope:**
- sample request cleanup
- ATP vs TDF request clarity
- happy path vs reject path fixtures
- redundant fixture reduction

**Done criteria:**
- fixture names and roles are immediately understandable

---

## H-07 — Test coverage hardening
**Priority:** P2  
**Objective:** strengthen ATP v0 baseline confidence.

**Scope:**
- edge cases
- reject cases
- unsupported route/provider cases
- approval needs-attention path
- inspect/summary behavior where appropriate

**Done criteria:**
- regression risk is lower and edge coverage is better

---

## H-08 — Artifact / report polish
**Priority:** P3  
**Objective:** make artifact-like summaries and final outputs more stable.

**Scope:**
- artifact summary shape
- final summary key consistency
- authoritative / selected / filtered stability

**Done criteria:**
- output summaries do not drift unnecessarily across flows
