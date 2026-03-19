# AI_OS ↔ ATP Helper Tooling Reference

## Mục đích

Tài liệu này định nghĩa ATP-local boundary cho **helper tooling** quanh mối quan hệ AI_OS ↔ ATP.

Helper tooling ở đây chỉ là lớp hỗ trợ bounded.  
Nó là lớp hỗ trợ **optional**, không phải runtime platform và không phải orchestration layer.

## Helper tooling được hiểu là gì

Trong ATP-local context, helper tooling chỉ nên bao gồm:

- context export
- handoff support
- checkpointing support
- validation support
- discoverability support

## Helper tooling không được hiểu là gì

Helper tooling không được trở thành:

- orchestration layer
- background work system
- scheduler / daemon
- central state manager
- live execution controller
- provider/runtime dependency layer
- operational control surface

## Boundary sử dụng

Nếu helper tooling được nhắc tới trong ATP docs, wording phải luôn giữ rõ:

- bounded
- repo-local
- human-gated
- non-operational
- additive to governance flow only

## Current ATP posture

Tại thời điểm reference này được tạo, ATP vẫn:

- không orchestration
- không automation
- không scheduler / daemon
- không live-state board
- không central execution controller
- không real integration runtime
- không real deployment runtime

Helper tooling, nếu có, chỉ là support cho governance/execution discipline chứ không vận hành ATP như một live managed system.

## Boundary statements (locked)
Các statement sau phải giữ nguyên **ý nghĩa** khi nhắc tới helper tooling:

- **Helper tooling assists, not orchestrates.**
- **AI_OS governs ATP, not operates ATP live.**
- **ATP materializes the model, not a runtime control plane.**
- **AI_OS ↔ ATP is a governance linkage, not an operational dependency.**
