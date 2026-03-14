# Orchestration Flow

Flow ATP v0 van giu day du theo architecture da khoa, nhung implementation hien tai chi bao phu den M7.

Flow chuan:

1. Request Intake
2. Normalize
3. Input Classification
4. Product Resolution
5. Context Packaging
6. Routing Preparation
7. Route Selection
8. Execution via Adapter
9. Capture Output
10. Validation / Review
11. Approval Gate
12. Finalization
13. Handoff to Next Step
14. Close Run or Continue

Trang thai implementation hien tai:

- Implemented shallow: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- Stub only: 11-14

M7 thuc hien:

- capture normalized execution output thanh artifact-like structures
- tao validation summary `passed` / `failed` / `incomplete`
- tao review decision `accept` / `reject` / `revise`

ATP chua co approval gate workflow, finalization, hay production artifact materialization.
