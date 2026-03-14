# Subprocess

`adapters/subprocess` chua local non-LLM execution path cho ATP M6.

Pham vi M6:

- chay local command an toan qua `subprocess.run`
- uu tien `payload.command_argv`
- capture `exit_code`, `stdout`, `stderr`, `command`

Khong mo rong sang retry, shell orchestration phuc tap, hay workspace runtime.
