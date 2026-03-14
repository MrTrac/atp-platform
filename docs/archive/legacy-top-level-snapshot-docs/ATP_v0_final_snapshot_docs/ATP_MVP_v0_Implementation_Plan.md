# ATP MVP v0 Implementation Plan

- **Title:** ATP MVP v0 Implementation Plan
- **Version:** v0.2
- **Status:** Implemented Baseline
- **Date:** 2026-03-14
- **Scope:** ATP MVP v0
- **Source Baseline:** `ATP_MVP_v0_Freeze_Decision_Record.md`

## Planning principle

ATP MVP v0 was implemented as a shape-correct MVP with correct repository boundary, control-plane semantics, provider/adapter/registry shape, artifact lifecycle semantics, and enough implementation to execute one full end-to-end run in repo-local MVP form.

## Milestone status summary

- M0 — Done
- M1 — Done
- M2 — Done
- M3 — Done
- M4 — Done
- M5 — Done
- M6 — Done
- M7 — Done
- M8 — Done

## Delivered baseline behavior

ATP MVP v0 can now:

1. load a request
2. normalize it
3. classify it
4. resolve ATP or TDF
5. build task manifest
6. build product context
7. select evidence
8. build evidence bundle summary
9. prepare/select a route
10. execute the supported local non-LLM path
11. normalize execution output
12. capture artifact-like outputs
13. validate and review the result
14. pass through a minimal approval gate
15. build handoff outputs
16. finalize the run
17. decide close-run or continue-run
18. present a useful CLI summary
19. pass happy-path and reject-path tests

## Out of scope for MVP v0

- production workspace materialization under `SOURCE_DEV/workspace`
- human approval UI
- advanced escalation engine
- advanced scheduling / background orchestration
- remote orchestration plane
- multi-provider arbitration engine
- production-grade persistence layer
