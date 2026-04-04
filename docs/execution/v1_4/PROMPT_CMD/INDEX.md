# ATP v1.4 — PROMPT_CMD Index

## 1. Mục đích

Thư mục `PROMPT_CMD/` của `ATP v1.4` dùng để định nghĩa các feature-execution programs ở mức planning/execution-design cho line:

**ATP v1.4 — Operator Reviewability Consolidation**

Bộ tài liệu này được mở sau khi:

- `ROADMAP_EXECUTION.md` của `v1.4` đã được chốt
- objective đã được khóa
- feature line đã được khóa
- authorization boundary đã được chốt:
  - GO cho `PROMPT_CMD/INDEX.md`
  - GO cho 3 feature-program files
  - chưa authorize coding

Các file trong thư mục này không phải implementation artifact.
Chúng chỉ dùng để:

- định nghĩa execution contract cho từng feature
- khóa scope / out-of-scope
- khóa pack discipline
- khóa fail-stop boundaries
- chuẩn bị điều kiện để sau này có thể viết prompt executor đúng bounded shape

---

## 2. Canonical line objective

**ATP v1.4 — Operator Reviewability Consolidation**

Line này chỉ hợp lệ nếu nó làm ATP:

- dễ review hơn
- coherent hơn
- rõ posture hơn

và không làm ATP:

- operational hơn
- orchestration-ready hơn
- automation-ready hơn
- integration/deployment capable hơn

---

## 3. Locked feature line

### F-301 — Operator Review Summary
Feature đầu tiên của line `v1.4`, nhằm tạo một bounded, review-oriented summary surface cho operator/reviewer.

File:
- `01_operator_review_summary.md`

### F-302 — Handoff / Planning Surface Consolidation
Feature thứ hai của line `v1.4`, nhằm tăng coherence giữa các bounded planning/handoff/review surfaces hiện có.

File:
- `02_handoff_planning_surface_consolidation.md`

### F-303 — Reviewability Posture Guard
Feature thứ ba của line `v1.4`, nhằm khóa regression semantics cho toàn line reviewability.

File:
- `03_reviewability_posture_guard.md`

---

## 4. Execution order

Thứ tự execution-design của `v1.4` phải là:

1. F-301 — Operator Review Summary
2. F-302 — Handoff / Planning Surface Consolidation
3. F-303 — Reviewability Posture Guard

Không đảo thứ tự nếu chưa có evidence rất mạnh.

Lý do:
- F-301 tạo review summary center
- F-302 làm coherent hơn các bounded surfaces liên quan
- F-303 khóa posture cuối line

---

## 5. Shared carried-forward invariants

Toàn bộ feature-program trong `v1.4` phải preserve nguyên trạng:

- JSON-first output remains canonical
- repo-local CLI entrypoint remains `./atp`
- single-request path remains intact
- multi-request path remains bounded and explicit
- session tracking remains explicit and non-persistent
- export remains opt-in only
- composition remains synchronous and human-initiated
- no orchestration
- no scheduler
- no automation
- no provider abstraction
- no daemon/background execution
- no real external integration implementation
- no real deployment execution

Ngoài ra phải preserve posture:

- ATP là bounded review/handoff/planning support toolchain
- ATP không phải operational control plane

---

## 6. Shared pack discipline

Mỗi feature trong `v1.4` phải đi theo 3-pack discipline:

### P1 — Gap capture / evidence
- test-first hoặc evidence-first
- chứng minh bounded gap thật sự tồn tại
- không đổi runtime nếu chưa cần

### P2 — Bounded surface / contract implementation
- thêm surface nhỏ nhất cần thiết
- descriptive only
- reviewability only
- không capability inflation

### P3 — Posture / regression lock
- khóa wording
- khóa non-operational posture
- xác nhận canonical/smoke paths không drift

---

## 7. Shared fail-stop boundaries

Mọi feature-program phải dừng ngay nếu xuất hiện bất kỳ drift nào sau đây:

- orchestration semantics
- automation semantics
- scheduler/background worker semantics
- provider abstraction
- registry/persistence/history/audit semantics
- real integration execution semantics
- real deployment execution semantics
- workflow engine semantics
- control-plane/dashboard semantics
- scope inflation beyond small bounded line
- wording khiến ATP bị hiểu nhầm là operational platform

---

## 8. Authorization status

Trạng thái hiện tại của `v1.4`:

- execution-design roadmap: approved
- `PROMPT_CMD` generation: approved
- coding / implementation: chưa được authorize trong index này

Tức là:
- được phép viết feature-program files
- chưa được phép dùng các file này như coding approval mặc định

---

## 9. Expected next governance use

Bộ `PROMPT_CMD` này sẽ được dùng để:

- review execution shape của từng feature
- viết prompt executor bounded hơn ở bước sau nếu có approval
- giữ line `v1.4` đúng small-line posture

Không được dùng bộ này như:
- implicit implementation approval
- justification cho broad feature growth
- excuse để bỏ qua review gate tiếp theo

---

## 10. Kết luận

`PROMPT_CMD/` của `ATP v1.4` tồn tại để giữ line này:

- small
- bounded
- governance-first
- reviewability-focused

Mọi file trong thư mục này phải giúp ATP:

- dễ review hơn
- coherent hơn
- rõ posture hơn

và không được làm ATP:

- operational hơn
- autonomous hơn
- orchestration/automation-ready hơn
