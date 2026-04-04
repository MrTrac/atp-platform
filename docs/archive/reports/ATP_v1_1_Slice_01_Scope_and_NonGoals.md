# ATP v1.1 Slice 01 Scope and Non-Goals

## 1. Scope identity

- Slice: `v1.1 Slice 01`
- Slice name: `Multi-AI Orchestration Request Boundary Contract`
- Status: bounded execution scope note
- Date: 2026-03-18
- Branch context: `codex/release-v1.1-execution`

## 2. In-scope

Slice này chỉ in-scope các phần sau:

- contract boundary cho orchestration request đầu vào
- input/output expectations ở mức request boundary
- policy-enforcement checkpoints tối thiểu ở boundary đó
- traceability/testability expectations của boundary contract
- bounded artifact surface đủ để later implementation pass có basis review/test

## 3. Out-of-scope

Slice này out-of-scope rõ ràng với:

- orchestration slices khác ngoài request boundary contract
- broad architecture rewrite
- unrelated runtime work
- policy engine rộng
- routing/provider selection
- execution graph orchestration
- release actions
- merge `main`
- push `main`
- tag release

## 4. Boundary discipline

Slice này phải được đọc như:

- contract-first
- boundary-first
- traceability-aware
- testability-aware

Slice này không được đọc như:

- orchestration subsystem rollout
- implementation pass cho nhiều slices
- runtime expansion breadth
- release-prep pass

## 5. Non-goals

Non-goals cụ thể của slice này là:

- không tạo generalized orchestration engine
- không materialize full multi-agent runtime behavior
- không giải quyết end-to-end execution topology
- không mở rộng sang approval UI, recovery subsystem, hay routing layer
- không rewrite stable core hoặc released baseline truth của `v1.0.4`

## 6. Final scope reading

Nếu một thay đổi không trực tiếp phục vụ request boundary contract, policy checkpoints tại boundary, hoặc traceability/testability surface của boundary này, thì thay đổi đó nằm ngoài scope của Slice 01.
