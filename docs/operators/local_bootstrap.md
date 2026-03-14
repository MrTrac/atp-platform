# Local bootstrap

Tài liệu này mô tả bootstrap local cho ATP theo baseline hiện tại.

## Working directory

Làm việc từ:

```text
SOURCE_DEV/platforms/ATP
```

## Các bước bootstrap tối thiểu

1. kiểm tra `python3 --version`
2. chạy `python3 -m compileall cli core tests`
3. chạy `make test`

## Ví dụ CLI

- `./cli/atp validate tests/fixtures/requests/sample_request_atp.yaml`
- `./cli/atp run tests/fixtures/requests/sample_request_exec_echo.yaml`
- `./cli/atp inspect`

## Ghi chú vận hành

- không tạo runtime artifact production trong repo ATP
- ATP v0 hiện là baseline repo-local đã khép kín đến M8
- các output của validation, review, approval gate, và finalization vẫn thiên về summary semantics
- production workspace writes vẫn là deferred scope sau ATP v0
