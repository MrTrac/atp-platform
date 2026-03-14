# ATP v0.1 Hardening Implementation Plan

- **Title:** ATP v0.1 Hardening Implementation Plan
- **Version:** v0.1
- **Status:** Draft-Baseline
- **Date:** 2026-03-14
- **Scope:** ATP v0.1 Hardening
- **Positioning:** Hardening Track
- **Parent Baseline:** ATP MVP v0 implemented baseline

## 1. Planning principle

ATP v0.1 is a **hardening phase**.

The implementation principle is:

- hardening, not expansion
- consistency, not redesign
- operability, not platform growth
- stability, not feature inflation

## 2. Phase map

### Phase A — Documentation & consistency
Focus:
- docs cleanup
- schema/model naming consistency
- wording alignment across architecture/design/operator docs

Target outcomes:
- ATP docs reflect the implemented baseline precisely
- naming is stable across docs, schemas, and summaries

### Phase B — CLI & inspect hardening
Focus:
- normalize CLI summaries
- improve inspect usefulness
- clarify error and exit behavior

Target outcomes:
- `validate`, `run`, and `inspect` present more consistent operator-facing behavior

### Phase C — Fixtures & tests
Focus:
- clean and simplify fixtures
- increase edge-case and reject-path coverage
- reduce ambiguity in sample requests

Target outcomes:
- tests better protect ATP v0 behavior from regression

### Phase D — Artifact/report polish
Focus:
- stabilize artifact-like summaries
- make final summary keys more consistent
- reduce output shape drift between flows

Target outcomes:
- summary outputs are easier to interpret and compare

## 3. Milestones

### v0.1-M1
- docs cleaned
- naming consistency improved

### v0.1-M2
- CLI summaries normalized
- inspect improved
- error behavior clarified

### v0.1-M3
- fixtures cleaned
- tests expanded for edge and reject cases

### v0.1-M4
- artifact/report polish completed
- ATP v0.1 release candidate ready

## 4. Deliverables

ATP v0.1 should produce:

- updated docs bundle
- refined CLI behavior
- better inspect usability
- cleaner fixtures
- stronger tests
- more stable artifact/report summaries

## 5. Deferred items

The following remain deferred beyond ATP v0.1:

- workspace-backed production persistence
- approval UI
- advanced escalation workflows
- remote orchestration plane
- advanced scheduling
- multi-provider arbitration

## 6. Exit criteria

ATP v0.1 is complete when:

- implemented baseline docs are coherent and current
- CLI summaries are aligned
- inspect is practically useful within MVP limits
- test confidence is stronger than ATP v0 baseline
- output summaries are more stable
- no architectural expansion occurred
