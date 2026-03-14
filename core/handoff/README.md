# Handoff

`core/handoff` chứa các cơ chế handoff tối thiểu đang được support trong ATP v0:

- Inline Context
- Evidence Bundle
- Exchange Bundle
- Manifest Reference

Baseline hiện tại:

- giữ handoff summary ở dạng dict-based, bám đúng control-plane shape đã freeze
- giữ continuity tối thiểu cho next step, không mở rộng thành workflow engine
- từ v0.3 có thêm exchange-boundary decision, continuation state, và traceability support tối thiểu
- không mở rộng thành exchange subsystem, continuation subsystem, hay persistence layer rộng hơn
