# Orchestration Flow

Flow ATP v0 van giu day du theo architecture da khoa, nhung implementation hien tai chi bao phu den M4.

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

- Implemented shallow: 1, 2, 3, 4, 5
- Stub only: 6-14

Context Packaging trong M4 thuc hien:

- build task manifest
- build product context
- select evidence artifacts
- materialize evidence bundle trong memory

ATP chua thuc thi routing, execution, hay side effect runtime nao trong repo source nay.
