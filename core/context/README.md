# Context

`core/context` chứa implementation M4 cho Context Packaging.

Input chính:

- normalized request
- classification result
- product resolution result

Output M4:

- task manifest
- product context
- selected evidence list
- in-memory evidence bundle

Context Packaging trong M4 chỉ gồm:

- chốt task manifest shape
- trích product context cần thiết từ resolution
- chọn artifact cốt lõi cho continuity của bước tiếp theo
- tạo evidence bundle dict-based

Deferred rõ ràng:

- routing preparation
- capability/routing decisions thuc te
- exchange bundle packaging
- workspace artifact materialization
