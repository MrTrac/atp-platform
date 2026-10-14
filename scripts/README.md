# Scripts

`scripts/` chứa safe bootstrap và validation helpers cho ATP source repo.

Phạm vi:

- hỗ trợ bootstrap, validation, và repo maintenance ở mức nhẹ
- không phải runtime workflow engine
- gồm cả ATP-side read-only bridge helpers cho AI_OS, ví dụ `aios_bridge.sh`
- `ci_local.sh` (`make ci-local`): chạy bộ kiểm như CI chạy, tức clone sạch của một commit, môi trường đã lọc, từng phiên bản Python của ma trận CI. Chạy trước khi push. Xem README (mục Local bootstrap)
