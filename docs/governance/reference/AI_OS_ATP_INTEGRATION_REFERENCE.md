# AI_OS ↔ ATP Integration Reference

## Mục đích

Tài liệu này là local reference ngắn trong ATP để chỉ tới canonical integration model giữa **AI_OS** và **ATP**.

ATP không giữ source-of-truth chính cho mô hình kết nối này.  
Canonical source nằm ở repo **AI_OS**.

## Canonical source

Canonical document:
- `AI_OS/40_INTEGRATIONS/AI_OS_ATP_INTEGRATION_MODEL.md`

## Ý nghĩa đối với ATP

ATP được vận hành như một **project instance dưới AI_OS governance model**.

Điều đó có nghĩa là ATP kế thừa từ AI_OS các lớp sau:

- authority / precedence model
- governance doctrine
- execution-roadmap model
- prompt-cmd model
- review / verify / freeze / handoff discipline
- safe Git discipline

## Boundary cần giữ

Mối quan hệ AI_OS ↔ ATP hiện tại là:

- mạnh ở lớp governance / execution model
- có thể có helper-tooling ở mức bounded
- không phải live runtime orchestration
- không phải control plane sống
- không phải provider/runtime dependency

ATP không được hiểu là:

- runtime node dưới AI_OS
- orchestration worker
- live managed project service

## Cách dùng reference này

Khi cần hiểu đúng mô hình kết nối AI_OS ↔ ATP, phải đọc canonical document trong AI_OS trước.

Tài liệu này chỉ có vai trò:
- local bridge/reference
- giúp reviewer trong ATP repo biết canonical source nằm ở đâu
- tránh tạo dual authority giữa AI_OS và ATP

## Ghi chú trạng thái hiện tại

Tại thời điểm reference này được tạo:
- ATP đang ở frozen governance baseline sau `v1.4`
- `v1.3` và `v1.4` đều đã freeze
- không có active execution line mở mặc định
- không có roadmap generation đang mở mặc định