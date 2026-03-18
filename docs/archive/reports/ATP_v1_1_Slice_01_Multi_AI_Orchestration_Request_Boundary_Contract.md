# ATP v1.1 Slice 01 Multi-AI Orchestration Request Boundary Contract

## 1. Document status

- Tài liệu: bounded execution contract artifact
- Slice: `v1.1 Slice 01`
- Status: execution baseline artifact
- Date: 2026-03-18
- Execution branch context: `codex/release-v1.1-execution`
- Baseline inherited: `v1.0.4`

## 2. Slice identity

- Slice name: `Multi-AI Orchestration Request Boundary Contract`
- Execution line: `v1.1 Execution Line — Open`
- Slice role: first bounded execution slice của `v1.1`

## 3. Purpose

Slice này định nghĩa một request boundary contract hẹp cho ATP khi đi vào multi-AI orchestration capability line của `v1.1`.

Contract này tồn tại để chốt:

- ATP nhận orchestration request ở boundary nào
- boundary đó cho phép và không cho phép gì
- input/output expectations nào là tối thiểu
- policy-enforcement checkpoints nào phải được giữ explicit
- traceability/testability expectations nào phải có ngay từ request boundary

Slice này không phải orchestration engine, không phải routing subsystem, và không phải execution graph rộng.

## 4. Boundary statement

`Multi-AI Orchestration Request Boundary` là lớp contract đầu vào hẹp nơi ATP:

- nhận một orchestration-intent request đã explicit
- ghi rõ boundary metadata tối thiểu của request đó
- gắn policy checkpoints ban đầu
- chuẩn bị traceability surface đủ để các bước sau có thể được review

Boundary này chưa quyết định toàn bộ orchestration flow phía sau. Nó chỉ chốt request boundary contract của slice đầu tiên.

## 5. Input expectations

Một request ở boundary này tối thiểu phải explicit:

- `request_id`
- `orchestration_intent`
- `request_scope`
- `request_constraints`
- `request_policy_context`
- `request_traceability_seed`

Input expectations này tồn tại ở mức contract. Slice này chưa chốt runtime transport, persistence detail, hay execution routing detail.

## 6. Output expectations

Boundary này tối thiểu phải cho phép ATP materialize một bounded request-boundary artifact với:

- request identity summary
- accepted boundary scope
- rejected / out-of-bound indicators nếu có
- policy checkpoint summary
- traceability hooks để review/test các bước sau

Output expectations này vẫn ở mức contract artifact, không phải full runtime result.

## 7. Policy-enforcement checkpoints

Tại boundary này ATP phải giữ explicit tối thiểu các checkpoints sau:

- scope admissibility checkpoint
- policy-context presence checkpoint
- orchestration-boundary classification checkpoint
- traceability-seed checkpoint

Slice này chỉ chốt các checkpoints như contract obligations. Slice này chưa triển khai policy engine đầy đủ.

## 8. Traceability / testability expectations

Boundary contract của slice này phải đủ để các bước sau có thể reconstruct tối thiểu:

- request nào đi vào boundary
- request đó thuộc orchestration intent nào
- boundary scope nào đã được chấp nhận
- checkpoint nào đã được áp vào request
- traceability seed nào được dùng để nối tiếp review/test

Testability expectations ở slice này là:

- contract shape phải rõ và bounded
- checkpoints phải reviewable
- traceability hooks phải explicit
- boundary wording không được drift sang engine breadth

## 9. Non-goals

Slice này không chốt:

- orchestration scheduler
- execution graph engine
- cross-agent runtime coordination đầy đủ
- provider routing
- release/integration behavior
- merge/tag/release path

## 10. Final note

Slice 01 chỉ tạo request boundary contract đầu tiên cho `v1.1`. Nó là entry execution artifact hẹp, additive trên `v1.0.4`, và phải được đọc như một bounded contract surface, không phải broader orchestration implementation.
