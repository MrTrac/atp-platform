# Overview

ATP la platform repo dieu phoi ATP v0 theo mo hinh control-plane, provider-agnostic, artifact-centric.

Pham vi da seed den M6:

- nhan request
- normalize
- classify
- resolve `ATP` hoac `TDF`
- package context
- prepare/select route
- thuc thi local non-LLM path khi route ho tro

Adapter contracts trong M6 co muc tieu tach:

- contract: interface dict-based
- adapter: noi thuc thi cu the
- executor: map route sang adapter
- orchestrator: dieu phoi execution stage va normalize output

Nhung phan sau van defer:

- validation/review
- approval gate runtime
- finalization
- production workspace materialization
