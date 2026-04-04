# ATP v1.4 — ROADMAP_EXECUTION

## 1. Mục đích tài liệu

Tài liệu này là execution-design roadmap cho `ATP v1.4`, được mở sau khi:

- `ATP v1.3` đã close-out và freeze chính thức
- `ATP v1.4 Scope Proposal` đã được chấp nhận
- `ATP v1.4 Line Definition Proposal` đã được chấp nhận
- `ATP v1.4 Roadmap Readiness Decision` đã chốt **GO có điều kiện** cho roadmap generation

Roadmap này vẫn phải giữ đúng posture:

- small line
- bounded line
- governance-first
- reviewability-first
- planning/handoff oriented
- non-operational

Tài liệu này không mở implementation trực tiếp.
Nó chỉ định nghĩa execution-design line cho `v1.4`.

---

## 2. Line identity

### Canonical objective
**ATP v1.4 — Operator Reviewability Consolidation**

### Line intent
`v1.4` chỉ nhằm làm ATP:

- dễ review hơn
- coherent hơn ở level planning/handoff/operator
- nhất quán hơn về posture/readability

`v1.4` không nhằm làm ATP:

- mạnh hơn về execution runtime
- operational hơn
- autonomous hơn
- orchestration-ready
- integration-ready in real execution sense
- deployment-ready in real operational sense

---

## 3. Authority and lineage

### Freeze baseline
- `docs/archive/reports/ATP_v1_3_Freeze_Closeout.md`

### Planning authority for v1.4
- `docs/execution/v1_4/ROADMAP_EXECUTION.md`
- `docs/execution/v1_4/PROMPT_CMD/INDEX.md`
- `docs/execution/v1_4/PROMPT_CMD/01_operator_review_summary.md`
- `docs/execution/v1_4/PROMPT_CMD/02_handoff_planning_surface_consolidation.md`
- `docs/execution/v1_4/PROMPT_CMD/03_reviewability_posture_guard.md`

### Planning authority interpretation
`v1.4` planning authority hiện được materialize trong chính execution-design doc set dưới `docs/execution/v1_4/`. Bộ file này là canonical, path-verifiable planning chain hiện có trong repo cho line `v1.4`.

### Accepted inherited truth from v1.3
ATP hiện đã có:

- bounded artifact export surfaces
- bounded structured CLI composition
- bounded, truthful, repo-local, non-persistent session-artifact continuity
- projection-only `./atp integration-contract`
- readiness-only `./atp deployability-check`

ATP hiện vẫn không có, và không được hiểu nhầm là đã có:

- orchestration
- automation
- scheduler
- daemon/background execution
- provider abstraction
- persistence / registry / audit history
- real external integration
- real deployment execution

---

## 4. Non-negotiable carried-forward invariants

Toàn bộ các invariants sau phải được preserve nguyên trạng trong toàn bộ `v1.4`:

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

## 5. Theme combination locked for roadmap

Roadmap `v1.4` chỉ được phép bám đúng theme combination đã được accept:

### Primary theme
**Theme A — Operator Review Summary Surface**

### Secondary theme
**Theme B — Planning / Handoff Contract Consolidation**

### Companion guard theme
**Theme C — Posture Guard Hardening**

### Optional-only theme
**Theme D — Canonical Discoverability Hygiene**
- chỉ được dùng nếu có evidence thật
- không được thành core feature line
- không được biến thành broad docs cleanup

---

## 6. Execution-shape principles for v1.4

Roadmap này phải tuân theo các nguyên tắc sau:

### 6.1 Small-line discipline
- ít feature
- ít surface mới
- bounded command/report/artifact additions
- không broad refactor

### 6.2 Reviewability-first discipline
- mọi feature phải chứng minh phục vụ reviewability/coherence
- không feature nào được justify bằng future-runtime aspiration

### 6.3 No operational drift
- không được để bất kỳ feature nào bị hiểu thành:
  - orchestration prep
  - automation prep
  - provider prep
  - deploy runtime prep
  - integration runtime prep

### 6.4 Fail-stop discipline
- nếu một feature candidate không còn small/bounded/credible, phải dừng ngay
- partial line nhỏ còn tốt hơn line bị inflation

---

## 7. Candidate feature line for v1.4

Đề xuất execution line nhỏ nhất, phù hợp nhất cho `v1.4` gồm 3 feature.

---

## F-301 — Operator Review Summary

### Purpose
Tạo một bounded, operator-facing review summary surface giúp hợp nhất việc nhìn nhận ATP posture hiện tại theo cách concise, truthful, machine-readable và review-oriented.

### Why this feature exists
Sau `v1.3`, ATP có nhiều truthful bounded surfaces nhưng còn phân tán.
Feature này nhằm tạo một điểm hội tụ review-friendly, không làm ATP operational hơn.

### Intended value
- giúp operator/reviewer thấy nhanh:
  - ATP exposes what
  - ATP exports what
  - ATP projects what
  - ATP assesses what
  - ATP explicitly does not do what
- giảm fragmentation trong việc đọc ATP state

### Acceptable shape
- một bounded summary command hoặc bounded summary artifact surface
- descriptive only
- no registry semantics
- no orchestration semantics
- no runtime activation semantics

### Must not become
- control dashboard
- execution console
- orchestration surface
- meta-runtime surface
- hidden registry

### Exit condition
Feature chỉ pass nếu summary surface:
- truthful
- compact
- review-oriented
- non-operational
- regression-safe

---

## F-302 — Handoff / Planning Surface Consolidation

### Purpose
Tăng coherence giữa các bounded surfaces hiện có liên quan đến planning/handoff/review:

- `compose-chain`
- `integration-contract`
- `deployability-check`
- continuity-related posture
- freeze/close-out / planning framing nếu thật sự cần

### Why this feature exists
Hiện ATP đã có nhiều surface đúng, nhưng review/handoff contract framing còn có khả năng rời rạc.
Feature này nhằm giảm mental stitching cho operator.

### Intended value
- làm các bounded surfaces nói chuyện với nhau rõ hơn
- tăng planning/handoff coherence
- giảm posture confusion

### Acceptable shape
- bounded summaries
- narrow contract alignment
- review/handoff framing refinement
- very selective CLI/report/output harmonization nếu justified

### Must not become
- workflow engine
- phase/state engine
- execution router
- planning orchestrator
- runtime dispatcher

### Exit condition
Feature chỉ pass nếu consolidation:
- bounded
- review/planning oriented
- không spray semantics rộng
- không làm ATP bị hiểu thành execution platform

---

## F-303 — Reviewability Posture Guard

### Purpose
Khóa regression semantics cho toàn line `v1.4`, bảo đảm các additions mới không drift khỏi posture đã chốt.

### Why this feature exists
Bất kỳ line nào thêm review surfaces đều có nguy cơ bị hiểu nhầm là control surface hoặc operational maturity jump.
Feature này nhằm khóa drift đó ngay trong line.

### Intended value
- ngăn false maturity claims
- ngăn fake operationalization
- ngăn semantic drift giữa reviewability và runtime capability

### Acceptable shape
- regression locks
- wording discipline checks
- posture guard assertions
- bounded verification additions

### Must not become
- generic hardening program
- broad test overhaul
- unrelated QA expansion

### Exit condition
Feature chỉ pass nếu guard set:
- evidence-based
- bounded
- directly tied to v1.4 additions
- không mở broad quality program ngoài line objective

---

## 8. Feature ordering

Roadmap order đề xuất:

1. **F-301 — Operator Review Summary**
2. **F-302 — Handoff / Planning Surface Consolidation**
3. **F-303 — Reviewability Posture Guard**

### Logic của thứ tự này
- F-301 tạo review summary center
- F-302 làm coherent hơn các bounded surfaces liên quan
- F-303 khóa posture cuối line

Đây là order tự nhiên nhất cho một line reviewability-first.

---

## 9. Suggested pack discipline per feature

Mỗi feature trong `v1.4` nên đi theo kỷ luật 3-pack giống line trước:

### P1 — Gap capture / evidence
- test-first hoặc evidence-first
- chứng minh gap bounded thật sự tồn tại
- không đổi runtime behavior nếu chưa cần

### P2 — Bounded surface / contract implementation
- thêm surface nhỏ nhất cần thiết
- descriptive only
- reviewability only
- no capability inflation

### P3 — Posture / regression lock
- khóa wording
- khóa non-operational posture
- xác nhận smoke / canonical paths không drift

---

## 10. Explicit out-of-scope for the whole roadmap

Toàn bộ roadmap `v1.4` phải giữ **out-of-scope tuyệt đối**:

- orchestration
- scheduler
- automation
- daemon / background worker
- queue / polling / watcher
- provider abstraction
- connector registry
- backend / target runtime selection
- persistent history / registry / audit service
- real external integration
- real deployment execution
- installer / runtime engine
- platform-wide control plane
- broad repo-wide docs normalization
- speculative future architecture not grounded in repo truth

---

## 11. Fail-stop boundaries for roadmap execution design

Phải dừng roadmap execution design ngay nếu có bất kỳ dấu hiệu nào sau đây:

### 11.1 Scope inflation
- feature count tăng vượt small-line shape
- một feature không còn phục vụ reviewability objective
- optional theme D bắt đầu lấn thành core

### 11.2 Operational drift
- wording hoặc design khiến ATP bị hiểu nhầm là operational platform
- xuất hiện ideas kiểu dashboard/control/state engine
- summary surface bắt đầu giống control plane

### 11.3 Architecture drift
- xuất hiện provider layer
- xuất hiện registry/history/persistence
- xuất hiện background execution semantics
- xuất hiện integration/deployment execution semantics

### 11.4 Governance drift
- roadmap bị dùng như cớ để implementation sớm
- planning artifact bị dùng như feature approval mặc định
- objective bị broaden vượt khỏi `Operator Reviewability Consolidation`

---

## 12. Acceptance standard for the line

`v1.4` chỉ được coi là successful nếu line hoàn tất mà ATP vẫn giữ được:

- bounded posture
- reviewability-first posture
- planning/handoff orientation
- non-operational semantics
- carried-forward invariants nguyên trạng

và đồng thời đạt được:

- operator review clarity tốt hơn
- coherence tốt hơn giữa relevant surfaces
- posture consistency mạnh hơn
- semantic drift risk thấp hơn

---

## 13. Execution readiness statement

### Current roadmap state
`v1.4` hiện **đủ điều kiện để roadmap hóa** theo shape nhỏ đã khóa.

### Current implementation state
`v1.4` hiện **chưa được mở implementation** trong tài liệu này.

### What this roadmap authorizes
Roadmap này xác nhận execution-design set của `v1.4` hiện đã tồn tại ở mức planning:
- `docs/execution/v1_4/PROMPT_CMD/INDEX.md`
- feature-program files cho F-301 / F-302 / F-303

Roadmap này **không** tự authorize coding trực tiếp.
Next valid governance use của roadmap này là:
- review execution-design set hiện có
- dùng bộ `PROMPT_CMD` để viết bounded executor prompts chỉ khi có approval riêng ở bước sau

---

## 14. Recommended next governance use

Sau tài liệu này, next valid governance use là:

- review `docs/execution/v1_4/PROMPT_CMD/INDEX.md`
- review 3 feature-program files của F-301 / F-302 / F-303
- chỉ sau một approval riêng mới được dùng bộ này để soạn bounded executor prompts

Không có additional artifact bắt buộc nào phải được tạo thêm trong current v1.4 doc set chỉ để hoàn tất execution-design shape.

---

## 15. Kết luận cuối

### Final roadmap statement
`ATP v1.4` được roadmap hóa như một **small, bounded, governance-first, reviewability-focused line**.

### Locked feature line
- F-301 — Operator Review Summary
- F-302 — Handoff / Planning Surface Consolidation
- F-303 — Reviewability Posture Guard

### Final posture statement
`v1.4` chỉ hợp lệ nếu nó làm ATP:

- dễ review hơn
- coherent hơn
- rõ posture hơn

và không làm ATP:

- operational hơn
- autonomous hơn
- orchestration-ready hơn
- integration/deployment capable hơn
