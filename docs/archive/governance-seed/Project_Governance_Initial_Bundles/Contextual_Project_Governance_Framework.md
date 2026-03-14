# Contextual Project Governance Framework

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Scope:** Cross-project, reusable
- **Role:** Parent governance framework

## 1. Purpose

This framework defines the rule that every important project activity should be governed by explicit templates, not by memory, habit, or ad hoc decisions.

## 2. Core principle

For any project:

- if a process is repeated
- if a process is risky
- if a process involves multiple actors
- if a process requires approvals
- if a process can damage repo, release, docs, architecture, or runtime state

then that process should have a governance template bundle.

## 3. Governance domains

The baseline governance domains are:

- Git Governance
- Documentation Governance
- Coding Governance
- Release Governance
- AI Collaboration Governance

Additional domains may be added later if justified by project scale and risk.

## 4. Authority rule

Once a governance bundle is promoted as authoritative, all project members must follow it until a newer reviewed revision replaces it.

Members include:

- user
- AI assistants
- scripts / wrappers
- CI or automation components
- collaborators

## 5. Placement rule

Governance artifacts should be stored in a stable project path, for example:

```text
docs/governance/
```

Each governance domain should have its own folder.

## 6. Context rule

Governance is contextual, not universal by default.

That means:
- repo role matters
- branch role matters
- release stage matters
- risk level matters
- project type matters

Templates must be adapted to project context, while preserving core safety principles.

## 7. Completion rule

A phase/process/module should not be considered fully governed until:
- a governance template exists for it
- validation/checking expectations are defined
- approval boundaries are defined
- actor responsibilities are defined

## 8. Final note

This framework is the parent “constitution” for all governance bundles in the project.
