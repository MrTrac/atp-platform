# Orchestration Flow

Flow ATP v0 van giu day du theo architecture da khoa, nhung implementation hien tai chi bao phu M1-M2.

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

- Implemented shallow: 1, 2, 3
- Seed state only: early run state updates quanh 1-3
- Stub only: 4-14

CLI `validate` va `run` trong M1-M2 chi thuc hien:

- load request
- normalize request
- rule-based classify
- preview early run state

ATP chua thuc thi execution hoac side effect nao trong repo source nay.
