# ATP v0.1 Hardening Checklist

- **Ngày:** 2026-03-14
- **Phạm vi:** hardening ATP v0 theo freeze hiện hành, không mở rộng kiến trúc

## Architecture conformance

- [x] Đọc `README.md`, `docs/architecture/overview.md`, freeze record, và implementation plan trước khi sửa
- [x] Map implementation hiện tại vào flow ATP 14 bước
- [x] Kiểm tra alignment giữa docs wording, module naming, và CLI behavior
- [x] Xác định drift semantic ở approval, finalization, handoff, và close-run
- [x] Tránh tạo layer, module, hoặc flow mới ngoài ATP v0 freeze

## Repo/workspace boundary

- [x] Rà soát code và doc có làm mờ ranh giới giữa source repo và runtime workspace hay không
- [x] Xác nhận runtime artifact không được treated như repo-local persistent state
- [x] Kiểm tra placeholder path/runtime hint trong adapters
- [x] Siết semantics về `SOURCE_DEV/workspace` khi có drift rõ ràng

## Schema/contracts

- [x] Rà request, artifact, routing, run, approval, và handoff contracts hiện có
- [x] Đối chiếu semantics giữa schema intent, CLI output, và test assumptions
- [x] Chỉ sửa khi inconsistency đủ rõ và nằm trong ATP v0 semantics
- [ ] Thêm automated schema validation runner cho preview output nếu phase sau cần

## CLI semantics

- [x] Rà `cli/run.py`, `cli/validate.py`, `cli/inspect.py`, và `cli/atp`
- [x] Kiểm tra input contract và output summary semantics
- [x] Kiểm tra failure semantics và messaging wording
- [x] Sửa drift nhỏ về wording hoặc semantic mapping nếu có

## Handoff / finalization / approval

- [x] Đối chiếu `validation -> review -> approval -> finalization -> handoff -> close/continue`
- [x] Đồng bộ `final_status` với finalization semantics
- [x] Giữ `evidence_bundle` theo selected continuity artifact
- [x] Kiểm tra authoritative artifact selection không drift với handoff references
- [x] Đảm bảo run-state flow không bỏ qua `FINALIZED`

## Testing / retest

- [x] Rà coverage ở execution failure normalization
- [x] Rà coverage ở finalization consistency
- [x] Rà coverage ở handoff artifact semantics
- [x] Rà coverage boundary helper giữa repo và workspace
- [x] Chạy targeted tests cho vùng vừa sửa
- [x] Chạy full `make test`
- [x] Ghi lại phần fixed now và deferred trong reports
