# Orchestration Flow

Flow ATP v0 van giu day du theo architecture da khoa, nhung implementation hien tai chi bao phu den M5.

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

- Implemented shallow: 1, 2, 3, 4, 5, 6, 7
- Stub only: 8-14

Routing trong M5 thuc hien:

- derive required capability
- load provider candidates
- load node candidates
- chon mot route local-first, rule-based
- tao routing result summary

ATP chua thuc thi adapter, command, hay runtime side effect nao trong repo source nay.
