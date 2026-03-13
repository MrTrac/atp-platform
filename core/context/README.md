# Context

`core/context` chua implementation M4 cho Context Packaging.

Input chinh:

- normalized request
- classification result
- product resolution result

Output M4:

- task manifest
- product context
- selected evidence list
- in-memory evidence bundle

Context Packaging trong M4 chi gom:

- chot task manifest shape
- trich product context can thiet tu resolution
- chon artifact cot loi cho continuity cua buoc tiep theo
- tao evidence bundle dict-based

Deferred ro rang cho M5+:

- routing preparation
- capability/routing decisions thuc te
- exchange bundle packaging
- workspace artifact materialization
