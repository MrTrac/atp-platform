# Coding Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Role:** Governance rules for implementation phases, coding scope, testing-before-done, and branch-aware delivery

## 1. Purpose

This bundle governs implementation behavior for humans and AI assistants.

## 2. Scope

Applies to:
- feature implementation
- phase work
- refactors
- code generation
- test generation
- code review preparation

## 3. Rules

### CG-01 — Every coding phase must have a defined scope
No coding phase should start without scope boundaries.

### CG-02 — Done requires testing/validation
A coding phase is not complete until it has passed appropriate testing or validation for that phase.

### CG-03 — Branch-aware coding is mandatory
Coding must happen on the correct branch for the correct phase/version/context.

### CG-04 — AI must not silently expand scope
If the current phase is hardening, AI must not turn it into feature expansion.

### CG-05 — Code and docs should stay aligned
If behavior changes materially, related docs must be reviewed or updated.

## 4. Validation gates

Minimum coding gate:
- correct branch check
- scope check
- compile/syntax check where relevant
- test/check pass where relevant
- diff review before commit

## 5. Recommended placement

```text
docs/governance/coding/
```

## 6. Final note

Coding should be phase-governed, branch-governed, and validation-gated.
