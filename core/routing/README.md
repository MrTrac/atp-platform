# Routing

`core/routing` chứa implementation M5 cho Routing Preparation và Route Selection.

Input chính:

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

Routing trong M5 chỉ gồm:

- derive required capabilities
- load capability/provider/node registry data
- lọc provider và node tương thích
- chọn route local-first và low-cost khi hợp lệ

Deferred rõ ràng:

- adapter execution
- provider interaction runtime
- execution retries
- output capture
