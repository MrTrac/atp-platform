# ATP v0.5 Execution Plan

> **Trạng thái tài liệu này:** Active — milestone đang ở giai đoạn `consolidated baseline ready to continue toward freeze/integration`.
> Tài liệu này mô tả execution plan dựa trên evidence đã có từ branch `v0.5-planning`,
> integration review, và consolidation decision.

---

## Mục đích

Định nghĩa operating plan cho việc thực thi `v0.5`.

## Phạm vi thực thi

**Đã xác nhận:**

- Branch: `v0.5-planning` (active)
- Scope: Slices A-D, không mở Slice E trừ khi có foundational gap mới được chứng minh
- Không mở rộng sang provider routing, portfolio orchestration, approval UI, recovery execution, distributed control, v1/v2 horizons

## Workstreams / Slices

**Đã xác nhận từ `ATP_v0_5_Integration_Review.md` và `ATP_v0_5_Consolidation_Decision.md`:**

| Slice | Nội dung | Trạng thái hiện tại |
|---|---|---|
| Slice A | Request-to-product resolution contract: chốt product target, capability target, rationale, traceability ở mức `request_to_product_only` | **Đã triển khai và review** |
| Slice B | Resolution-to-handoff intent contract: chốt bounded handoff intent từ Slice A ở mức `resolution_to_handoff_only` | **Đã triển khai và review** |
| Slice C | Product execution preparation contract: chốt execution preparation package từ Slice A-B ở mức `product_execution_preparation_only` | **Đã triển khai và review** |
| Slice D | Product execution result contract: chốt bounded execution result record từ Slice C ở mức `product_execution_result_only` | **Đã triển khai và review** |

Chain thực thi đã xác nhận:

```
request
  → request-to-product resolution (Slice A)
  → resolution-to-handoff intent (Slice B)
  → product execution preparation (Slice C)
  → product execution result (Slice D)
```

## Deliverables

**Đã xác nhận từ integration review:**

### Runtime artifacts

- `request-to-product-resolution-contract.json` trong `manifests/`
- `resolution-to-handoff-intent-contract.json` trong `manifests/`
- `product-execution-preparation-contract.json` trong `manifests/`
- `product-execution-result-contract.json` trong `manifests/`

### Linkage / traceability

- Slice B ref tới Slice A
- Slice C ref tới Slice A và Slice B
- Slice D ref tới Slice A, Slice B, và Slice C

### Documentation

- `docs/roadmap/versions/ATP_v0_5_Roadmap.md` — đã được correct trong integration review pass
- `docs/archive/reports/ATP_v0_5_Integration_Review.md`
- `docs/archive/reports/ATP_v0_5_Consolidation_Decision.md`

### Runtime write locations

**Đã xác nhận — không có runtime state ghi vào ATP source repo:**

- `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- `SOURCE_DEV/workspace/exchange/current-task/<run-id>/` khi exchange boundary yêu cầu

## Test / validation strategy

**Đã xác nhận từ `ATP_v0_5_Integration_Review.md`:**

Current tests chứng minh được:

- Contract shape của từng slice
- Contract separation và anti-scope-creep
- Workspace artifact existence
- Linkage/traceability giữa Slice A-D
- End-to-end coherence của chain ở `happy`, `reject`, và `continue_pending`

Không có test nào ngụ ý scope rộng hơn actual baseline.

Có thể thêm test content-level sâu hơn cho traceability về sau nếu cần — hiện không phải blocker.

## Dependencies / risks

**Đã xác nhận / suy luận hợp lý:**

- Phụ thuộc vào `v0.4.0` frozen baseline (persistence, recovery contract, pointer, inspect đã đúng)
- Rủi ro chính: blur ranh giới giữa resolution, handoff intent, preparation, và result — đã kiểm soát qua semantics rõ từng Slice
- Rủi ro scope creep sang Slice E / provider arbitration / portfolio — đã defer rõ trong consolidation decision
- Docs drift: đã được phát hiện và sửa trong integration review pass (roadmap doc)

## Exit criteria

**Đã xác nhận từ `ATP_v0_5_Roadmap.md` và consolidation decision:**

- Cả 4 slice (A-D) tạo thành request-to-product execution chain nhất quán
- Không có scope creep sang provider routing, portfolio orchestration, approval UI, recovery execution, distributed control
- Integration review pass: không có blocker kiến trúc, boundary, hay test
- Consolidation decision: `consolidated baseline ready to continue toward freeze/integration`
- **Bước tiếp theo:** freeze-readiness pass, rồi integration/freeze decision

**Trạng thái hiện tại:** Slices A-D đã đạt consolidation. Chưa freeze.

---

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/roadmap/milestones/v0_5/ATP_v0_5_Proposal.md`
- `docs/roadmap/versions/ATP_v0_5_Roadmap.md`
- `docs/archive/reports/ATP_v0_5_Integration_Review.md`
- `docs/archive/reports/ATP_v0_5_Consolidation_Decision.md`
- `docs/roadmap/milestones/v0_5/ATP_v0_5_Freeze_Decision_Record.md`
- `docs/roadmap/milestones/v0_4/` — milestone predecessor
