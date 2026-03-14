# ATP v0.1 Hardening Gap Map

- **Ngày:** 2026-03-14
- **Phạm vi:** ATP v0.1 hardening trong boundary của ATP MVP v0 freeze
- **Nguyên tắc:** chỉ ghi nhận drift, inconsistency, và hardening item; không mở rộng kiến trúc

## HGM-01

- **Title:** `final_status` drift giữa handoff và finalization
- **Severity:** High
- **Area:** Handoff / Finalization
- **Affected files:** `cli/run.py`, `core/finalization/finalize.py`, `tests/integration/test_happy_path.py`, `tests/integration/test_reject_path.py`, `tests/unit/test_finalization_flow.py`
- **Source-of-truth reference:** `README.md`; `docs/architecture/overview.md`; `docs/design/handoff_model.md`; `docs/architecture/orchestration_flow.md`
- **Current issue:** `inline_context.final_status` đang lấy trực tiếp từ `approval_status`, khiến handoff và finalization dùng hai vocabulary khác nhau cho cùng một semantic chain.
- **Recommended correction:** Tạo mapping `approval_status -> final_status` ổn định và dùng chung cho handoff và finalization summary.
- **Status:** fixed now
- **Short rationale:** Đây là semantic drift trực tiếp trong chuỗi M8, sửa nhỏ nhưng giá trị cao.

## HGM-02

- **Title:** `evidence_bundle` handoff đang chứa quá nhiều artifact trung gian
- **Severity:** High
- **Area:** Handoff semantics
- **Affected files:** `cli/run.py`, `tests/integration/test_happy_path.py`, `tests/integration/test_reject_path.py`
- **Source-of-truth reference:** `docs/design/handoff_model.md`; `docs/architecture/workspace_artifact_handoff.md`
- **Current issue:** Handoff evidence đang mang cả raw, filtered, selected, authoritative artifacts thay vì continuity payload gọn hơn.
- **Recommended correction:** Chỉ giữ selected continuity artifact trong `selected_artifacts`, còn authoritative selection giữ qua `authoritative_refs`.
- **Status:** fixed now
- **Short rationale:** Giảm drift với mô hình handoff đã freeze mà không thay đổi capability.

## HGM-03

- **Title:** Run-state transition làm mờ thứ tự `Approval -> Finalization -> Close/Continue`
- **Severity:** Medium
- **Area:** Run-state / flow traceability
- **Affected files:** `cli/run.py`
- **Source-of-truth reference:** `docs/architecture/overview.md`; `docs/architecture/orchestration_flow.md`; `docs/design/run_model.md`
- **Current issue:** Reject hoặc needs-attention path có thể nhảy state sớm trước khi `FINALIZED`, làm trace flow kém rõ.
- **Recommended correction:** Luôn ghi `FINALIZED` trước quyết định `CLOSED` hoặc `CONTINUE_PENDING`.
- **Status:** fixed now
- **Short rationale:** Đây là hardening cho traceability của 14-step flow, không phải thay đổi kiến trúc.

## HGM-04

- **Title:** Placeholder runtime path chưa phản ánh boundary chuẩn
- **Severity:** High
- **Area:** Repo vs workspace boundary
- **Affected files:** `adapters/filesystem/workspace_writer.py`, `tests/unit/test_artifact_model.py`
- **Source-of-truth reference:** `README.md`; `docs/architecture/repo_boundary.md`; `docs/operators/workspace_layout.md`
- **Current issue:** `deferred-workspace/...` là placeholder mơ hồ, không bám semantics `SOURCE_DEV/workspace`.
- **Recommended correction:** Chuẩn hóa runtime path hint về `SOURCE_DEV/workspace/<area>/<run_id>` và giữ repo-local serialization path chỉ cho test fixtures.
- **Status:** fixed now
- **Short rationale:** Sửa nhỏ nhưng quan trọng để không làm mờ boundary source/runtime.

## HGM-05

- **Title:** Wording mức module vẫn mô tả baseline như seed/skeleton
- **Severity:** Medium
- **Area:** Architecture wording / CLI contract
- **Affected files:** `cli/README.md`, `core/README.md`, `cli/atp`, `cli/validate.py`, `cli/inspect.py`
- **Source-of-truth reference:** `README.md`; `docs/architecture/overview.md`
- **Current issue:** Một số entrypoint và README mức module vẫn mô tả ATP như skeleton hoặc early milestone surface.
- **Recommended correction:** Chuẩn hóa wording sang repo-local baseline M8, không đổi behavior.
- **Status:** fixed now
- **Short rationale:** Giảm drift giữa docs active và implementation thực tế.

## HGM-06

- **Title:** Test coverage còn thiếu ở failure normalization và boundary helper
- **Severity:** Medium
- **Area:** Testing / contracts
- **Affected files:** `tests/unit/test_execution_flow.py`, `tests/unit/test_finalization_flow.py`, `tests/unit/test_artifact_model.py`
- **Source-of-truth reference:** `docs/design/run_model.md`; `docs/design/handoff_model.md`; `docs/architecture/repo_boundary.md`
- **Current issue:** Chưa có test explicit cho non-zero execution normalization, finalization vocabulary mapping, và workspace path semantics.
- **Recommended correction:** Bổ sung unit test nhỏ, tập trung vào semantic contract.
- **Status:** fixed now
- **Short rationale:** Tăng confidence mà không thêm infrastructure mới.

## HGM-07

- **Title:** Một số README mức module vẫn còn wording cũ
- **Severity:** Low
- **Area:** Module docs wording
- **Affected files:** `core/*/README.md`, `schemas/README.md`, `tests/README.md`
- **Source-of-truth reference:** `README.md`; `docs/architecture/overview.md`
- **Current issue:** Vẫn còn vài README dùng phrasing kiểu seed/baseline sớm hoặc mô tả hẹp hơn implementation thực tế.
- **Recommended correction:** Chuẩn hóa tiếp ở pass sau nếu cần, nhưng không bắt buộc cho semantic correctness hiện tại.
- **Status:** deferred
- **Short rationale:** Giá trị chủ yếu là wording cleanup, không chặn correctness của v0.

## HGM-08

- **Title:** Chưa có schema-level validation runner cho preview outputs
- **Severity:** Low
- **Area:** Schema / contract review
- **Affected files:** `schemas/*`, CLI preview outputs, tests`
- **Source-of-truth reference:** `docs/design/request_model.md`; `docs/design/artifact_model.md`; `docs/design/handoff_model.md`
- **Current issue:** Contract hiện được giữ chủ yếu bằng code shape và tests, chưa có layer kiểm chứng schema tự động cho preview outputs.
- **Recommended correction:** Chỉ xem xét ở phase hardening tiếp theo; không cần thêm trong pass hiện tại.
- **Status:** deferred
- **Short rationale:** Hữu ích nhưng vượt quá ngưỡng “small but important fix” của pass này.

## Nhận xét chính

- Flow 14 bước trong implementation hiện có bám được freeze, nhưng phần wording và vài semantic link giữa approval, finalization, handoff, và close-run đã có drift nhỏ cần siết lại.
- Boundary repo/runtime về cơ bản đúng vì chưa materialize runtime artifact, nhưng placeholder path cũ là điểm dễ gây hiểu sai nhất.
- ATP vẫn ở đúng scope của v0; các fix áp dụng trong pass này đều là refinement và hardening, không phải feature expansion.
