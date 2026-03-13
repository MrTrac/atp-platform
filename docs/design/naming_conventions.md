# Naming Conventions

ATP v0 giu dung vocabulary da khoa trong Freeze Decision Record. M1-M2 chi duoc dung cac ten sau cho control-plane va schema fields:

- `product`
- `provider`
- `adapter`
- `capability`
- `execution_intent`
- `artifact`
- `artifact_freshness`
- `authoritative`
- `evidence_bundle`
- `manifest_reference`
- `approval_gate`

Orchestration stages giu ten on dinh:

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

Quy uoc dat ten cho M1-M2:

- Python module va function dung `snake_case`.
- Schema field dung `snake_case`.
- Constant state dung `UPPER_CASE`.
- Handoff type name trong docs giu dang vocabulary: `inline_context`, `evidence_bundle`, `exchange_bundle`, `manifest_reference`.

Khong dua vao top-level naming moi nhu `planner`, `dispatcher`, `agent_router`, hoac vocabulary khac chua co decision.
