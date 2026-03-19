# Kho lưu tài liệu lịch sử

**Mục đích:** Lưu tài liệu lịch sử, seed bundle, và bản sao cũ để traceability.

**Phạm vi:** Governance seed, snapshot bundle legacy, báo cáo rà soát, planning, consolidation, và freeze close-out đã lưu.

**Trạng thái:** Archived.

---

## ⚠️ Nguồn sự thật

**`docs/archive/` KHÔNG phải nguồn sự thật chính.** Tài liệu trong đây không được dùng làm authority hiện hành. Luôn ưu tiên tài liệu active dưới `architecture/`, `design/`, `operators/`, `governance/`.

## Quy tắc sử dụng

- Không dùng tài liệu trong `archive/` làm nguồn authority hiện hành nếu đã có bản mới dưới `architecture/` hoặc `governance/`
- Chỉ chuyển tài liệu vào `archive/` khi authority path mới đã rõ ràng
- Giữ cấu trúc archive đủ rõ để lần theo lịch sử mà không tạo nhầm lẫn với tài liệu active

## Các nhóm archive hiện có

- `governance-seed/` — governance bundle giai đoạn seed hoặc placement proposal ban đầu
- `legacy-top-level-snapshot-docs/` — snapshot bundle từng nằm sai ở top-level `docs/`
- `reports/` — báo cáo rà soát, consolidation, scope planning, và freeze close-out (ví dụ: `ATP_Docs_Review_Report_VI.md`, `ATP_v0_2_0_Freeze_Closeout.md`, `ATP_v0_4_0_Freeze_Closeout.md`, ATP v1.0 Slice D bundle: baseline `ATP_v1_0_Slice_D_*`, integration review, consolidation decision, freeze-readiness assessment, documentation governance close-out; ATP v1.0 Slice E baseline bundle: `ATP_v1_0_Slice_E_Resulting_Operational_State_Move_Closure_Contract.md`, `ATP_v1_0_Slice_E_Closure_State_Model.md`, `ATP_v1_0_Slice_E_Result_Traceability_Model.md`, `ATP_v1_0_Slice_E_Scope_and_NonGoals.md`, `ATP_v1_0_Slice_E_Baseline_Execution_Plan.md`)
  - current execution-line freeze close-out example: `ATP_v1_3_Freeze_Closeout.md`
  - latest execution-line freeze close-out example: `ATP_v1_4_Freeze_Closeout.md`
- `bundles/` — bản nén tài liệu trước governance (ví dụ: `docs_pre_governance_bundle.zip`)

## Tài liệu liên quan

- Nguồn chuẩn active: `docs/architecture/`, `docs/design/`, `docs/operators/`, `docs/governance/`
- Bản đồ tài liệu: `docs/README.md`
