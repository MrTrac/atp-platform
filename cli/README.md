# ATP CLI

`cli/` là entry surface cho ATP control-plane baseline trong repo source.

- `atp`: shell entrypoint
- `run.py`: preview flow ATP v0 và materialize runtime outputs theo baseline đã freeze
- `inspect.py`: inspect summary/runtime references ở mức ATP v0
- `validate.py`: preview flow validate không thực thi execution

Phạm vi hiện hành:

- local preview/control surface cho ATP
- không thay thế operators UI
- không phải orchestration console hay remote control plane
