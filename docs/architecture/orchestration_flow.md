# Orchestration Flow

Flow ATP v0 van giu day du theo architecture da khoa, nhung implementation hien tai bao phu den M8.

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

- Implemented shallow: 1-14

M8 thuc hien:

- approval gate summary `approved` / `rejected` / `needs_attention`
- handoff outputs: inline context, evidence bundle, exchange bundle, manifest reference
- finalization summary
- close-run / continue-run decision

ATP van chua co human approval UI, production workspace materialization, hay orchestration plane ngoai repo nay.
