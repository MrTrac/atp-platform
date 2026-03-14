# Release Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Purpose

This bundle governs how a project moves from working branch to released and frozen state.

## 2. Scope

Applies to:
- release branch completion
- merge into `main`
- version tagging
- changelog/release note readiness
- post-release state

## 3. Rules

- A release must have a freeze point
- Freeze uses tags, not branch memory
- Merge into `main` requires release readiness checks
- `main` must remain the latest integrated clean state
- Release branches should be frozen after completion

## 4. Validation gates

Before release integration:
- branch clean
- tests pass
- docs/release notes sufficiently aligned
- merge summary reviewed
- user approval for merge/tag/push

## 5. Final note

Release governance exists to stop “almost done” from pretending to be “released safely”.
