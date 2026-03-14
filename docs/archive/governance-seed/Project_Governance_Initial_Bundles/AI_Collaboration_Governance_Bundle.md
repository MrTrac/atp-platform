# AI Collaboration Governance Bundle

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Role:** Governance rules for user + AI + multi-branch + multi-phase collaboration

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

### ACG-01 — Every major branch should have its own AI workspace/chat
Avoid cross-branch context contamination.

### ACG-02 — AI must always verify repo and branch context
Before action, AI must confirm:
- repo root
- current branch
- working tree state

### ACG-03 — AI must respect approval boundaries
AI may automate checks and preparation, but must stop at high-risk approval points.

### ACG-04 — AI should maximize automation, not bypass governance
Automation should reduce manual burden, not remove safety gates.

### ACG-05 — AI outputs must be validated before being called complete
Code phases need tests/checks. Documents need at least two self-review passes before export.

## 4. Approval-sensitive actions
Always approval-sensitive:
- merge into `main`
- push `main`
- release tag creation
- release tag push
- destructive history operations

## 5. Recommended placement

```text
docs/governance/ai-collaboration/
```

## 6. Final note

AI collaboration should be governance-led, not prompt-chaos-led.
