# AI_OS ↔ ATP Integration Reference

## Mục đích

Tài liệu này là local reference ngắn trong ATP để chỉ tới canonical integration model giữa **AI_OS** và **ATP**.

ATP không giữ source-of-truth chính cho mô hình kết nối này.  
Canonical source nằm ở repo **AI_OS**.

## Canonical source

Canonical document:
- `AI_OS/40_INTEGRATIONS/AI_OS_ATP_INTEGRATION_MODEL.md`

Canonical / local split:

- **AI_OS** giữ canonical integration model và doctrine cấp cha
- **ATP** chỉ giữ local reference / local projection docs ngắn để hỗ trợ reviewer trong repo này
- ATP không tạo canonical copy thứ hai cho mô hình AI_OS ↔ ATP

## Ý nghĩa đối với ATP

ATP được vận hành như một **project instance dưới AI_OS governance model**.

Điều đó có nghĩa là ATP kế thừa từ AI_OS các lớp sau:

- authority / precedence model
- governance doctrine
- execution-roadmap model
- prompt-cmd model
- review / verify / freeze / handoff discipline
- safe Git discipline

Approved 3-layer model ở ATP-local interpretation:

- **governance/control model** nằm ở AI_OS doctrine và canonical integration model
- **ATP project instance** là repo được govern theo model đó
- **helper-tooling layer**, nếu có, chỉ được hiểu là bounded support cho context/handoff/checkpoint/validation; không phải live runtime coupling

## Boundary cần giữ

Mối quan hệ AI_OS ↔ ATP hiện tại là:

- mạnh ở lớp governance / execution model
- có thể có helper-tooling ở mức bounded
- không phải live runtime orchestration
- không phải control plane sống
- không phải provider/runtime dependency

## Boundary statements (locked)
Các statement sau phải giữ nguyên **ý nghĩa** xuyên suốt mọi tài liệu ATP-local reference:

- **AI_OS governs ATP, not operates ATP live.**
- **ATP materializes the model, not a runtime control plane.**
- **Helper tooling assists, not orchestrates.**
- **AI_OS ↔ ATP is a governance linkage, not an operational dependency.**

ATP không được hiểu là:

- runtime node dưới AI_OS
- orchestration worker
- live managed project service
- second canonical source cho integration model này

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
- ATP vẫn giữ posture bounded, non-operational, và không phụ thuộc vào AI_OS như một live orchestration runtime
