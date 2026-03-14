# ATP CLI

`cli/` là entry surface cho ATP control-plane baseline trong repo source.

- `atp`: shell entrypoint
- `run.py`: preview flow ATP v0 và materialize runtime outputs theo baseline đã freeze
- `inspect.py`: read-only inspect cho summary file hoặc current-task state đã materialize dưới workspace
- `validate.py`: preview flow validate không thực thi execution

Phạm vi hiện hành:

- local preview/control surface cho ATP
- read-only inspect surface hẹp cho current-task traceability của v0.4
- không thay thế operators UI
- không phải orchestration console hay remote control plane
