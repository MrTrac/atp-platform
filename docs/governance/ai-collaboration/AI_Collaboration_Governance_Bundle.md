# AI Collaboration Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Purpose

This bundle governs how AI assistants participate in project work.

## 2. Scope

Applies to:
- ChatGPT
- Codex
- Claude
- IDE agents
- future AI tooling

## 3. Rules

- Every major branch should have its own AI workspace/chat
- AI must always verify repo and branch context
- Before starting any new slice, AI must create the slice branch, switch into it, verify repo/branch/worktree again, and only then begin the first docs or implementation pass
- AI must not write baseline docs or implementation for a new slice while still standing on the previous branch
- If new-slice work is discovered on the wrong branch, AI must stop and repair branch lineage before continuing
- AI must respect approval boundaries
- AI should maximize automation, not bypass governance
- AI outputs must be validated before being called complete

## 4. Completion rule

Code phases need tests/checks. Documents need at least two self-review passes before export.

## 5. Approval-sensitive actions

Always approval-sensitive:
- merge into `main`
- push `main`
- release tag creation
- release tag push
- destructive history operations

## 6. Final note

AI collaboration should be governance-led, not prompt-chaos-led.
