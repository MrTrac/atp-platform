# ATP v1.1 Planning Entrypoint Decision

## 1. Decision identity

- Decision scope: `ATP v1.1 planning entrypoint review / approval`
- Baseline inherited: `v1.0.4`
- Branch context: `main`
- Decision date: 2026-03-18

## 2. Decision

`Approve ATP v1.1 planning entrypoint and allow opening the v1.1 planning line at governance level, while keeping execution closed until a separate explicit approval is granted.`

## 3. Planning readiness basis

Planning entrypoint decision này dựa trên:

- v1.0.4 đã merged vào `main`, pushed remote, và tagged
- Slice chain A -> B -> C -> D -> E đã khép ở mức governance/docs
- Slice E đã hoàn tất consolidation, freeze-readiness, close-out, merge-prep, và merge decision path
- current `main` worktree đang sạch trong local repo reading
- AI_OS ATP project pack đã phản ánh đúng post-release / planning readiness phase

Do đó ATP hiện có một stable baseline đủ chặt để mở planning line mới mà không cần phá current `v1.0.x` closure.

## 4. Planning entrypoint definition

`v1.1 planning entrypoint` trong pass này được hiểu là:

- điểm mở chính thức của **planning line** kế tiếp sau v1.0.x
- một governance entrypoint để xác định task statement, scope lock, boundaries, và planning artifacts cho `v1.1`
- chưa phải planning execution
- chưa phải implementation execution

Entrypoint này xuất phát từ:

- **new capability line** sau khi `v1.0.x` đã khép
- có kế thừa từ Slice E theo nghĩa Slice E đã đóng closure cho `v1.0.x`, từ đó tạo baseline đủ ổn định để planning line mới được mở
- không phải một gap blocker còn dang dở của `v1.0.x`

## 5. Proposed v1.1 planning line scope

### 5.1 In-scope for v1.1 planning

- xác định mục tiêu của `v1.1` dưới dạng slices bounded
- nghiên cứu controlled extension cho multi-AI orchestration capability
- làm rõ continuity, policy enforcement, testability, và governance boundaries của orchestration flow
- chuẩn hóa planning artifacts cho `v1.1`: brief, scope lock, review gate, acceptance criteria

### 5.2 Out-of-scope for v1.1 planning

- mở execution line cho `v1.1` trong pass này
- runtime/code implementation
- refactor lớn phá stable core của ATP
- thay đổi retroactive meaning của Slice A -> E
- merge/tag/release actions mới trong pass này

## 6. Boundary with v1.0.x

`v1.1` phải kế thừa từ `v1.0.x` các điểm sau:

- governance-first discipline
- slice-based bounded development
- review -> consolidation -> freeze -> close-out chain
- contract/state/traceability discipline đã chốt qua Slice A -> E
- safe Git / approval gate doctrine

`v1.1` không được phá hoặc rewrite:

- governance model đã chốt của `v1.0.x`
- meaning của Slice E như closure slice cho `v1.0.x`
- contract/state/traceability model đang là baseline authority
- stable core của ATP

## 7. Residual gaps classification

### 7.1 Blocker

Không có blocker thật sự để mở `v1.1` planning line ở mức governance entrypoint.

### 7.2 Non-blocking

- `V1_1_PLANNING_ENTRYPOINT.md` hiện vẫn là draft; sau decision này nó có thể được nâng sang approved planning basis trong AI_OS pack.
- Mọi transition từ planning entrypoint sang planning execution hoặc execution branch vẫn cần explicit human approval riêng.

### 7.3 Cosmetic

- Có thể bổ sung planning review checklist ngắn gọn hơn hoặc sharpen wording của planning brief về sau nếu thật sự cần readability.

## 8. Gating conditions

Các điều kiện vẫn phải giữ explicit:

- approval riêng nếu chuyển từ planning entrypoint sang planning execution
- approval riêng nếu tạo execution branch cho `v1.1`
- approval riêng cho bất kỳ architectural decision lớn nào vượt beyond planning scope
- không dev trực tiếp trên `main`

## 9. Next governance step

Bước governance hợp lệ tiếp theo là:

- `open v1.1 planning line`
- sau đó, nếu cần, thực hiện planning scope-lock / planning artifact pass

Không được suy diễn từ decision này rằng:

- `v1.1` execution đã được mở
- runtime/code pass được tự động approved
- release path mới đã được approved

## 10. Final statement

ATP hiện đã có stable baseline `v1.0.4` đủ để mở `v1.1` planning line ở mức governance.

Decision này chỉ chốt rằng planning entrypoint đã được approve. Nó không tự động mở execution, không bypass approval gates, và không thay đổi closure status của `v1.0.x`.
