# Release Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Role:** Governance rules for release freeze, tag, release branch closure, and main integration

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

### RG-01 — A release must have a freeze point
Every version/release milestone must have a clearly identified freeze commit.

### RG-02 — Freeze uses tags, not branch memory
Release identity must be frozen by tag.

### RG-03 — Merge into `main` requires release readiness checks
No release branch may be merged into `main` casually.

### RG-04 — `main` must remain the latest integrated clean state
Release integration must strengthen `main`, not destabilize it.

### RG-05 — Release branches should be frozen after completion
Once merged and tagged, release branches should not continue as active dev branches.

## 4. Validation gates

Before release integration:
- branch clean
- tests pass
- docs/release notes sufficiently aligned
- merge summary reviewed
- user approval for merge/tag/push

## 5. Recommended placement

```text
docs/governance/release/
```

## 6. Final note

Release governance exists to stop “almost done” from pretending to be “released safely”.
