# Bố cục workspace

Runtime workspace chính thức của ATP được mô hình hóa quanh các vùng sau:

- `SOURCE_DEV/workspace/atp-runs`
- `SOURCE_DEV/workspace/atp-artifacts`
- `SOURCE_DEV/workspace/atp-cache`
- `SOURCE_DEV/workspace/atp-staging`
- `SOURCE_DEV/workspace/exchange`

## Quy tắc

Repo ATP chỉ `reference` runtime zone này. ATP source repo không phải nơi chứa runtime artifact production.
