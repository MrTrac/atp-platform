# Documentation Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Role:** Governance rules for creating, reviewing, promoting, naming, and storing project documentation

## 1. Purpose

This bundle governs all documentation work so that documents are authoritative, reviewable, and stored in the correct place.

## 2. Scope

Applies to:
- architecture docs
- implementation plans
- decision records
- runbooks
- checklists
- governance docs
- exported snapshot docs

## 3. Rules

### DG-01 — Every important document set must have an authority path
A document or document bundle must have one authoritative location.

### DG-02 — Do not keep multiple authoritative copies in parallel
If a revised bundle replaces an older one, promote the new one and supersede the old one clearly.

### DG-03 — Documents must be named by role, not casually
Names should reflect:
- domain
- scope
- version/context
- document role

### DG-04 — Every deliverable document must be reviewed before export
Minimum rule:
- self-review pass 1 = logic/scope/content
- self-review pass 2 = wording/consistency/usability

### DG-05 — Exported documents must match repo intent
If a document is intended for repo adoption, its placement path must be defined.

### DG-06 — Snapshot bundles should include an index
Each document bundle should include a `README.md` index.

## 4. Validation gates

Before promoting a documentation bundle:
- naming review
- path/authority review
- consistency review
- duplicate-authority review
- scope review

## 5. Recommended placement

```text
docs/governance/documentation/
```

## 6. Final note

Documentation should not be operated by memory. It should be operated by document governance.
