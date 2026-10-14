# Adapters

`adapters/` chứa các adapter boundaries và helper implementations mà ATP core dùng để:

- thực thi command hoặc external path ở mức tối thiểu
- shape artifact và handoff payload
- materialize runtime state dưới `SOURCE_DEV/workspace` theo baseline đã freeze

Cây này cũng là một extension-seam layer của ATP: modular boundaries ở đây cho phép ATP hấp thụ execution/runtime patterns tốt hơn từ market, nhưng chỉ qua contract-driven change và governance-controlled evolution.

Phạm vi hiện hành:

- execution adapters tối thiểu cho local path và placeholders có chủ đích cho remote/UI/API bridges
- contract layer nhẹ giữa core và adapter
- filesystem materialization cho baseline v0.2-v0.3
- filesystem/runtime traceability hardening cho baseline v0.4

Không thuộc scope của cây này:

- orchestration engine rộng
- production persistence layer
- UI subsystem
- remote execution plane hoàn chỉnh

## Trạng thái placeholder và stub (rà 14/10/2026, KD-ATP-009)

Bốn thư mục dưới đây là **architectural slot có chủ đích** từ bộ khung v0 (commit `2403d9d`, 14/3/2026). Quyết định 14/10/2026: **giữ nguyên, không xoá**. Xoá là đổi hình dạng adapter đã đóng băng
(`AGENTS.md`) và không đem lại lợi ích chức năng nào. Mỗi thư mục chỉ có `README.md` và `__init__.py`; không có mã, bài kiểm hay registry nào dùng chúng. **Chưa có use case hay chủ nào được gán.**

| Thư mục | Vai trò dự kiến (theo README của nó) | Trạng thái |
|---|---|---|
| `adapters/api` | đường thực thi hoặc tích hợp qua API | placeholder, không có runtime |
| `adapters/desktop_bridge` | tương tác qua desktop | placeholder, không có runtime |
| `adapters/local_service` | tích hợp dịch vụ cục bộ | placeholder, không có runtime |
| `adapters/ui_bridge` | tương tác qua UI | placeholder, không có runtime |

Quy tắc: khi một placeholder có mã thật thì PHẢI (1) sửa README của nó, thôi gọi là placeholder, (2) gỡ nó khỏi bảng trên, (3) bỏ nó khỏi `PLACEHOLDERS` trong `tests/unit/test_placeholder_adapters.py`.
Bài kiểm đó đỏ cho tới khi làm đủ ba việc. Một thư mục adapter mới chỉ có README cũng phải vào bảng này. Slot nào cũng **không được dùng để đưa LLM local trở lại** trên macOS (`00_AUTHORITY/Global_Mac_No_Ollama_Rule.md`).

Khác với placeholder: `adapters/ssh_remote` là **stub có mã** (49 dòng). `execute_remote` không bao giờ thực thi gì và luôn trả `status: deferred`. Đường rơi dự phòng của `core/execution/executor.py` cũng trả về đây cho mọi
provider không có handler (đã che lỗi KD-ATP-010 nhiều tháng; xem KD-ATP-015 trong sổ AI). `adapters/contracts` không phải placeholder: đó là tầng hợp đồng `typing.Protocol` giữa core và adapter.
