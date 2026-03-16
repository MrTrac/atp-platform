# ATP-side AI_OS Thin Integration

- **Mục đích:** Chuẩn hóa lớp tích hợp mỏng từ ATP sang AI_OS ở mức repo-local, read-only hoặc low-risk.
- **Phạm vi:** Bridge files, ATP-side verifier hooks, authority path discovery, và readiness checks trước khi ghép ATP với AI_OS.
- **Trạng thái:** Active.

## Mục tiêu

ATP chỉ cung cấp lớp phối hợp mỏng để AI_OS có thể:

- đọc đúng repo identity và Git context hiện tại
- tìm đúng authority docs và archive evidence trong ATP
- gọi các verifier hooks read-only ở phía ATP
- đồng bộ continuity/handoff với ATP mà không nhúng AI_OS vào runtime hoặc business logic

Tài liệu này không thay ATP governance. ATP docs, repo state, Git state, tests, và baseline hiện hành vẫn là authority ở phía ATP.

## Ranh giới tích hợp

ATP-side AI_OS integration phải giữ các ranh giới sau:

- không sửa business logic của ATP chỉ để phục vụ AI_OS
- không chạm ATM runtime, ATM data, hoặc operation plane
- không thay `gsgr` làm Git-safe execution layer
- không biến ATP thành AI workflow engine, orchestration engine, hay handoff engine lớn
- không dùng AI_OS như authority thay thế cho docs/Git/test state của ATP

AI_OS trong bối cảnh ATP chỉ là:

- continuity layer
- context sync layer
- baseline sync layer
- orchestration layer ở ngoài repo ATP

## Authority order ở phía ATP

Khi AI_OS phối hợp với ATP, thứ tự authority phải được hiểu như sau:

1. current human-approved task instruction
2. active ATP docs trong `docs/`
3. current repo state và Git state của ATP
4. current tests và review evidence liên quan
5. external AI_OS context, handoff, và global rules khi không mâu thuẫn với ATP authority

Nếu AI_OS và ATP authority docs/Git state mâu thuẫn, không được tự hòa giải bằng suy đoán. Phải surface conflict đó.

## Bridge surface hiện có

Các bridge files ATP-side hiện dùng để nói cho AI tools biết cách phối hợp với AI_OS:

- `AGENTS.md`
- `AI_OS_CONTEXT.md`
- `CLAUDE.md`
- `.cursorrules`
- `.github/copilot-instructions.md`

Vai trò của các file này là:

- trỏ tới AI_OS context ngoài repo
- nhắc read order tối thiểu
- nhắc approval gates
- nhắc rằng ATP docs và repo state vẫn là authority ở phía ATP

Các bridge files này không được coi là business/runtime module.

## ATP-side verifier hooks

ATP cung cấp helper script read-only:

- `scripts/aios_bridge.sh`

Các lệnh hiện có:

- `scripts/aios_bridge.sh context`
- `scripts/aios_bridge.sh status`
- `scripts/aios_bridge.sh authority`
- `scripts/aios_bridge.sh verify`

Các lệnh này chỉ:

- đọc repo path
- đọc Git root, branch, HEAD, latest tag, worktree status
- expose governance root, operators root, archive reports root
- expose bridge file locations
- kiểm tra sự tồn tại của ATP-side bridge surface tối thiểu

Các lệnh này không được:

- merge
- tag
- reset
- push
- ghi state vào runtime/business area

## Makefile wrappers

ATP có các wrappers mỏng để AI_OS hoặc operator gọi ổn định hơn:

- `make aios-context`
- `make aios-status`
- `make aios-authority`
- `make aios-verify`

Các target này chỉ gọi `scripts/aios_bridge.sh` với subcommand tương ứng.

## Những gì AI_OS nên đọc/gọi ở ATP-side

Khi cần phối hợp với ATP, AI_OS nên ưu tiên:

1. ATP docs authority trong `docs/`
2. ATP Git state hiện tại
3. `scripts/aios_bridge.sh authority`
4. `scripts/aios_bridge.sh context`
5. `scripts/aios_bridge.sh verify`

Nói ngắn gọn:

- authority nằm ở docs/Git/tests của ATP
- bridge surface chỉ giúp AI_OS khám phá và xác minh ATP-side state

## Những gì ATP-side integration tuyệt đối không làm

- không inject AI_OS vào ATP runtime model
- không tạo ATP-local orchestration control plane cho AI_OS
- không tạo queue, planner engine, hoặc handoff engine lớn trong ATP
- không ghi state AI_OS vào business/runtime data của ATP
- không thay ruleset Git-safe hiện có

## Readiness check trước khi ghép ATP với AI_OS

ATP-side được coi là sẵn sàng cho two-side integration test khi:

- bridge files đang đồng nhất về authority wording
- `scripts/aios_bridge.sh verify` chạy pass
- `make aios-verify` chạy pass
- authority roots được expose rõ
- current branch, HEAD, latest tag, worktree status đọc được ổn định
- không có thay đổi nào tác động ATM runtime/data plane

## Tài liệu liên quan

- `docs/README.md`
- `docs/operators/README.md`
- `docs/governance/README.md`
- `docs/governance/Global_Safe_Git_Branch_Guard_Rule.md`
- `docs/governance/reference/ATP_Global_Shorthand_and_Alias_Rules.md`
- `AGENTS.md`
