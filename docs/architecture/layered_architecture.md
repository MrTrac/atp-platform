# Kiến trúc phân lớp

ATP v0 giữ các lớp chính sau:

- CLI
- core control-plane modules
- adapters
- registry
- schemas
- profiles
- templates

## Boundary theo lớp

- source repo: `platforms/ATP`
- product repo tối thiểu được tham chiếu: `products/TDF`
- runtime workspace: `workspace`

## Vai trò của từng lớp trong ATP v0

### Lớp control-plane

Các module core xử lý:

- request intake
- classification
- product resolution
- context packaging
- routing
- execution orchestration
- validation và review
- approval gate và finalization summary

### Lớp adapter

Lớp adapter tách logic điều phối khỏi logic thực thi cụ thể.

Trong ATP v0:

- `core/routing` chọn provider và node
- `core/execution/executor` ánh xạ route sang adapter
- `adapters/subprocess` thực thi local command được hỗ trợ
- `core/execution/orchestrator` chuẩn hóa execution result thành cấu trúc ATP

### Lớp registry

Registry lưu dữ liệu file-based phục vụ:

- product resolution
- routing preparation
- policy lookup
- capability, provider, và node mapping

## Điều chưa mở rộng trong baseline

Remote execution trong ATP v0 mới dừng ở mức placeholder hoặc contract-backed. ATP chưa có runtime behavior đầy đủ cho remote orchestration path.
