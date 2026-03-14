# Tổng quan ATP

- **Mục đích:** Tổng quan ATP, baseline M8, đặc tính kiến trúc đã khóa.
- **Phạm vi:** ATP MVP v0; flow 14 bước; năng lực hiện có; phần deferred.
- **Trạng thái:** Active.
- **Tài liệu liên quan:** `layered_architecture.md`, `orchestration_flow.md`, `design/artifact_model.md`.

ATP là một `platform repository` điều phối workflow theo mô hình control-plane, provider-agnostic, adapter-first, artifact-centric, và human-gated.

ATP không được hiểu như một closed snapshot architecture và cũng không được hiểu như một ad hoc open architecture.

ATP được duy trì như:

- một stable core
- với modular boundaries
- explicit extension seams
- composable capabilities
- và controlled evolutionary governance

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
- architecture-first but market-aware
- provider-agnostic
- adapter-first
- artifact-centric
- human-gated
- local-first but node-portable
- single source of contextual truth

Điều này có nghĩa:

- ATP không evolve bằng ad hoc expansion
- modularization là cần thiết nhưng chưa đủ để được coi là “open”
- openness của ATP phải là contract-driven, composable, và governance-controlled
- ATP có thể hấp thụ better modern patterns từ market, nhưng chỉ qua controlled review, planning, verification, consolidation, freeze, close-out, và roadmap inheritance

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

- production-grade runtime materialization đầy đủ trong `SOURCE_DEV/workspace` vượt quá baseline v0.2 hiện tại
- production-grade runtime materialization đầy đủ trong `SOURCE_DEV/workspace` vượt quá baseline v0.4 hiện tại
- approval UI
- remote orchestration plane hoàn chỉnh
- advanced scheduling
- multi-provider arbitration engine
- persistence layer ở mức production

## Trạng thái runtime materialization v0.2-v0.4

ATP v0.2 đã thiết lập baseline runtime materialization tối thiểu, bám đúng boundary `SOURCE_DEV/workspace`, gồm:

- run tree materialization dưới `atp-runs/<run-id>/`
- handoff materialization tối thiểu trong `handoff/`
- authoritative projection tối thiểu dưới `atp-artifacts/<artifact-id>/`
- retention / cleanup semantics tối thiểu ở mức explicit, không có automatic deletion

ATP v0.3 đã nối tiếp baseline đó bằng:

- exchange-boundary decision model
- minimal exchange materialization dưới `exchange/current-task/<run-id>/` khi boundary yêu cầu
- continue-pending operational continuity state
- minimal file-based reference/index support cho exchange, continuation, và authoritative refs

ATP v0.4 đã nối tiếp baseline đó bằng:

- minimal current-task persistence contract
- minimal continue-pending recovery contract
- active/supersede pointer traceability tối thiểu
- read-only inspect surface hẹp cho current-task state và traceability

Baseline hiện tại nhằm làm rõ runtime model, operational traceability, và recovery-entry clarity ở mức tối thiểu; không phải triển khai full runtime subsystem, production persistence, hay lifecycle automation rộng.

## Doctrine phát triển kiến trúc

ATP được xây trên một architecture baseline đã được tổng hợp và review cẩn thận, không phải trên một snapshot đóng kín tuyệt đối và cũng không phải trên một mô hình mở tùy hứng.

Luật tiến hóa của ATP là:

- giữ stable core của control-plane, repo boundary, artifact lifecycle discipline, và human-gated flow
- mở extension seams tại các ranh giới rõ như adapters, runtime materialization zones, handoff/exchange contracts, current-task contracts, và inspect surfaces
- cho phép composable capability growth theo từng versioned slice
- dùng governance-backed architectural fitness checks để chặn scope drift trước khi integration/freeze

## Version inheritance và continuity

Mỗi version mới của ATP phải kế thừa từ:

- previous frozen version
- consolidation baseline của version trước đó
- freeze close-out của version trước đó nếu đã có
- roadmap continuity đã được ghi rõ

Điều này cũng kéo theo:

- implementation không nên đi trước planning baseline acceptance
- freeze không nên diễn ra nếu chưa có consolidation decision
- sau mỗi version đã freeze, formal freeze close-out là bắt buộc
- roadmap continuity là một phần của ATP governance, không phải optional writing

## Quan hệ với roadmap

Roadmap của ATP không phải danh sách ý tưởng tự do. Roadmap là lớp điều phối evolution theo ba tầng:

- product roadmap
- major roadmap
- version roadmap

Minor versions mở rộng capability horizon của current major family. Major transitions chỉ hợp lệ khi current major family đã đạt một coherent maturity boundary đủ rõ để chuyển sang capability horizon mới.

## Quan hệ với snapshot và governance

Tài liệu này là overview active. Authority chi tiết cho baseline và hardening snapshot nằm dưới `docs/architecture/`, còn governance authoritative nằm dưới `docs/governance/`.
