# Runbook ATP v0

Runbook M6 cho ATP:

1. tiep nhan request file
2. normalize request
3. classify request
4. resolve product
5. package context
6. prepare va select route
7. thuc thi local command neu route la `non_llm_execution` + `local_mac`
8. xem execution summary tren CLI

Supported execution path hien tai:

- local non-LLM qua subprocess

Van hanh v0:

- uu tien `payload.command_argv`
- `validate` khong thuc thi command
- `run` co the thuc thi local command an toan cho fixture/dev flow
- validation/review/approval van chua duoc implement
