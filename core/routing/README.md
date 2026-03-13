# Routing

`core/routing` chua implementation M5 cho Routing Preparation va Route Selection.

Input chinh:

- normalized request
- classification result
- resolution result
- task manifest
- product context
- evidence bundle summary

Output M5:

- routing preparation data
- candidate providers
- candidate nodes
- deterministic routing result

Routing trong M5 chi gom:

- derive required capabilities
- load capability/provider/node registry data
- loc provider va node tuong thich
- chon route local-first va low-cost khi hop le

Deferred ro rang cho M6+:

- adapter execution
- provider interaction runtime
- execution retries
- output capture
