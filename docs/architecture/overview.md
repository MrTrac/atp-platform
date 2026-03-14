# Tổng quan ATP

- **Mục đích:** Tổng quan ATP, baseline M8, đặc tính kiến trúc đã khóa.
- **Phạm vi:** ATP MVP v0; flow 14 bước; năng lực hiện có; phần deferred.
- **Trạng thái:** Active.
- **Tài liệu liên quan:** `layered_architecture.md`, `orchestration_flow.md`, `design/artifact_model.md`.

ATP là một `platform repository` điều phối workflow theo mô hình control-plane, provider-agnostic, adapter-first, artifact-centric, và human-gated.

## Trạng thái baseline hiện tại

ATP MVP v0 đã hoàn tất baseline repo-local đến M8. Flow chuẩn hiện hành gồm 14 bước:

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

## Đặc tính kiến trúc đã khóa

ATP hiện giữ nguyên các nguyên tắc đã được freeze:

- platform-first
- provider-agnostic
- adapter-first
- artifact-centric
- human-gated
- local-first but node-portable
- single source of contextual truth

## Năng lực đã có trong ATP v0

Baseline hiện tại đã hỗ trợ:

- request intake và normalization
- input classification
- product resolution tối thiểu cho ATP và TDF
- context packaging
- deterministic routing chuẩn hóa theo capability và provider
- local execution qua adapter được hỗ trợ
- artifact capture và authoritative selection ở mức summary
- validation, review, approval gate, finalization, và handoff summary
- quyết định `close-run` hoặc `continue-run`

## Phần còn deferred sau ATP v0

ATP v0 chưa mở rộng sang:

- production workspace materialization đầy đủ trong `SOURCE_DEV/workspace`
- approval UI
- remote orchestration plane hoàn chỉnh
- advanced scheduling
- multi-provider arbitration engine
- persistence layer ở mức production

## Quan hệ với snapshot và governance

Tài liệu này là overview active. Authority chi tiết cho baseline và hardening snapshot nằm dưới `docs/architecture/`, còn governance authoritative nằm dưới `docs/governance/`.
