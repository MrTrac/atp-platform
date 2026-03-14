# Coding Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

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

- Every coding phase must have a defined scope
- Done requires testing/validation
- Branch-aware coding is mandatory
- AI must not silently expand scope
- Code and docs should stay aligned when behavior changes materially

## 4. Validation gates

Minimum coding gate:
- correct branch check
- scope check
- compile/syntax check where relevant
- test/check pass where relevant
- diff review before commit

## 5. Completion rule

A coding phase is not complete until it has passed appropriate testing or validation for that phase.

## 6. Final note

Coding should be phase-governed, branch-governed, and validation-gated.
