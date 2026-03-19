# AI_OS ↔ ATP Boundary Reference

## Mục đích

Tài liệu này là ATP-local boundary interpretation cho mối quan hệ **AI_OS ↔ ATP**.

Nó không phải canonical doctrine mới.  
Canonical doctrine cho connection model family vẫn nằm ở AI_OS. ATP chỉ giữ local interpretation/reference ngắn để áp dụng đúng boundary trong repo này.

## Canonical source orientation

Khi cần hiểu đầy đủ integration model cấp cha, phải đọc:

- `AI_OS/40_INTEGRATIONS/AI_OS_ATP_INTEGRATION_MODEL.md`

Tài liệu này chỉ giải thích boundary theo ngữ cảnh ATP-local để tránh hiểu nhầm runtime scope.

## ATP có thể kế thừa gì từ AI_OS

Ở lớp governance/model, ATP có thể kế thừa:

- authority / precedence model
- governance doctrine
- execution-roadmap model
- prompt-cmd model
- handoff / checkpoint / review / verify / freeze discipline
- safe Git discipline
- bounded projection/reference pattern
- bounded helper tooling cho context / handoff / checkpoint / validation

## ATP không được ngụ ý gì từ AI_OS

ATP không được hiểu là đã có hoặc nên mở theo mặc định:

- live control plane semantics
- orchestration / automation / scheduler / daemon wording
- provider / runtime dependency language
- persistent central state / history / audit board semantics
- real external integration runtime claims
- real deployment runtime claims
- runtime node semantics dưới AI_OS
- live managed project service semantics

## Allowed

- governance inheritance
- handoff / checkpoint / freeze / review / verify discipline
- bounded projection/reference pattern
- bounded helper tooling cho context/handoff/checkpoint/validation
- local derivative docs ngắn để giúp reviewer trong ATP repo hiểu đúng authority path

## Disallowed

- live control plane semantics
- orchestration / automation / scheduler / daemon wording
- provider / runtime dependency language
- persistent central state / history board semantics
- central registry semantics
- live execution controller semantics
- real integration runtime claims
- real deployment runtime claims

## Reopen boundary

ATP không reopen chỉ vì AI_OS governance docs tiếp tục evolve.

ATP chỉ nên reopen line mới khi xuất hiện:

- real repeated repo-grounded friction
- evidence rằng friction đó không thể xử lý bằng bounded clarification nhỏ
- human-approved planning basis mới

## Current ATP posture lock

Tại thời điểm reference này được tạo, ATP vẫn phải được hiểu là:

- frozen governance baseline sau `v1.4`
- bounded
- repo-local
- human-gated
- non-operational
- không orchestration
- không automation
- không scheduler / daemon
- không provider abstraction
- không real integration runtime
- không real deployment runtime

## Boundary statements (locked)
Các statement sau phải giữ nguyên **ý nghĩa** và không được diễn giải lỏng hơn:

- **AI_OS governs ATP, not operates ATP live.**
- **ATP materializes the model, not a runtime control plane.**
- **Helper tooling assists, not orchestrates.**
- **AI_OS ↔ ATP is a governance linkage, not an operational dependency.**
