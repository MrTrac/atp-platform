# Subprocess

`adapters/subprocess` chứa local non-LLM execution path cho ATP M6.

Phạm vi:

- chạy local command an toàn qua `subprocess.run`
- ưu tiên `payload.command_argv`
- capture `exit_code`, `stdout`, `stderr`, `command`

Không mở rộng sang retry, shell orchestration phức tạp, hay remote runtime execution.
