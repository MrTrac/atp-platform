# AI Session Bootstrap Template
## Mẫu khởi tạo phiên làm việc cho AI theo governance của dự án

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Purpose:** Dùng để nạp nhanh rule, context, branch, và cách làm việc cho bất kỳ AI nào khi bắt đầu một phiên mới

---

# 1. Cách dùng

Khi mở một AI mới, anh chỉ cần:

1. copy phần template bên dưới
2. điền các chỗ cần thiết theo ngữ cảnh hiện tại
3. paste vào AI đó ở đầu phiên làm việc

Mục tiêu:
- AI hiểu đúng repo
- AI hiểu đúng branch
- AI hiểu đúng task
- AI tuân thủ governance docs
- AI không tự ý làm Git action nguy hiểm
- giảm việc phải nhắc lại nhiều lần

---

# 2. Session bootstrap template

```text
You are joining an active project workflow.

## Project identity
- Project name: <PROJECT_NAME>
- Repo role: <platform | product | utility | other>
- Repo root: <REPO_ROOT>
- Current branch: <BRANCH_NAME>
- Branch type: <main | release | feature | hotfix>
- Merge target: <MERGE_TARGET if relevant>

## Current task
- Current phase/step: <PHASE_OR_STEP>
- Task summary: <SHORT_TASK_SUMMARY>
- Scope boundary: <WHAT_IS_IN_SCOPE>
- Out of scope: <WHAT_IS_OUT_OF_SCOPE>

## Governance documents you must follow
Treat the following as authoritative for this session:
- <DOC_1>
- <DOC_2>
- <DOC_3>
- <DOC_4>

At minimum, follow:
1. branch-aware work discipline
2. validation/testing before calling work complete
3. documentation review before export
4. no dangerous Git actions without explicit approval

## Git and branch rules
- Do not develop casually on `main`
- Do not merge into `main` without explicit approval
- Do not push `main` without explicit approval
- Do not create or push release tags without explicit approval
- Always show branch/status/diff summary before dangerous Git actions
- Always respect the current branch context

## Document rules
- All project documents should be written in clear Vietnamese with proper Unicode accents
- Keep necessary English technical terms in original English where appropriate
- Any document/bundle must be self-reviewed at least 2 passes before final export

## Completion rule
A task/phase is not complete until appropriate validation has been performed:
- code -> compile/test/check
- docs -> scope/consistency/review
- workflow/rules -> logic/operability review

## Working style
- Prefer automation-first, but stop at approval points
- Reduce manual steps for the user as much as safely possible
- If you can directly process available content, do so
- If you cannot access the required content, write a tight prompt for another AI to execute
  The prompt should be delivered in one copy/paste-ready block, tell the user to paste the result back here for review, and keep room for a second review/follow-up prompt if needed

## Required startup checks
Before doing substantive work, verify:
- repo root
- current branch
- working tree status
- whether the current task matches the current branch

Now confirm:
1. your understanding of the project context
2. the branch you are operating on
3. the task you will perform next
4. any approval-sensitive actions you will not take without permission
```

---

# 3. ATP-specific quick example

```text
You are joining an active project workflow.

## Project identity
- Project name: ATP
- Repo role: platform
- Repo root: /Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
- Current branch: release/v0.1-hardening
- Branch type: release
- Merge target: main

## Current task
- Current phase/step: ATP v0.1 hardening phase A
- Task summary: review, refine, and normalize docs and consistency artifacts
- Scope boundary: docs/governance, docs/architecture, naming consistency, documentation normalization
- Out of scope: feature expansion, workspace materialization, approval UI, remote orchestration plane

## Governance documents you must follow
Treat the following as authoritative for this session:
- docs/governance/framework/Contextual_Project_Governance_Framework.md
- docs/governance/git/Git_Safety_Charter.md
- docs/governance/git/Safe_Git_Workflow_Templates.md
- docs/governance/ai-collaboration/AI_Collaboration_Governance_Bundle.md

## Git and branch rules
- Do not merge into `main` without explicit approval
- Do not push `main` without explicit approval
- Always work branch-aware
- Show summary before high-risk Git actions

## Document rules
- Write documents in clear Vietnamese with proper Unicode accents
- Keep necessary English technical terms in original English
- Self-review documents at least 2 passes before final export

## Completion rule
A phase is not complete until appropriate validation has been performed.

Now confirm:
1. your understanding of the ATP context
2. the branch you are operating on
3. the task you will perform next
4. any approval-sensitive actions you will not take without permission
```

---

# 4. Kết luận

Tài liệu này không thay thế governance docs.  
Nó là **mẫu nạp ngữ cảnh nhanh** để bất kỳ AI nào cũng vào đúng rule và đúng branch ngay từ đầu phiên.
