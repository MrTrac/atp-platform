# Execution

`core/execution` chua implementation M6 cho execution qua adapter.

M6 ho tro mot duong thuc thi that:

- provider `non_llm_execution`
- node `local_mac`
- local command qua subprocess adapter

Phan vai:

- contract: khoa shape giua core va adapter
- adapter: noi truc tiep chay command hoac tra ket qua deferred
- executor: map route sang adapter
- orchestrator: phoi hop execution stage va normalize output

Deferred ro rang cho M7+:

- validation/review
- approval/finalization
- production artifact lifecycle
- retry engine
