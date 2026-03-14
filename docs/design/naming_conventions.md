# Quy ước đặt tên

ATP phải giữ đúng vocabulary đã được khóa trong decision artifact và governance document.

## Vocabulary cốt lõi

Các thuật ngữ cốt lõi cần giữ ổn định gồm:

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

## Các stage của orchestration

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

## Quy tắc đặt tên

- Python modules và functions dùng `snake_case`
- Schema fields dùng `snake_case`
- Constant states dùng `UPPER_CASE`
- Tên `handoff type` phải giữ đúng vocabulary chuẩn: `inline_context`, `evidence_bundle`, `exchange_bundle`, `manifest_reference`

## Không tự ý thêm top-level vocabulary mới

Không tự ý đưa thêm top-level vocabulary chưa được chốt như:
- `planner`
- `dispatcher`
- `agent_router`

trừ khi có decision hoặc governance artifact mới chấp thuận.
