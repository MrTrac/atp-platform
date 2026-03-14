# ATP v0.5 Proposal

> **Trạng thái tài liệu này:** Active — milestone đang ở giai đoạn `consolidated baseline ready to continue toward freeze/integration`.
> Tài liệu này được tạo như một phần của documentation continuity backfill theo governance rule,
> dựa trên evidence hiện có: `ATP_v0_5_Roadmap.md`, `ATP_v0_5_Integration_Review.md`,
> `ATP_v0_5_Consolidation_Decision.md`, và runtime contracts trên branch `v0.5-planning`.

---

## Mục đích

Xác lập milestone initiation document cho ATP `v0.5`.

## Bối cảnh

**Đã xác nhận:**

- `v0.4.0` đã freeze với baseline: current-task persistence, recovery contract, active/supersede pointer traceability, read-only inspect
- ATP v0 major family cần một milestone cuối để hoàn tất chuỗi foundational request-to-product execution
- Sau `v0.4.0`, `v0.5-planning` là branch làm việc active

**Đã xác nhận từ `ATP_v0_5_Roadmap.md`:**

ATP `v0.5` được định vị là guided step để hoàn tất v0 major family — không phải v1, không phải milestone mở rộng portfolio.

Khoảng trống cần lấp:

- ATP thiếu chain contract rõ ràng từ request intent → resolution → handoff intent → execution preparation → execution result
- Không có explicit contracts file-based nối các bước này
- Traceability từ request tới bounded execution result chưa đủ coherent

## Mục tiêu

**Đã xác nhận từ `ATP_v0_5_Roadmap.md` và `ATP_v0_5_Integration_Review.md`:**

- Harden foundational request-to-product execution chain với explicit file-based contracts
- Thiết lập 4 contracts tạo thành chain khép kín:
  - Slice A: request-to-product resolution contract
  - Slice B: resolution-to-handoff intent contract
  - Slice C: product execution preparation contract
  - Slice D: product execution result contract
- Đảm bảo traceability từ request tới bounded execution result mà không mờ boundary với routing/provider selection
- Hoàn tất v0 major family đủ để cân nhắc chuyển sang v1 horizon

## In-scope

**Đã xác nhận từ `ATP_v0_5_Integration_Review.md` và `ATP_v0_5_Consolidation_Decision.md`:**

- Slice A: request-to-product resolution contract
  - Chốt product target, capability target, rationale, và traceability ở mức `request_to_product_only`
- Slice B: resolution-to-handoff intent contract
  - Chốt bounded handoff intent từ Slice A ở mức `resolution_to_handoff_only`
- Slice C: product execution preparation contract
  - Chốt execution preparation package từ Slice A-B ở mức `product_execution_preparation_only`
- Slice D: product execution result contract
  - Chốt bounded execution result record từ Slice C ở mức `product_execution_result_only`

Chain thực thi: `request → resolution → handoff intent → execution preparation → execution result`

Artifacts materialize dưới `manifests/`:
- `request-to-product-resolution-contract.json`
- `resolution-to-handoff-intent-contract.json`
- `product-execution-preparation-contract.json`
- `product-execution-result-contract.json`

## Out-of-scope

**Đã xác nhận từ `ATP_v0_5_Consolidation_Decision.md`:**

- Bất kỳ Slice E nào không chứng minh được foundational gap thật sự
- Provider arbitration engine
- Cost-aware routing expansion
- Topology-aware orchestration
- Approval UI
- Recovery execution
- Distributed control
- Generalized orchestration hoặc portfolio subsystem
- v1 / v2 horizon features

## Giả định và ràng buộc

**Đã xác nhận:**

- Kế thừa `v0.4.0` frozen baseline làm nền
- Slice A không làm classification hay routing
- Slice B không làm provider selection hay route arbitration
- Slice C không làm execution result hay orchestration engine
- Slice D không làm approval, recovery, hay distributed control
- Runtime writes tiếp tục đi vào `SOURCE_DEV/workspace/`, không vào ATP source repo

## Tiêu chí để mở milestone này

**Đã xác nhận — từ `ATP_v0_4_0_Freeze_Closeout.md`:**

- `v0.4.0` đã freeze thành công và integrate vào `main`
- Branch `v0.5-planning` đã là branch làm việc active sau freeze `v0.4.0`

## Quan hệ với mốc trước / mốc sau

- **Predecessor:** `v0.4` — operational runtime hardening; tag `v0.4.0`; lineage status: `documented`
- **Successor intent:** `v1` — operational maturity horizon (chỉ mở khi v0 đạt coherent maturity boundary)
  Lineage status: `provisional` — v1 chưa có formal planning baseline

---

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/roadmap/versions/ATP_v0_5_Roadmap.md` — version roadmap authoritative
- `docs/archive/reports/ATP_v0_5_Integration_Review.md` — integration review (active)
- `docs/archive/reports/ATP_v0_5_Consolidation_Decision.md` — consolidation decision (active)
- `docs/roadmap/majors/ATP_v0_Major_Roadmap.md` — v0 major family context
- `docs/roadmap/milestones/v0_4/` — milestone predecessor
- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
