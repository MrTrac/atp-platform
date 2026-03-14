# Execution

`core/execution` chứa implementation M6 cho execution qua adapter.

Hiện hành hỗ trợ một đường thực thi thật:

- provider `non_llm_execution`
- node `local_mac`
- local command qua subprocess adapter

Phân vai:

- contract: khóa shape giữa core và adapter
- adapter: nơi trực tiếp chạy command hoặc trả kết quả deferred
- executor: map route sang adapter
- orchestrator: phối hợp execution stage và normalize output

Deferred rõ ràng:

- validation/review
- approval/finalization
- production artifact lifecycle
- retry engine
