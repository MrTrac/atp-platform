# AI_OS ↔ ATP Staged Adoption Reference

## Mục đích

Tài liệu này mô tả ATP-local interpretation của **staged adoption** cho mối quan hệ AI_OS ↔ ATP.

Đây là local reference ngắn để giữ adoption ở mức bounded.  
Nó không phải roadmap mới và không phải canonical doctrine thay thế AI_OS.

## Nguyên tắc nền

- additive first
- compatibility first
- mapping before removal
- không reopen feature mặc định
- không ép repo churn chỉ vì model cấp cha evolve

## Stage 0 — Awareness only

ATP biết canonical model nằm ở AI_OS, nhưng chưa cần alignment local đáng kể ngoài awareness và source pointing.

## Stage 1 — Governance / reference alignment

ATP tạo các local bridge/reference docs ngắn để:

- chỉ tới canonical AI_OS source
- giải thích local boundary interpretation
- tránh dual authority

Stage này không tạo runtime coupling.

## Stage 2 — Bounded artifact / process alignment

ATP có thể align thêm ở mức:

- handoff wording
- checkpoint / freeze / review references
- discoverability / validation support

Miễn là các thay đổi vẫn:

- bounded
- additive
- compatible với frozen posture hiện có
- không mở execution line mới mặc định

## Stage 3 — Bounded helper-tooling support if justified

ATP chỉ nên chấp nhận helper-tooling support nếu có justification rõ, ví dụ:

- context export
- handoff support
- checkpointing support
- validation / discoverability support

Ngay cả ở stage này, helper-tooling vẫn không được hiểu là runtime coupling.

## Điều staged adoption không có nghĩa

Staged adoption không có nghĩa:

- runtime coupling
- live orchestration dependency
- control-plane relationship
- scheduler / daemon / background execution
- forced repo churn
- feature reopening by default

## Current ATP-local interpretation

Sau `v1.4`, ATP chỉ nên được hiểu là đang ở mức:

- governance/reference alignment
- một phần bounded artifact/process alignment

Điều này không mở line implementation mới theo mặc định và không biến ATP thành project runtime dưới AI_OS.
