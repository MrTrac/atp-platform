# Documentation Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

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

- Every important document set must have one authoritative location
- Do not keep multiple authoritative copies in parallel
- Documents must be named by role, not casually
- Every deliverable document must be reviewed before export
- Exported documents intended for repo adoption must have a defined target path
- Snapshot bundles should include a `README.md` index

## 4. Validation gates

Before promoting a documentation bundle:
- naming review
- path/authority review
- consistency review
- duplicate-authority review
- scope review

## 5. Review rule

Minimum document review rule:
- self-review pass 1 = logic / scope / content
- self-review pass 2 = wording / consistency / usability

## 6. Final note

Documentation should not be operated by memory. It should be operated by document governance.
