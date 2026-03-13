# Overview

ATP la platform repo dieu phoi ATP v0 theo mo hinh control-plane, provider-agnostic, artifact-centric.

Pham vi da seed den M5:

- nhan request
- normalize
- classify
- resolve `ATP` hoac `TDF` bang file-based registry/profile/policy
- package context
- prepare route
- select route bang capability/provider/node-aware rules

Capability-based routing trong M5 co muc tieu xac dinh:

- capability nao dang can cho request hien tai
- provider nao support capability do
- node nao tuong thich voi provider da chon
- vi sao route local-first duoc chon

Nhung phan sau van defer:

- execution
- validation/review
- approval gate runtime
- finalization
