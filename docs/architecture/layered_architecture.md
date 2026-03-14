# Layered Architecture

ATP v0 giu cac lop chinh:

- CLI
- Core control-plane modules
- Adapters
- Registry
- Schemas
- Profiles
- Templates

Boundary:

- Source repo: `platforms/ATP`
- Product repo target toi thieu: `products/TDF`
- Runtime workspace: `workspace`

M6 them execution theo lop ro rang:

- `core/routing` chon provider + node
- `core/execution/executor` map route sang adapter
- `adapters/subprocess` thuc thi local command ho tro
- `core/execution/orchestrator` normalize ket qua cho ATP

Remote execution van chi la placeholder contract-backed, chua co runtime behavior thuc te.
