# ATP v0.1 Hardening Implementation Plan

- **Title:** ATP v0.1 Hardening Implementation Plan
- **Version:** v0.1 R2
- **Status:** Draft-Baseline
- **Date:** 2026-03-14
- **Scope:** ATP v0.1 Hardening
- **Positioning:** Hardening Track
- **Parent Baseline:** ATP MVP v0 implemented baseline
- **Parent baseline status:** Implemented Baseline

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

## 4. Verification gates

### After Phase A
- architecture/design/operator docs use aligned wording
- schema/model key naming conflicts are reduced or eliminated
- no new architecture concepts were introduced

### After Phase B
- `./cli/atp validate ...` summary fields are consistent
- `./cli/atp run ...` final summary fields are consistent
- `inspect` is materially more useful than baseline placeholder behavior
- error messages are shorter and clearer

### After Phase C
- `make test` passes
- edge-path and reject-path coverage is stronger than ATP v0 baseline
- fixtures are easier to distinguish by role and intent

### After Phase D
- artifact summary / final summary fields are stable
- happy-path and reject-path summaries do not drift unnecessarily
- ATP v0.1 remains inside hardening scope

## 5. Deliverables

ATP v0.1 should produce:

- updated docs bundle
- refined CLI behavior
- better inspect usability
- cleaner fixtures
- stronger tests
- more stable artifact summary / final summary outputs

## 6. Deferred items

The following remain deferred beyond ATP v0.1:

- workspace-backed production persistence
- approval UI
- advanced escalation workflows
- remote orchestration plane
- advanced scheduling
- multi-provider arbitration

## 7. Exit criteria

ATP v0.1 is complete when:

- implemented baseline docs are coherent and current
- CLI summaries are aligned
- inspect is practically useful within MVP limits
- test confidence is stronger than ATP v0 baseline
- output summaries are more stable
- no architectural expansion occurred
