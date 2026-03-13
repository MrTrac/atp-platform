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

M5 giu routing o lop core + registry:

- `core/context` tao input cho routing
- `core/routing` doc capability/provider/node registry va chon route
- registry cung cap rule input, khong thuc thi side effect

Routing van provider-agnostic, capability-based, local-first, va chua buoc sang execution.
